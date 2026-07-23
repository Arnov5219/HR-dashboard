"""Unit tests for 4-punch attendance models, status rules, unique constraint, and dashboard views."""

from datetime import date, time, datetime
from django.db.utils import IntegrityError
from django.test import RequestFactory, TestCase
from django.urls import reverse
from unittest.mock import patch

from attendance.models import Attendance, Employee
from attendance.views import dashboard_view


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
    """Test suite for attendance dashboard view, summary cards, and search using mocked Excel data."""

    def setUp(self) -> None:
        self.factory = RequestFactory()
        self.dashboard_url = reverse('attendance:dashboard')

        self.today = date.today()
        # Mock attendance records matching the expected format from excel (as dictionaries)
        self.mock_records = [
            {
                'employee_id': 'EMP001',
                'employee_name': 'John Doe',
                'date': self.today,
                'in_time': time(9, 0),
                'out_time': None,
                'last_punch': time(9, 0),
                'status': 'Working',
                'last_updated': datetime.combine(self.today, time(9, 0)),
                'total_hours': '09:00'
            },
            {
                'employee_id': 'EMP002',
                'employee_name': 'Jane Smith',
                'date': self.today,
                'in_time': time(9, 0),
                'out_time': None,
                'last_punch': time(13, 0),
                'status': 'On Break',
                'last_updated': datetime.combine(self.today, time(13, 0)),
                'total_hours': '04:00'
            }
        ]

        # Patch the read_attendance_data function called in views
        self.patcher = patch('attendance.views.read_attendance_data')
        self.mock_read = self.patcher.start()
        self.mock_read.return_value = self.mock_records

    def tearDown(self) -> None:
        self.patcher.stop()

    def test_dashboard_renders(self) -> None:
        """Dashboard view should render status 200 with summary card stats from mocked excel data."""
        request = self.factory.get(self.dashboard_url)
        response = dashboard_view(request)
        self.assertEqual(response.status_code, 200)
        content = response.content.decode()
        self.assertIn("John Doe", content)
        self.assertIn("Jane Smith", content)
        self.assertIn("09:00", content)
        self.assertIn("04:00", content)

    def test_search_by_employee_id(self) -> None:
        """Search query matching employee_id should filter records."""
        request = self.factory.get(f"{self.dashboard_url}?search=EMP001")
        response = dashboard_view(request)
        self.assertEqual(response.status_code, 200)
        content = response.content.decode()
        self.assertIn("John Doe", content)
        self.assertNotIn("Jane Smith", content)

    def test_search_by_employee_name(self) -> None:
        """Search query matching employee name should filter records."""
        request = self.factory.get(f"{self.dashboard_url}?search=Jane")
        response = dashboard_view(request)
        self.assertEqual(response.status_code, 200)
        content = response.content.decode()
        self.assertNotIn("John Doe", content)
        self.assertIn("Jane Smith", content)

    def test_dashboard_excel_missing_handled(self) -> None:
        """Dashboard view should handle FileNotFoundError gracefully and display error message."""
        self.mock_read.side_effect = FileNotFoundError("Excel file not found at path")
        request = self.factory.get(self.dashboard_url)
        response = dashboard_view(request)
        self.assertEqual(response.status_code, 200)
        content = response.content.decode()
        self.assertIn("could not be found", content)
        self.assertIn("No attendance records found for today", content)

    def test_dashboard_excel_locked_handled(self) -> None:
        """Dashboard view should handle PermissionError gracefully and display error message."""
        self.mock_read.side_effect = PermissionError("Permission denied. Locked file.")
        request = self.factory.get(self.dashboard_url)
        response = dashboard_view(request)
        self.assertEqual(response.status_code, 200)
        content = response.content.decode()
        self.assertIn("locked or open in another application", content)
        self.assertIn("No attendance records found for today", content)

