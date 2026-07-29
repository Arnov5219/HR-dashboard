"""Unit tests for attendance models, database constraints, and dashboard API views."""

from datetime import date, time, timedelta
import json
from django.db.utils import IntegrityError
from django.test import RequestFactory, TestCase
from django.urls import reverse
from unittest.mock import patch

from attendance.models import Attendance, Employee
from attendance.views import (
    dashboard_view,
    api_filters_view,
    api_attendance_today_view,
    api_attendance_history_view
)


class AttendanceModelTestCase(TestCase):
    """Test suite for Attendance model and database constraints."""

    def setUp(self) -> None:
        self.emp = Employee.objects.create(employee_id="EMP001", name="John Doe")
        self.today = date.today()


    def test_unique_attendance_per_day_constraint(self) -> None:
        """Employee cannot have more than one attendance record per day."""
        Attendance.objects.create(employee=self.emp, date=self.today, in_time=time(9, 0))
        with self.assertRaises(IntegrityError):
            Attendance.objects.create(employee=self.emp, date=self.today, in_time=time(9, 30))


class AttendanceDashboardTestCase(TestCase):
    """Tests for the active dashboard and Filters page APIs."""

    def setUp(self) -> None:
        self.factory = RequestFactory()
        self.today = date.today()
        self.yesterday = self.today - timedelta(days=1)
        
        self.mock_employees = {
            'EMP001': 'John Doe',
            'EMP002': 'Jane Smith'
        }
        
        # Mock attendance records matching the expected format from excel (as dictionaries)
        self.mock_records = [
            {
                'employee_id': 'EMP001',
                'employee_name': 'John Doe',
                'date': self.today,
                'in_time': time(9, 0),
                'out_time': None,
                'total_hours': None
            },
            {
                'employee_id': 'EMP002',
                'employee_name': 'Jane Smith',
                'date': self.yesterday,
                'in_time': time(9, 0),
                'out_time': time(17, 0),
                'total_hours': '08:00'
            }
        ]

        # Patch the load_data function inside services
        self.patcher = patch('attendance.services.ExcelAttendanceService.load_data')
        self.mock_load = self.patcher.start()
        self.mock_load.return_value = (self.mock_employees, self.mock_records)

    def tearDown(self) -> None:
        self.patcher.stop()

    def test_dashboard_shell_renders(self) -> None:
        """Dashboard view should render status 200."""
        request = self.factory.get(reverse('attendance:dashboard'))
        response = dashboard_view(request)
        self.assertEqual(response.status_code, 200)

    def test_filters_api(self) -> None:
        """Filters API should return the options rendered by the Filters page."""
        request = self.factory.get(reverse('attendance:api_filters'))
        response = api_filters_view(request)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode())
        
        self.assertEqual(len(data['employees']), 2)
        self.assertIn('available_dates', data)
        self.assertIn('weeks', data)

    def test_today_attendance_api_search(self) -> None:
        """Today's attendance endpoint should return matching employees."""
        # Check all present
        request = self.factory.get(reverse('attendance:api_attendance_today'))
        response = api_attendance_today_view(request)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode())
        
        self.assertEqual(data['total_count'], 2) # John Doe (Working) and Jane Smith (Absent today)
        
        # Search for John
        request = self.factory.get(f"{reverse('attendance:api_attendance_today')}?search=John")
        response = api_attendance_today_view(request)
        data = json.loads(response.content.decode())
        self.assertEqual(data['total_count'], 1)
        self.assertEqual(data['records'][0]['employee_name'], 'John Doe')

    def test_history_attendance_api_orders_newest_first(self) -> None:
        """History attendance should return the newest records first."""
        request = self.factory.get(reverse('attendance:api_attendance_history'))
        response = api_attendance_history_view(request)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode())
        
        # Returns both yesterday's record for Jane Smith and today's record for John Doe
        self.assertEqual(data['total_count'], 2)
        self.assertEqual(data['records'][0]['employee_name'], 'John Doe')
        self.assertEqual(data['records'][1]['employee_name'], 'Jane Smith')
