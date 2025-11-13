#!/usr/bin/env python3
"""
Generate SQL to create employees with proper Django password hashes
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.contrib.auth.hashers import make_password

employees = [
    {
        'email': 'maria.gonzalez@claimit.org',
        'password': 'password123',
        'full_name': 'Maria Gonzalez',
        'role': 'senior_caseworker'
    },
    {
        'email': 'john.smith@claimit.org',
        'password': 'password123',
        'full_name': 'John Smith',
        'role': 'caseworker'
    },
    {
        'email': 'sarah.johnson@claimit.org',
        'password': 'password123',
        'full_name': 'Sarah Johnson',
        'role': 'caseworker'
    },
    {
        'email': 'admin@claimit.org',
        'password': 'password123',
        'full_name': 'Admin User',
        'role': 'admin'
    }
]

print("\n" + "="*80)
print("COPY THIS SQL AND RUN IT IN SUPABASE SQL EDITOR")
print("="*80 + "\n")

print("""-- Create employees table for caseworker authentication
CREATE TABLE IF NOT EXISTS employees (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    role VARCHAR(50) DEFAULT 'caseworker',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE
);

-- Enable Row Level Security for employees
ALTER TABLE employees ENABLE ROW LEVEL SECURITY;

-- Create policy for employees (allow all for now)
DROP POLICY IF EXISTS "Allow all access to employees" ON employees;
CREATE POLICY "Allow all access to employees" ON employees FOR ALL USING (true);

-- Clear existing employees (if any)
TRUNCATE TABLE employees;

-- Insert employees with Django password hashes
""")

for emp in employees:
    # Generate Django password hash
    password_hash = make_password(emp['password'])
    
    print(f"INSERT INTO employees (email, password_hash, full_name, role) VALUES")
    print(f"    ('{emp['email']}', '{password_hash}', '{emp['full_name']}', '{emp['role']}');")
    print()

print("\n" + "="*80)
print("✅ SQL Generated Successfully!")
print("="*80)
print("\n📋 Demo Credentials:")
print("   Email:    john.smith@claimit.org")
print("   Password: password123")
print("\n   (All accounts use password: password123)")
print()
