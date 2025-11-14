from django.apps import AppConfig


class ChatbotConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'chatbot'

    def ready(self):
        """Run startup checks when Django app is ready"""
        import os
        # Only test connection in production or when explicitly enabled
        if os.getenv('DJANGO_SETTINGS_MODULE') == 'backend.settings_production' or os.getenv('TEST_SUPABASE_ON_STARTUP'):
            from .supabase_sync import test_supabase_connection
            test_supabase_connection()
