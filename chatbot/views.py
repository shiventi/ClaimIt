import sys
import os
import json
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'app', 'Backend'))

from typing import Dict, Any
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.http import HttpResponse, JsonResponse
from .models import Conversation, Message, CaseSubmission
from .serializers import ConversationSerializer, MessageSerializer
from datetime import datetime

# Import Supabase sync utilities
from .supabase_sync import (
    sync_conversation_to_supabase,
    sync_message_to_supabase,
    sync_case_submission_to_supabase,
    bulk_sync_conversation_with_messages,
    get_supabase_client,
)

# Import the Watson Intake Assistant
try:
    from app.Backend.watson_intake import WatsonIntakeAssistant
except ImportError:
    print("⚠️ Failed to import WatsonIntakeAssistant")
    WatsonIntakeAssistant = None

# Create a single shared Watson instance to maintain conversation state
_watson_instance = None

def get_watson_instance():
    global _watson_instance
    if _watson_instance is None and WatsonIntakeAssistant:
        try:
            _watson_instance = WatsonIntakeAssistant()
            print("✅ Watson Intake Assistant initialized")
        except Exception as e:
            print(f"❌ Failed to initialize Watson: {e}")
            _watson_instance = None
    return _watson_instance




class ConversationViewSet(viewsets.ModelViewSet):
    """
    Handles comprehensive intake conversations and case submissions.
    Focuses on gathering data for caseworkers.
    """
    queryset = Conversation.objects.all()
    serializer_class = ConversationSerializer
    
    @property
    def watson(self):
        """Get the shared Watson instance"""
        return get_watson_instance()
    
    def create(self, request, *args, **kwargs):
        """Override create to sync new conversations to Supabase"""
        response = super().create(request, *args, **kwargs)
        
        # Sync newly created conversation to Supabase
        if response.status_code == 201:
            try:
                conversation_id = response.data.get('id')
                conversation = Conversation.objects.get(id=conversation_id)
                sync_conversation_to_supabase(conversation)
            except Exception as e:
                print(f"⚠️ Failed to sync new conversation: {e}")
        
        return response
    
    @action(detail=True, methods=['post'])
    def send_message(self, request, pk=None):
        """
        Send a message in a conversation and continue intake process.
        Returns AI response + current progress.
        Automatically syncs to Supabase at key points.
        """
        conversation = self.get_object()
        user_message = request.data.get('message', '')
        
        if not user_message:
            return Response(
                {'error': 'Message is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Save user message
        user_msg = Message.objects.create(
            conversation=conversation,
            role='user',
            content=user_message
        )
        
        # OPTIMIZATION: Only sync user messages (not every message to reduce API calls)
        # Assistant messages will be synced when conversation is complete
        sync_message_to_supabase(user_msg)
        
        # Get Watson response
        if self.watson:
            try:
                result = self.watson.send_message(str(conversation.id), user_message)
                
                assistant_message = result.get('watson_response', 'I understand.')
                extracted_data = result.get('extracted_data', {})
                is_complete = result.get('is_complete', False)
                questions_asked = result.get('questions_asked', 0)
                
                # Update conversation status
                conversation.is_complete = is_complete
                conversation.save()
                
                # Sync conversation status update
                sync_conversation_to_supabase(conversation)
                
                # If complete, generate case submission
                if is_complete:
                    # Check if submission already exists
                    if not hasattr(conversation, 'case_submission'):
                        self._create_case_submission(conversation, result)
                        
                        # CRITICAL: Sync complete conversation with all data to Supabase
                        print("🔄 Conversation complete - syncing all data to Supabase...")
                        bulk_sync_conversation_with_messages(conversation)
                
            except Exception as e:
                print(f"❌ Watson error: {e}")
                import traceback
                traceback.print_exc()
                assistant_message = "I'm having trouble processing that. Could you please try again?"
                is_complete = False
                questions_asked = 0
        else:
            assistant_message = "Watson assistant is not available. Please check configuration."
            is_complete = False
            questions_asked = 0
        
        # Save assistant message
        assistant_msg = Message.objects.create(
            conversation=conversation,
            role='assistant',
            content=assistant_message
        )
        
        # Sync assistant message too
        sync_message_to_supabase(assistant_msg)
        
        # Return response with progress info
        serializer = self.get_serializer(conversation)
        response_data = serializer.data
        response_data['is_complete'] = is_complete
        response_data['questions_asked'] = questions_asked
        response_data['latest_message'] = assistant_message
        
        return Response(response_data)
    
    def _create_case_submission(self, conversation: Conversation, watson_result: Dict) -> CaseSubmission:
        """
        Create a case submission from completed intake conversation.
        Generates summary, urgency score, and recommendations.
        """
        print(f"📝 Creating case submission for conversation {conversation.id}")
        
        # Generate comprehensive summary
        summary_data = self.watson.generate_case_summary(str(conversation.id))
        
        extracted_data = summary_data.get('extracted_data', {})
        personal = extracted_data.get('personal', {})
        household = extracted_data.get('household', {})
        employment = extracted_data.get('employment', {})
        financial = extracted_data.get('financial', {})
        housing = extracted_data.get('housing', {})
        health = extracted_data.get('health', {})
        legal = extracted_data.get('legal', {})
        current_benefits = extracted_data.get('current_benefits', {})
        emergency = extracted_data.get('emergency', {})

        def safe_str(value: Any) -> str:
            """Normalize optional string values so we never insert NULLs."""
            if value is None:
                return ''
            if isinstance(value, str):
                cleaned = value.strip()
                return '' if cleaned.lower() == 'null' else cleaned
            return str(value)

        def safe_list(value: Any) -> list:
            if isinstance(value, list):
                return value
            if isinstance(value, str):
                cleaned = value.strip()
                if cleaned.lower() in ('', 'null', 'none'):
                    return []
                try:
                    parsed = json.loads(cleaned)
                    if isinstance(parsed, list):
                        return parsed
                    if parsed in (None, '', 'null'):
                        return []
                    return [parsed]
                except json.JSONDecodeError:
                    return [cleaned]
            return [] if value in (None, '', 'null') else [value]

        def safe_dict(value: Any) -> dict:
            if isinstance(value, dict):
                return value
            if isinstance(value, str):
                cleaned = value.strip()
                if cleaned.lower() in ('', 'null', 'none'):
                    return {}
                try:
                    parsed = json.loads(cleaned)
                    return parsed if isinstance(parsed, dict) else {}
                except json.JSONDecodeError:
                    return {}
            return {}
        
        # Parse date of birth if available
        dob = None
        dob_str = personal.get('date_of_birth')
        if dob_str and dob_str != 'null':
            try:
                dob = datetime.strptime(dob_str, '%Y-%m-%d').date()
            except:
                pass
        
        # Create case submission
        full_name = safe_str(personal.get('full_name'))
        if not full_name:
            full_name = safe_str(personal.get('first_name'))

        case = CaseSubmission.objects.create(
            conversation=conversation,
            urgency_score=summary_data.get('urgency_score', 5),
            urgency_reasoning=safe_str(summary_data.get('urgency_reasoning', '')),
            
            # Personal info
            full_name=full_name,
            date_of_birth=dob,
            age=personal.get('age'),
            phone_number=safe_str(personal.get('phone', '')),
            email=safe_str(personal.get('email', '')),
            
            # Household
            household_size=household.get('size'),
            household_members=safe_list(household.get('members', [])),
            has_children=household.get('has_children'),
            
            # Financial
            monthly_income=financial.get('monthly_income'),
            income_sources=safe_list(financial.get('income_sources', [])),
            total_assets=financial.get('total_assets'),
            monthly_expenses=safe_dict(financial.get('monthly_expenses', {})),
            monthly_rent=financial.get('monthly_rent'),
            
            # Employment
            employment_status=safe_str(employment.get('status', '')),
            current_employer=safe_str(employment.get('employer', '')),
            job_title=safe_str(employment.get('job_title', '')),
            employment_duration=safe_str(employment.get('duration', '')),
            
            # Housing
            housing_situation=safe_str(housing.get('status', '')),
            address=safe_str(housing.get('address', '')),
            at_risk_of_homelessness=bool(housing.get('at_risk_of_homelessness', False)),
            
            # Health
            has_disability=health.get('has_disability'),
            disability_details=safe_str(health.get('disability_details', '')),
            has_medical_expenses=health.get('has_medical_expenses'),
            monthly_medical_costs=health.get('monthly_medical_costs'),
            has_health_insurance=health.get('has_insurance'),
            
            # Legal
            citizenship_status=safe_str(legal.get('citizenship_status', '')),
            immigration_status=safe_str(legal.get('immigration_status', '')),
            
            # Current benefits
            current_benefits=safe_list(current_benefits.get('programs', [])),
            
            # Emergency
            has_emergency_needs=bool(emergency.get('has_urgent_needs', False)),
            emergency_details=safe_str(emergency.get('details', '')),
            
            # AI-generated content
            structured_summary=safe_dict(extracted_data),
            ai_summary=safe_str(summary_data.get('ai_summary', '')),
            recommended_programs=safe_list(summary_data.get('recommended_programs', [])),
            recommended_actions=safe_str(summary_data.get('recommended_actions', '')),
        )
        
        print(f"✅ Case submission created: {case.id} (Urgency: {case.urgency_score}/10)")
        return case
    
    @action(detail=True, methods=['get'])
    def case_summary(self, request, pk=None):
        """
        Get the complete case summary for a completed conversation.
        This is what the caseworker will see.
        """
        conversation = self.get_object()
        
        if not conversation.is_complete:
            return Response(
                {'error': 'Conversation not yet complete'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get or create case submission
        try:
            case = conversation.case_submission
        except CaseSubmission.DoesNotExist:
            return Response(
                {'error': 'Case submission not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Build comprehensive response
        summary = {
            'case_id': str(case.id),
            'submitted_at': case.submitted_at.isoformat(),
            'urgency_score': case.urgency_score,
            'urgency_reasoning': case.urgency_reasoning,
            
            # Structured sections for caseworker
            'personal_info': {
                'name': case.full_name,
                'age': case.age,
                'date_of_birth': case.date_of_birth.isoformat() if case.date_of_birth else None,
                'phone': case.phone_number,
                'email': case.email,
            },
            
            'household_info': {
                'size': case.household_size,
                'has_children': case.has_children,
                'members': case.household_members,
            },
            
            'financial_info': {
                'monthly_income': case.monthly_income,
                'income_sources': case.income_sources,
                'total_assets': case.total_assets,
                'monthly_rent': case.monthly_rent,
                'monthly_expenses': case.monthly_expenses,
            },
            
            'employment_info': {
                'status': case.employment_status,
                'employer': case.current_employer,
                'job_title': case.job_title,
                'duration': case.employment_duration,
            },
            
            'housing_info': {
                'situation': case.housing_situation,
                'address': case.address,
                'at_risk': case.at_risk_of_homelessness,
            },
            
            'health_info': {
                'has_disability': case.has_disability,
                'disability_details': case.disability_details,
                'has_insurance': case.has_health_insurance,
                'monthly_medical_costs': case.monthly_medical_costs,
            },
            
            'legal_info': {
                'citizenship_status': case.citizenship_status,
                'immigration_status': case.immigration_status,
            },
            
            'current_benefits': case.current_benefits,
            
            'emergency_info': {
                'has_urgent_needs': case.has_emergency_needs,
                'details': case.emergency_details,
            },
            
            # AI-generated insights
            'ai_summary': case.ai_summary,
            'recommended_programs': case.recommended_programs,
            'recommended_actions': case.recommended_actions,
            
            # Full conversation transcript
            'conversation_transcript': [
                {
                    'role': msg.role,
                    'content': msg.content,
                    'timestamp': msg.created_at.isoformat()
                }
                for msg in conversation.messages.all()
            ],
        }
        
        return Response(summary)
    
    @action(detail=False, methods=['get'])
    def all_cases(self, request):
        """
        Get all submitted cases for caseworker dashboard.
        Sorted by urgency score (highest first), then date.
        """
        cases = CaseSubmission.objects.all().order_by('-urgency_score', '-submitted_at')
        
        cases_list = []
        for case in cases:
            cases_list.append({
                'case_id': str(case.id),
                'conversation_id': str(case.conversation.id),
                'submitted_at': case.submitted_at.isoformat(),
                'urgency_score': case.urgency_score,
                'urgency_reasoning': case.urgency_reasoning,
                'name': case.full_name,
                'age': case.age,
                'phone': case.phone_number,
                'email': case.email,
                'recommended_programs': case.recommended_programs,
                'has_emergency': case.has_emergency_needs,
            })
        
        
        return Response({
            'total_cases': len(cases_list),
            'cases': cases_list
        })


# Dashboard API Views for Caseworkers

from rest_framework.decorators import api_view
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.hashers import make_password, check_password


@api_view(['GET'])
def healthz(request):
    """
    Simple health check endpoint for uptime monitors (Render, UptimeRobot, etc.)
    Returns 200 OK when the Django app is responsive.
    """
    return Response({'status': 'ok'})


@api_view(['POST'])
@csrf_exempt
def employee_login(request):
    """
    Authenticate an employee using Supabase
    """
    email = request.data.get('email', '').strip()
    password = request.data.get('password', '')
    
    if not email or not password:
        return Response(
            {'error': 'Email and password are required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    supabase = get_supabase_client()
    if not supabase:
        return Response(
            {'error': 'Database connection unavailable'},
            status=status.HTTP_503_SERVICE_UNAVAILABLE
        )
    
    try:
        # Query employee from Supabase
        result = supabase.table('employees').select('*').eq('email', email).eq('is_active', True).execute()
        
        if not result.data or len(result.data) == 0:
            return Response(
                {'error': 'Invalid email or password'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        employee = result.data[0]
        
        # Verify password using Django's password hasher
        password_hash = employee['password_hash']
        if check_password(password, password_hash):
            # Return employee data (without password)
            return Response({
                'id': employee['id'],
                'email': employee['email'],
                'full_name': employee['full_name'],
                'role': employee['role'],
            })
        else:
            return Response(
                {'error': 'Invalid email or password'},
                status=status.HTTP_401_UNAUTHORIZED
            )
    except Exception as e:
        print(f"❌ Login error: {e}")
        import traceback
        traceback.print_exc()
        return Response(
            {'error': 'Authentication failed'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
def dashboard_cases(request):
    """
    Get all cases from Supabase for dashboard
    Supports filtering and sorting
    """
    supabase = get_supabase_client()
    if not supabase:
        return Response(
            {'error': 'Database connection unavailable'},
            status=status.HTTP_503_SERVICE_UNAVAILABLE
        )
    
    try:
        # Get query parameters
        sort_by = request.GET.get('sort_by', 'urgency_score')
        order = request.GET.get('order', 'desc')
        search = request.GET.get('search', '').strip()
        
        # Build query
        query = supabase.table('case_submissions').select('*')
        
        # Apply search filter if provided
        if search:
            query = query.or_(f'full_name.ilike.%{search}%,email.ilike.%{search}%')
        
        # Apply sorting
        ascending = (order == 'asc')
        query = query.order(sort_by, desc=not ascending)
        
        result = query.execute()
        
        return Response({
            'total_cases': len(result.data),
            'cases': result.data
        })
    except Exception as e:
        print(f"❌ Dashboard cases error: {e}")
        return Response(
            {'error': 'Failed to fetch cases'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
def dashboard_case_detail(request, case_id):
    """
    Get detailed case information including conversation history
    """
    supabase = get_supabase_client()
    if not supabase:
        return Response(
            {'error': 'Database connection unavailable'},
            status=status.HTTP_503_SERVICE_UNAVAILABLE
        )
    
    try:
        # Get case submission
        case_result = supabase.table('case_submissions').select('*').eq('id', case_id).execute()
        
        if not case_result.data:
            return Response(
                {'error': 'Case not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        case = case_result.data[0]
        conversation_id = case['conversation_id']
        
        # Get conversation
        conv_result = supabase.table('conversations').select('*').eq('id', conversation_id).execute()
        
        # Get messages
        messages_result = supabase.table('messages').select('*').eq('conversation_id', conversation_id).order('created_at').execute()
        
        return Response({
            'case': case,
            'conversation': conv_result.data[0] if conv_result.data else None,
            'messages': messages_result.data
        })
    except Exception as e:
        print(f"❌ Case detail error: {e}")
        return Response(
            {'error': 'Failed to fetch case details'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
def dashboard_conversations(request):
    """
    Get all conversations from Supabase for dashboard
    """
    supabase = get_supabase_client()
    if not supabase:
        return Response(
            {'error': 'Database connection unavailable'},
            status=status.HTTP_503_SERVICE_UNAVAILABLE
        )
    
    try:
        # Get query parameters
        is_complete = request.GET.get('is_complete', None)
        
        # Build query
        query = supabase.table('conversations').select('*')
        
        # Filter by completion status if specified
        if is_complete is not None:
            is_complete_bool = is_complete.lower() == 'true'
            query = query.eq('is_complete', is_complete_bool)
        
        # Sort by most recent first
        query = query.order('created_at', desc=True)
        
        result = query.execute()
        
        return Response({
            'total_conversations': len(result.data) if result.data else 0,
            'conversations': result.data or []
        })
    except Exception as e:
        print(f"❌ Dashboard conversations error: {e}")
        import traceback
        traceback.print_exc()
        return Response(
            {'error': 'Failed to fetch conversations'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
def dashboard_conversation_detail(request, conversation_id):
    """
    Get a specific conversation with its messages
    """
    supabase = get_supabase_client()
    if not supabase:
        return Response(
            {'error': 'Database connection unavailable'},
            status=status.HTTP_503_SERVICE_UNAVAILABLE
        )
    
    try:
        # Get conversation
        conv_result = supabase.table('conversations').select('*').eq('id', conversation_id).execute()
        
        if not conv_result.data or len(conv_result.data) == 0:
            return Response(
                {'error': 'Conversation not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        conversation = conv_result.data[0]
        
        # Get messages for this conversation
        messages_result = supabase.table('messages').select('*').eq('conversation_id', conversation_id).order('created_at', desc=False).execute()
        
        conversation['messages'] = messages_result.data or []
        
        return Response(conversation)
    except Exception as e:
        print(f"❌ Dashboard conversation detail error: {e}")
        import traceback
        traceback.print_exc()
        return Response(
            {'error': 'Failed to fetch conversation details'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
def dashboard_conversation_case(request, conversation_id):
    """
    Get case submission for a conversation (if it exists)
    """
    supabase = get_supabase_client()
    if not supabase:
        return Response(
            {'error': 'Database connection unavailable'},
            status=status.HTTP_503_SERVICE_UNAVAILABLE
        )
    
    try:
        # Get case submission for this conversation
        case_result = supabase.table('case_submissions').select('*').eq('conversation_id', conversation_id).execute()
        
        if not case_result.data or len(case_result.data) == 0:
            return Response(
                {'error': 'No case submission found for this conversation'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        return Response(case_result.data[0])
    except Exception as e:
        print(f"❌ Dashboard conversation case error: {e}")
        return Response(
            {'error': 'Failed to fetch case submission'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
def dashboard_stats(request):
    """
    Get dashboard statistics
    """
    supabase = get_supabase_client()
    if not supabase:
        return Response(
            {'error': 'Database connection unavailable'},
            status=status.HTTP_503_SERVICE_UNAVAILABLE
        )
    
    try:
        # Total conversations
        total_convs = supabase.table('conversations').select('id', count='exact').execute()
        
        # Completed conversations
        completed_convs = supabase.table('conversations').select('id', count='exact').eq('is_complete', True).execute()
        
        # Total cases
        total_cases = supabase.table('case_submissions').select('id', count='exact').execute()
        
        # High urgency cases (score >= 8)
        high_urgency = supabase.table('case_submissions').select('id', count='exact').gte('urgency_score', 8).execute()
        
        # Emergency cases
        emergency_cases = supabase.table('case_submissions').select('id', count='exact').eq('has_emergency_needs', True).execute()
        
        return Response({
            'total_conversations': len(total_convs.data) if total_convs.data else 0,
            'completed_conversations': len(completed_convs.data) if completed_convs.data else 0,
            'total_cases': len(total_cases.data) if total_cases.data else 0,
            'high_urgency_cases': len(high_urgency.data) if high_urgency.data else 0,
            'emergency_cases': len(emergency_cases.data) if emergency_cases.data else 0,
        })
    except Exception as e:
        print(f"❌ Dashboard stats error: {e}")
        return Response(
            {'error': 'Failed to fetch statistics'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
