"""
Supabase sync utilities
"""
import os
from typing import Dict, Any, Optional
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL", "https://uwqxplllohfdevxvsyii.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY")

if not SUPABASE_KEY:
    print("⚠️ WARNING: SUPABASE_ANON_KEY not found in environment variables")

def get_supabase_client() -> Optional[Client]:
    """
    Get a fresh Supabase client
    """
    if not SUPABASE_KEY:
        print("⚠️ Supabase not available: Missing SUPABASE_ANON_KEY")
        print(f"   SUPABASE_URL present: {bool(SUPABASE_URL)}")
        return None
        
    try:
        client = create_client(SUPABASE_URL, SUPABASE_KEY)
        print(f"✅ Supabase client created successfully (URL: {SUPABASE_URL[:30]}...)")
        return client
    except Exception as e:
        import traceback
        print(f"⚠️ Supabase client creation failed: {e}")
        print(f"   SUPABASE_URL: {SUPABASE_URL}")
        print(f"   Traceback: {traceback.format_exc()}")
        return None


def sync_conversation_to_supabase(conversation) -> bool:
    """
    Sync a conversation to Supabase
    Returns True if successful, False otherwise
    """
    supabase = get_supabase_client()
    if not supabase:
        print(f"⚠️ Supabase client not available - cannot sync conversation {conversation.id}")
        return False
    
    try:
        data = {
            "id": str(conversation.id),
            "created_at": conversation.created_at.isoformat(),
            "updated_at": conversation.updated_at.isoformat(),
            "is_complete": conversation.is_complete,
        }
        
        # Upsert (insert or update)
        result = supabase.table("conversations").upsert(data).execute()
        print(f"📤 Synced conversation {conversation.id} to Supabase (status: {result.data is not None})")
        return True
    except Exception as e:
        import traceback
        print(f"⚠️ Failed to sync conversation {conversation.id}: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        return False


def sync_message_to_supabase(message) -> bool:
    """
    Sync a message to Supabase
    Returns True if successful, False otherwise
    """
    supabase = get_supabase_client()
    if not supabase:
        print(f"⚠️ Supabase client not available - cannot sync message {message.id}")
        return False
    
    try:
        data = {
            "id": str(message.id),
            "conversation_id": str(message.conversation_id),
            "role": message.role,
            "content": message.content,
            "created_at": message.created_at.isoformat(),
        }
        
        result = supabase.table("messages").upsert(data).execute()
        print(f"📤 Synced message {message.id} to Supabase (status: {result.data is not None})")
        return True
    except Exception as e:
        import traceback
        print(f"⚠️ Failed to sync message {message.id}: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        return False


def sync_case_submission_to_supabase(case_submission) -> bool:
    """
    Sync a case submission to Supabase
    This is the most important data to sync
    Returns True if successful, False otherwise
    """
    supabase = get_supabase_client()
    if not supabase:
        return False
    
    try:
        data = {
            "id": str(case_submission.id),
            "conversation_id": str(case_submission.conversation_id),
            "submitted_at": case_submission.submitted_at.isoformat(),
            
            # Urgency
            "urgency_score": case_submission.urgency_score,
            "urgency_reasoning": case_submission.urgency_reasoning,
            
            # Personal
            "full_name": case_submission.full_name,
            "date_of_birth": case_submission.date_of_birth.isoformat() if case_submission.date_of_birth else None,
            "age": case_submission.age,
            "phone_number": case_submission.phone_number,
            "email": case_submission.email,
            
            # Household
            "household_size": case_submission.household_size,
            "household_members": case_submission.household_members,
            "has_children": case_submission.has_children,
            
            # Financial
            "monthly_income": case_submission.monthly_income,
            "income_sources": case_submission.income_sources,
            "total_assets": case_submission.total_assets,
            "monthly_expenses": case_submission.monthly_expenses,
            "monthly_rent": case_submission.monthly_rent,
            
            # Employment
            "employment_status": case_submission.employment_status,
            "current_employer": case_submission.current_employer,
            "job_title": case_submission.job_title,
            "employment_duration": case_submission.employment_duration,
            
            # Housing
            "housing_situation": case_submission.housing_situation,
            "address": case_submission.address,
            "at_risk_of_homelessness": case_submission.at_risk_of_homelessness,
            
            # Health
            "has_disability": case_submission.has_disability,
            "disability_details": case_submission.disability_details,
            "has_medical_expenses": case_submission.has_medical_expenses,
            "monthly_medical_costs": case_submission.monthly_medical_costs,
            "has_health_insurance": case_submission.has_health_insurance,
            
            # Legal
            "citizenship_status": case_submission.citizenship_status,
            "immigration_status": case_submission.immigration_status,
            
            # Benefits
            "current_benefits": case_submission.current_benefits,
            
            # Emergency
            "has_emergency_needs": case_submission.has_emergency_needs,
            "emergency_details": case_submission.emergency_details,
            
            # AI Generated
            "structured_summary": case_submission.structured_summary,
            "ai_summary": case_submission.ai_summary,
            "recommended_programs": case_submission.recommended_programs,
            "recommended_actions": case_submission.recommended_actions,
            
            # Additional
            "additional_data": case_submission.additional_data,
        }
        
        supabase.table("case_submissions").upsert(data).execute()
        print(f"📤 Synced case submission {case_submission.id} to Supabase")
        return True
    except Exception as e:
        print(f"⚠️ Failed to sync case submission: {e}")
        return False


def bulk_sync_conversation_with_messages(conversation) -> bool:
    """
    Efficiently sync a conversation with all its messages
    Used when conversation is completed
    """
    supabase = get_supabase_client()
    if not supabase:
        return False
    
    try:
        # Sync conversation first
        sync_conversation_to_supabase(conversation)
        
        # Sync all messages in bulk
        messages = conversation.messages.all()
        for message in messages:
            sync_message_to_supabase(message)
        
        # Sync case submission if exists
        if hasattr(conversation, 'case_submission'):
            sync_case_submission_to_supabase(conversation.case_submission)
        
        print(f"✅ Fully synced conversation {conversation.id} with {len(messages)} messages")
        return True
    except Exception as e:
        import traceback
        print(f"⚠️ Failed to bulk sync: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        return False


def test_supabase_connection() -> bool:
    """
    Test Supabase connection at startup
    Returns True if connection is working, False otherwise
    """
    print("🔌 Testing Supabase connection...")
    supabase = get_supabase_client()
    if not supabase:
        print("❌ Supabase connection test FAILED: Could not create client")
        return False
    
    try:
        # Try a simple query
        result = supabase.table("conversations").select("id").limit(1).execute()
        print(f"✅ Supabase connection test PASSED (found {len(result.data)} conversations)")
        return True
    except Exception as e:
        import traceback
        print(f"❌ Supabase connection test FAILED: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        return False
