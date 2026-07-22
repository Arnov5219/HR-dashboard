"""Django Admin registration for Employee and Attendance models."""

from django.contrib import admin
from attendance.models import Attendance, Employee


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    """Admin configuration for Employee model."""
    list_display = ('employee_id', 'name')
    search_fields = ('employee_id', 'name')


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    """Admin configuration for Attendance model."""
    list_display = ('employee', 'date', 'in_time', 'break_start', 'break_end', 'final_out', 'status')
    list_filter = ('status', 'date')
    search_fields = ('employee__employee_id', 'employee__name')

