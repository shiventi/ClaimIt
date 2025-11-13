"""
Setup Supabase tables
"""
import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("❌ ERROR: SUPABASE_URL and SUPABASE_ANON_KEY must be set in .env file")
    exit(1)

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

print("🔌 Connected to Supabase!")
print(f"📍 Project URL: {SUPABASE_URL}")

# Create tables using SQL via Supabase SQL Editor
# You need to run this SQL in Supabase Dashboard → SQL Editor:

sql_schema = """
-- ClaimIt Database Schema for Supabase

-- Conversations table
CREATE TABLE IF NOT EXISTS conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    is_complete BOOLEAN DEFAULT FALSE
);

-- Messages table
CREATE TABLE IF NOT EXISTS messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID REFERENCES conversations(id) ON DELETE CASCADE,
    role VARCHAR(10) NOT NULL CHECK (role IN ('user', 'assistant')),
    content TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Case Submissions table
CREATE TABLE IF NOT EXISTS case_submissions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID UNIQUE REFERENCES conversations(id) ON DELETE CASCADE,
    submitted_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Urgency
    urgency_score INTEGER DEFAULT 5,
    urgency_reasoning TEXT,
    
    -- Personal Information
    full_name VARCHAR(255),
    date_of_birth DATE,
    age INTEGER,
    phone_number VARCHAR(20),
    email VARCHAR(254),
    
    -- Household
    household_size INTEGER,
    household_members JSONB DEFAULT '[]'::jsonb,
    has_children BOOLEAN,
    
    -- Financial
    monthly_income FLOAT,
    income_sources JSONB DEFAULT '[]'::jsonb,
    total_assets FLOAT,
    monthly_expenses JSONB DEFAULT '{}'::jsonb,
    
    -- Employment
    employment_status VARCHAR(50),
    current_employer VARCHAR(255),
    job_title VARCHAR(255),
    employment_duration VARCHAR(100),
    
    -- Housing
    housing_situation VARCHAR(100),
    address TEXT,
    monthly_rent FLOAT,
    at_risk_of_homelessness BOOLEAN DEFAULT FALSE,
    
    -- Health
    has_disability BOOLEAN,
    disability_details TEXT,
    has_medical_expenses BOOLEAN,
    monthly_medical_costs FLOAT,
    has_health_insurance BOOLEAN,
    
    -- Legal
    citizenship_status VARCHAR(100),
    immigration_status VARCHAR(100),
    
    -- Benefits
    current_benefits JSONB DEFAULT '[]'::jsonb,
    
    -- Emergency
    has_emergency_needs BOOLEAN DEFAULT FALSE,
    emergency_details TEXT,
    
    -- AI Generated
    structured_summary JSONB DEFAULT '{}'::jsonb,
    ai_summary TEXT,
    recommended_programs JSONB DEFAULT '[]'::jsonb,
    recommended_actions TEXT,
    
    -- Additional
    additional_data JSONB DEFAULT '{}'::jsonb
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_case_urgency ON case_submissions(urgency_score DESC, submitted_at DESC);
CREATE INDEX IF NOT EXISTS idx_case_submitted ON case_submissions(submitted_at DESC);
CREATE INDEX IF NOT EXISTS idx_messages_conversation ON messages(conversation_id, created_at);

-- Employees table for caseworker authentication
CREATE TABLE IF NOT EXISTS employees (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    role VARCHAR(50) DEFAULT 'caseworker',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE
);

-- Insert demo employees (passwords are hashed with bcrypt - password is 'password123')
-- You can use https://bcrypt-generator.com/ to generate more hashes
INSERT INTO employees (email, password_hash, full_name, role) VALUES
    ('maria.gonzalez@claimit.org', '$2a$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYIVKmWU3GW', 'Maria Gonzalez', 'senior_caseworker'),
    ('john.smith@claimit.org', '$2a$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYIVKmWU3GW', 'John Smith', 'caseworker'),
    ('sarah.johnson@claimit.org', '$2a$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYIVKmWU3GW', 'Sarah Johnson', 'caseworker'),
    ('admin@claimit.org', '$2a$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYIVKmWU3GW', 'Admin User', 'admin')
ON CONFLICT (email) DO NOTHING;

-- Enable Row Level Security (RLS)
ALTER TABLE conversations ENABLE ROW LEVEL SECURITY;
ALTER TABLE messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE case_submissions ENABLE ROW LEVEL SECURITY;
ALTER TABLE employees ENABLE ROW LEVEL SECURITY;

-- Create policies (allow all for now - adjust for production)
CREATE POLICY "Allow all access to conversations" ON conversations FOR ALL USING (true);
CREATE POLICY "Allow all access to messages" ON messages FOR ALL USING (true);
CREATE POLICY "Allow all access to case_submissions" ON case_submissions FOR ALL USING (true);
CREATE POLICY "Allow all access to employees" ON employees FOR ALL USING (true);
"""

print("\n" + "="*60)
print("📋 COPY THIS SQL AND RUN IT IN SUPABASE:")
print("="*60)
print("\n1. Go to: https://supabase.com/dashboard/project/uwqxplllohfdevxvsyii/sql/new")
print("2. Paste the SQL below")
print("3. Click 'RUN'\n")
print("="*60)
print(sql_schema)
print("="*60)

# Test connection by trying to read from a table
try:
    response = supabase.table('conversations').select("*").limit(1).execute()
    print("\n✅ Successfully connected to Supabase!")
    print(f"📊 Found {len(response.data)} conversations")
except Exception as e:
    print(f"\n⚠️ Tables not created yet. Run the SQL above first!")
    print(f"Error: {e}")
