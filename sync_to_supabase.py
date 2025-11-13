"""
Sync SQLite data to Supabase
This will copy all your conversations, messages, and case submissions to Supabase
"""
import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from chatbot.models import Conversation, Message, CaseSubmission
from supabase import create_client, Client
from datetime import datetime

# Supabase credentials
SUPABASE_URL = os.getenv('SUPABASE_URL', "https://your-project-ref.supabase.co")
SUPABASE_KEY = os.getenv('SUPABASE_ANON_KEY', "your-anon-key-here")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

print("🔄 Starting sync from SQLite to Supabase...\n")

# Get all data from SQLite
conversations = Conversation.objects.all()
messages = Message.objects.all()
case_submissions = CaseSubmission.objects.all()

print(f"📊 Found in SQLite:")
print(f"   - {conversations.count()} conversations")
print(f"   - {messages.count()} messages")
print(f"   - {case_submissions.count()} case submissions\n")

# Sync Conversations
print("📤 Syncing conversations...")
for conv in conversations:
    data = {
        "id": str(conv.id),
        "created_at": conv.created_at.isoformat(),
        "updated_at": conv.updated_at.isoformat(),
        "is_complete": conv.is_complete,
    }
    try:
        supabase.table('conversations').upsert(data).execute()
        print(f"   ✅ Conversation {conv.id}")
    except Exception as e:
        print(f"   ❌ Error syncing conversation {conv.id}: {e}")

# Sync Messages
print("\n📤 Syncing messages...")
for msg in messages:
    data = {
        "id": str(msg.id),
        "conversation_id": str(msg.conversation.id),
        "role": msg.role,
        "content": msg.content,
        "created_at": msg.created_at.isoformat(),
    }
    try:
        supabase.table('messages').upsert(data).execute()
        print(f"   ✅ Message {msg.id}")
    except Exception as e:
        print(f"   ❌ Error syncing message {msg.id}: {e}")

# Sync Case Submissions
print("\n📤 Syncing case submissions...")
for case in case_submissions:
    data = {
        "id": str(case.id),
        "conversation_id": str(case.conversation.id),
        "submitted_at": case.submitted_at.isoformat(),
        "urgency_score": case.urgency_score,
        "urgency_reasoning": case.urgency_reasoning,
        "full_name": case.full_name,
        "date_of_birth": case.date_of_birth.isoformat() if case.date_of_birth else None,
        "age": case.age,
        "phone_number": case.phone_number,
        "email": case.email,
        "household_size": case.household_size,
        "household_members": case.household_members,
        "has_children": case.has_children,
        "monthly_income": case.monthly_income,
        "income_sources": case.income_sources,
        "total_assets": case.total_assets,
        "monthly_expenses": case.monthly_expenses,
        "employment_status": case.employment_status,
        "current_employer": case.current_employer,
        "job_title": case.job_title,
        "employment_duration": case.employment_duration,
        "housing_situation": case.housing_situation,
        "address": case.address,
        "monthly_rent": case.monthly_rent,
        "at_risk_of_homelessness": case.at_risk_of_homelessness,
        "has_disability": case.has_disability,
        "disability_details": case.disability_details,
        "has_medical_expenses": case.has_medical_expenses,
        "monthly_medical_costs": case.monthly_medical_costs,
        "has_health_insurance": case.has_health_insurance,
        "citizenship_status": case.citizenship_status,
        "immigration_status": case.immigration_status,
        "current_benefits": case.current_benefits,
        "has_emergency_needs": case.has_emergency_needs,
        "emergency_details": case.emergency_details,
        "structured_summary": case.structured_summary,
        "ai_summary": case.ai_summary,
        "recommended_programs": case.recommended_programs,
        "recommended_actions": case.recommended_actions,
        "additional_data": case.additional_data,
    }
    try:
        supabase.table('case_submissions').upsert(data).execute()
        print(f"   ✅ Case {case.id} - {case.full_name} (Urgency: {case.urgency_score}/10)")
    except Exception as e:
        print(f"   ❌ Error syncing case {case.id}: {e}")

print("\n" + "="*60)
print("✅ SYNC COMPLETE!")
print("="*60)
print(f"\n🌐 View your data in Supabase:")
print(f"   📊 Table Editor: https://supabase.com/dashboard/project/uwqxplllohfdevxvsyii/editor")
print(f"   📋 Conversations: https://supabase.com/dashboard/project/uwqxplllohfdevxvsyii/editor/public/conversations")
print(f"   💬 Messages: https://supabase.com/dashboard/project/uwqxplllohfdevxvsyii/editor/public/messages")
print(f"   📁 Case Submissions: https://supabase.com/dashboard/project/uwqxplllohfdevxvsyii/editor/public/case_submissions")
print("\n")
