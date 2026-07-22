"""Management command to populate sample data for demonstration."""

from datetime import date, time
from django.core.management.base import BaseCommand
from attendance.models import Attendance, Employee


class Command(BaseCommand):
    help = "Seeds database with sample employees and today's attendance records."

    def handle(self, *args, **options):
        self.stdout.write("Seeding sample data...")

        # Create sample employees
        sample_employees = [
            ("EMP001", "John Doe"),
            ("EMP002", "Sarah Smith"),
            ("EMP003", "Michael Johnson"),
            ("EMP004", "Emily Davis"),
            ("EMP005", "David Wilson"),
            ("EMP006", "Jessica Taylor"),
            ("EMP007", "James Anderson"),
            ("EMP008", "Amanda Thomas"),
            ("EMP009", "Robert Martinez"),
            ("EMP010", "Mary Jackson"),
        ]

        employees = []
        for emp_id, name in sample_employees:
            emp, _ = Employee.objects.get_or_create(
                employee_id=emp_id,
                defaults={"name": name}
            )
            employees.append(emp)

        today = date.today()

        # Create today's attendance records following the 4-punch workflow
        sample_attendances = [
            (employees[0], time(9, 0), time(13, 0), time(13, 30), time(18, 0)),   # Checked Out
            (employees[1], time(9, 2), time(13, 0), None, None),                 # On Break
            (employees[2], time(8, 55), time(12, 30), time(13, 0), time(17, 30)), # Checked Out
            (employees[3], None, None, None, None),                              # Absent
            (employees[4], time(9, 10), None, None, None),                       # Working
            (employees[5], time(9, 0), time(13, 0), time(13, 30), time(17, 0)),   # Checked Out
            (employees[6], None, None, None, None),                              # Absent
            (employees[7], time(8, 50), time(12, 45), time(13, 15), None),        # Working
            (employees[8], time(9, 15), time(13, 15), time(13, 45), time(17, 15)), # Checked Out
            (employees[9], time(9, 5), time(13, 0), None, None),                 # On Break
        ]

        for emp, in_t, b_start, b_end, f_out in sample_attendances:
            Attendance.objects.update_or_create(
                employee=emp,
                date=today,
                defaults={
                    "in_time": in_t,
                    "break_start": b_start,
                    "break_end": b_end,
                    "final_out": f_out,
                }
            )

        self.stdout.write(self.style.SUCCESS("Successfully seeded sample employees and attendance records!"))

