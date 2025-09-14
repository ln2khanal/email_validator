from django.urls import path
from . import views 

urlpatterns = [
    path('validate-emails/', views.ValidateEmailsView.as_view(), name='validate-emails'),
]

