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

        # Create today's attendance records
        sample_attendances = [
            (employees[0], time(9, 0)),
            (employees[1], time(9, 2)),
            (employees[2], time(8, 55)),
            (employees[3], None),
            (employees[4], time(9, 10)),
            (employees[5], time(9, 0)),
            (employees[6], None),
            (employees[7], time(8, 50)),
            (employees[8], time(9, 15)),
            (employees[9], time(9, 5)),
        ]

        for emp, in_t in sample_attendances:
            Attendance.objects.update_or_create(
                employee=emp,
                date=today,
                defaults={
                    "in_time": in_t,
                }
            )

        self.stdout.write(self.style.SUCCESS("Successfully seeded sample employees and attendance records!"))

