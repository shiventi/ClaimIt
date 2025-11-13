from django.urls import path
from . import views

urlpatterns = [
    path('list/', views.list_forms, name='list-forms'),
    path('<str:form_name>/', views.get_form, name='get-form'),
]
