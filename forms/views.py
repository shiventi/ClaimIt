from django.http import HttpResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response


@api_view(['GET', 'POST'])
def get_form(request, form_name):
    """Serve forms - simplified version without PDF"""
    return Response({'message': 'Form functionality removed - use dashboard instead'})


@api_view(['GET'])
def list_forms(request):
    """List available forms - simplified"""
    return Response({'forms': [], 'message': 'PDF forms removed - use dashboard for case management'})
