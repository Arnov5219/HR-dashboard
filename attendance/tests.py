"""Unit tests for 4-punch attendance models, status rules, unique constraint, and dashboard API views."""

from datetime import date, time, datetime
import json
from django.db.utils import IntegrityError
from django.test import RequestFactory, TestCase
from django.urls import reverse
from unittest.mock import patch

from attendance.models import Attendance, Employee
from attendance.views import (
    dashboard_view,
    api_stats_view,
    api_charts_view,
    api_filters_view,
    api_attendance_today_view,
    api_attendance_history_view
)
from attendance.services import ExcelAttendanceService


class AttendanceModelTestCase(TestCase):
    """Test suite for Attendance model 4-punch workflow and database constraints."""

    def setUp(self) -> None:
        self.emp = Employee.objects.create(employee_id="EMP001", name="John Doe")
        self.today = date.today()

    def test_auto_status_no_punches(self) -> None:
        """No punches should automatically set status to Absent."""
        att = Attendance.objects.create(employee=self.emp, date=self.today)
        self.assertEqual(att.status, "Absent")

    def test_auto_status_in_only(self) -> None:
        """Only In recorded should set status to Working."""
        att = Attendance.objects.create(
            employee=self.emp,
            date=self.today,
            in_time=time(9, 0)
        )
        self.assertEqual(att.status, "Working")

    def test_auto_status_break_start(self) -> None:
        """In + Break Start recorded should set status to On Break."""
        att = Attendance.objects.create(
            employee=self.emp,
            date=self.today,
            in_time=time(9, 0),
            break_start=time(13, 0)
        )
        self.assertEqual(att.status, "On Break")

    def test_auto_status_break_end(self) -> None:
        """Break End recorded should set status back to Working."""
        att = Attendance.objects.create(
            employee=self.emp,
            date=self.today,
            in_time=time(9, 0),
            break_start=time(13, 0),
            break_end=time(13, 30)
        )
        self.assertEqual(att.status, "Working")

    def test_auto_status_final_out(self) -> None:
        """Final Out recorded should set status to Checked Out."""
        att = Attendance.objects.create(
            employee=self.emp,
            date=self.today,
            in_time=time(9, 0),
            break_start=time(13, 0),
            break_end=time(13, 30),
            final_out=time(18, 0)
        )
        self.assertEqual(att.status, "Checked Out")

    def test_unique_attendance_per_day_constraint(self) -> None:
        """Employee cannot have more than one attendance record per day."""
        Attendance.objects.create(employee=self.emp, date=self.today, in_time=time(9, 0))
        with self.assertRaises(IntegrityError):
            Attendance.objects.create(employee=self.emp, date=self.today, in_time=time(9, 30))


class AttendanceDashboardTestCase(TestCase):
    """Test suite for attendance dashboard view, stats, charts, search and pagination using mocked Excel data."""

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
                'total_hours': None,
                'status': 'Working'
            },
            {
                'employee_id': 'EMP002',
                'employee_name': 'Jane Smith',
                'date': self.yesterday,
                'in_time': time(9, 0),
                'out_time': time(17, 0),
                'total_hours': '08:00',
                'status': 'Completed'
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

    def test_stats_api(self) -> None:
        """Stats API should return today's counts including synthesized Absent records."""
        request = self.factory.get(reverse('attendance:api_stats'))
        response = api_stats_view(request)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode())
        
        # EMP001 has today's record (Present). EMP002 has yesterday's record, so EMP002 is Absent today.
        self.assertEqual(data['total_employees'], 2)
        self.assertEqual(data['present'], 1)
        self.assertEqual(data['late'], 0)
        self.assertEqual(data['absent'], 1)

    def test_charts_api(self) -> None:
        """Charts API should return datasets for Pie, Bar, and Line charts."""
        request = self.factory.get(reverse('attendance:api_charts'))
        response = api_charts_view(request)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode())
        
        self.assertIn('pie', data)
        self.assertIn('bar', data)
        self.assertIn('line', data)

    def test_filters_api(self) -> None:
        """Filters API should return lists of employees, statuses, and dates tree."""
        request = self.factory.get(reverse('attendance:api_filters'))
        response = api_filters_view(request)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode())
        
        self.assertEqual(len(data['employees']), 2)
        self.assertIn('statuses', data)
        self.assertIn('dates', data)

    def test_today_attendance_api_search_and_sort(self) -> None:
        """Today's attendance endpoint should filter and paginate correctly."""
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

    def test_history_attendance_api_date_range(self) -> None:
        """History attendance endpoint should return historical records and respect limits/pagination."""
        request = self.factory.get(reverse('attendance:api_attendance_history'))
        response = api_attendance_history_view(request)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode())
        
        # Returns both yesterday's record for Jane Smith and today's record for John Doe
        self.assertEqual(data['total_count'], 2)
        self.assertEqual(data['records'][0]['employee_name'], 'John Doe')
        self.assertEqual(data['records'][1]['employee_name'], 'Jane Smith')

from datetime import timedelta
