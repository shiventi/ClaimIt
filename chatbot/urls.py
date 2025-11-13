from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ConversationViewSet,
    employee_login,
    dashboard_cases,
    dashboard_case_detail,
    dashboard_conversations,
    dashboard_conversation_detail,
    dashboard_conversation_case,
    dashboard_stats,
)

router = DefaultRouter()
router.register(r'conversations', ConversationViewSet, basename='conversation')

urlpatterns = [
    path('', include(router.urls)),
    # Dashboard endpoints
    path('auth/login/', employee_login, name='employee-login'),
    path('dashboard/cases/', dashboard_cases, name='dashboard-cases'),
    path('dashboard/cases/<str:case_id>/', dashboard_case_detail, name='dashboard-case-detail'),
    path('dashboard/conversations/', dashboard_conversations, name='dashboard-conversations'),
    path('dashboard/conversations/<str:conversation_id>/', dashboard_conversation_detail, name='dashboard-conversation-detail'),
    path('dashboard/conversations/<str:conversation_id>/case_summary/', dashboard_conversation_case, name='dashboard-conversation-case'),
    path('dashboard/stats/', dashboard_stats, name='dashboard-stats'),
]
