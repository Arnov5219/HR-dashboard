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

    STATUS_CHOICES = [
        ('Present', 'Present'),
        ('Working', 'Working'),
        ('On Break', 'On Break'),
        ('Checked Out', 'Checked Out'),
        ('Absent', 'Absent'),
    ]

    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='attendances'
    )
    date = models.DateField()
    in_time = models.TimeField(null=True, blank=True)
    break_start = models.TimeField(null=True, blank=True)
    break_end = models.TimeField(null=True, blank=True)
    final_out = models.TimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Absent')

    class Meta:
        ordering = ['-date', 'employee__employee_id']
        constraints = [
            models.UniqueConstraint(
                fields=['employee', 'date'],
                name='unique_employee_attendance_per_day'
            )
        ]

    def update_status(self) -> None:
        """Update status automatically based on attendance punches."""
        if self.final_out:
            self.status = 'Checked Out'
        elif self.break_end:
            self.status = 'Working'
        elif self.break_start:
            self.status = 'On Break'
        elif self.in_time:
            self.status = 'Working'
        else:
            self.status = 'Absent'

    def save(self, *args, **kwargs) -> None:
        if self.status != 'Present':
            self.update_status()
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.employee.employee_id} | {self.date} | {self.status}"

