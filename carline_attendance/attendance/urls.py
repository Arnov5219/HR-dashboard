"""URL routing for attendance app."""

from django.urls import path
from attendance.views import dashboard_view

app_name = 'attendance'

urlpatterns = [
    path('', dashboard_view, name='dashboard'),
]
