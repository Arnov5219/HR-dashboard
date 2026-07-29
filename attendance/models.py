"""Models for Employee and Attendance tracking."""

from django.db import models


class Employee(models.Model):
    """Represents an employee in the organization."""

    employee_id = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=150)

    class Meta:
        ordering = ['employee_id']

    def __str__(self) -> str:
        return f"{self.employee_id} - {self.name}"


class Attendance(models.Model):
    """Represents daily attendance record for an employee."""

    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='attendances'
    )
    date = models.DateField()
    in_time = models.TimeField(null=True, blank=True)

    class Meta:
        ordering = ['-date', 'employee__employee_id']
        constraints = [
            models.UniqueConstraint(
                fields=['employee', 'date'],
                name='unique_employee_attendance_per_day'
            )
        ]

    def __str__(self) -> str:
        return f"{self.employee.employee_id} | {self.date}"

