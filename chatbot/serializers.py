from rest_framework import serializers
from .models import Conversation, Message, CaseSubmission


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['id', 'role', 'content', 'created_at']
        read_only_fields = ['id', 'created_at']


class ConversationSerializer(serializers.ModelSerializer):
    messages = MessageSerializer(many=True, read_only=True)
    
    class Meta:
        model = Conversation
        fields = ['id', 'created_at', 'updated_at', 'is_complete', 'messages']
        read_only_fields = ['id', 'created_at', 'updated_at']


class CaseSubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CaseSubmission
        fields = '__all__'
        read_only_fields = ['id', 'submitted_at']
