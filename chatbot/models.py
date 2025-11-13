from django.db import models
import uuid
import json

class Conversation(models.Model):
    """Stores ongoing chat conversation and basic metadata"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_complete = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Conversation {self.id}"


class CaseSubmission(models.Model):
    """Complete intake case submitted to caseworker - structured for Supabase migration"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    conversation = models.OneToOneField(Conversation, on_delete=models.CASCADE, related_name='case_submission')
    submitted_at = models.DateTimeField(auto_now_add=True)
    
    # Urgency Assessment (1-10 scale)
    urgency_score = models.IntegerField(default=5)
    urgency_reasoning = models.TextField(blank=True)
    
    # Personal Information
    full_name = models.CharField(max_length=255, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    age = models.IntegerField(null=True, blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    
    # Household Information (stored as JSON for flexibility)
    household_size = models.IntegerField(null=True, blank=True)
    household_members = models.JSONField(default=list, blank=True)  # [{"name": "...", "age": ..., "relationship": "..."}]
    has_children = models.BooleanField(null=True, blank=True)
    
    # Financial Information
    monthly_income = models.FloatField(null=True, blank=True)
    income_sources = models.JSONField(default=list, blank=True)  # ["employment", "unemployment", "SSI", etc.]
    total_assets = models.FloatField(null=True, blank=True)
    monthly_expenses = models.JSONField(default=dict, blank=True)  # {"rent": 1200, "utilities": 150, etc.}
    
    # Employment History
    employment_status = models.CharField(max_length=50, blank=True)  # "employed", "unemployed", "self-employed", etc.
    current_employer = models.CharField(max_length=255, blank=True)
    job_title = models.CharField(max_length=255, blank=True)
    employment_duration = models.CharField(max_length=100, blank=True)
    
    # Housing Status
    housing_situation = models.CharField(max_length=100, blank=True)  # "rent", "own", "homeless", "temporary", etc.
    address = models.TextField(blank=True)
    monthly_rent = models.FloatField(null=True, blank=True)
    at_risk_of_homelessness = models.BooleanField(default=False)
    
    # Health Information
    has_disability = models.BooleanField(null=True, blank=True)
    disability_details = models.TextField(blank=True)
    has_medical_expenses = models.BooleanField(null=True, blank=True)
    monthly_medical_costs = models.FloatField(null=True, blank=True)
    has_health_insurance = models.BooleanField(null=True, blank=True)
    
    # Legal/Immigration Status
    citizenship_status = models.CharField(max_length=100, blank=True)
    immigration_status = models.CharField(max_length=100, blank=True)
    
    # Current Benefits
    current_benefits = models.JSONField(default=list, blank=True)  # ["SNAP", "Medi-Cal", etc.]
    
    # Emergency/Urgent Needs
    has_emergency_needs = models.BooleanField(default=False)
    emergency_details = models.TextField(blank=True)
    
    # AI-Generated Summary and Recommendations
    structured_summary = models.JSONField(default=dict, blank=True)  # Full structured summary
    ai_summary = models.TextField(blank=True)  # Human-readable summary from AI
    recommended_programs = models.JSONField(default=list, blank=True)  # ["SNAP", "Medi-Cal", etc.]
    recommended_actions = models.TextField(blank=True)  # Next steps for caseworker
    
    # Additional flexible data storage
    additional_data = models.JSONField(default=dict, blank=True)
    
    class Meta:
        ordering = ['-submitted_at']
        indexes = [
            models.Index(fields=['-urgency_score', '-submitted_at']),
            models.Index(fields=['submitted_at']),
        ]
    
    def __str__(self):
        return f"Case {self.id} - {self.full_name or 'Unknown'} (Urgency: {self.urgency_score}/10)"


class Message(models.Model):
    ROLE_CHOICES = [
        ('user', 'User'),
        ('assistant', 'Assistant'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.role}: {self.content[:50]}"
