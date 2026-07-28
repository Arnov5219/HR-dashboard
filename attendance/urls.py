"""URL routing for attendance app."""

from django.urls import path
from attendance.views import (
    dashboard_view,
    filters_view,
    api_stats_view,
    api_charts_view,
    api_filters_view,
    api_attendance_today_view,
    api_attendance_history_view,
    api_export_view
)

app_name = 'attendance'

urlpatterns = [
    path('', dashboard_view, name='dashboard'),
    path('filters/', filters_view, name='filters'),
    path('api/stats/', api_stats_view, name='api_stats'),
    path('api/charts/', api_charts_view, name='api_charts'),
    path('api/filters/', api_filters_view, name='api_filters'),
    path('api/attendance/today/', api_attendance_today_view, name='api_attendance_today'),
    path('api/attendance/history/', api_attendance_history_view, name='api_attendance_history'),
    path('api/export/', api_export_view, name='api_export'),
]
