from django.contrib import admin
from .models import Conversation, Message, CaseSubmission

@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ['id', 'created_at', 'is_complete']
    list_filter = ['is_complete', 'created_at']
    search_fields = ['id']
    ordering = ['-created_at']

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['id', 'conversation', 'role', 'created_at', 'content_preview']
    list_filter = ['role', 'created_at']
    search_fields = ['content']
    ordering = ['-created_at']
    
    def content_preview(self, obj):
        return obj.content[:100] + '...' if len(obj.content) > 100 else obj.content
    content_preview.short_description = 'Content'

@admin.register(CaseSubmission)
class CaseSubmissionAdmin(admin.ModelAdmin):
    list_display = ['id', 'full_name', 'urgency_score', 'submitted_at', 'has_emergency_needs', 'programs_preview']
    list_filter = ['urgency_score', 'has_emergency_needs', 'submitted_at']
    search_fields = ['full_name', 'phone_number', 'email']
    ordering = ['-urgency_score', '-submitted_at']
    readonly_fields = ['submitted_at', 'structured_summary']
    
    fieldsets = (
        ('Case Information', {
            'fields': ('conversation', 'submitted_at', 'urgency_score', 'urgency_reasoning')
        }),
        ('Personal Information', {
            'fields': ('full_name', 'date_of_birth', 'age', 'phone_number', 'email')
        }),
        ('Household', {
            'fields': ('household_size', 'household_members', 'has_children')
        }),
        ('Financial', {
            'fields': ('monthly_income', 'income_sources', 'total_assets', 'monthly_rent', 'monthly_expenses')
        }),
        ('Employment', {
            'fields': ('employment_status', 'current_employer', 'job_title', 'employment_duration')
        }),
        ('Housing', {
            'fields': ('housing_situation', 'address', 'at_risk_of_homelessness')
        }),
        ('Health', {
            'fields': ('has_disability', 'disability_details', 'has_health_insurance', 
                      'has_medical_expenses', 'monthly_medical_costs')
        }),
        ('Legal/Immigration', {
            'fields': ('citizenship_status', 'immigration_status')
        }),
        ('Benefits & Emergency', {
            'fields': ('current_benefits', 'has_emergency_needs', 'emergency_details')
        }),
        ('AI-Generated', {
            'fields': ('ai_summary', 'recommended_programs', 'recommended_actions', 'structured_summary')
        }),
    )
    
    def programs_preview(self, obj):
        return ', '.join(obj.recommended_programs) if obj.recommended_programs else 'None'
    programs_preview.short_description = 'Recommended Programs'
