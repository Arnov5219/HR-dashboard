"""Script to create a sample HR_Master.xlsm spreadsheet with mock attendance data for today.

Columns:
A - Employee ID
B - Employee Name
C - Date
D - IN
E - OUT
F - Last Punch
G - Status
H - Last Updated
"""

import os
from datetime import date, time, datetime
import openpyxl

def main():
    today = date.today()
    print(f"Creating sample Excel attendance sheet for today: {today}")

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Attendance"

    # Set headers exactly as required
    headers = [
        "Employee ID",
        "Employee Name",
        "Date",
        "IN",
        "OUT",
        "Last Punch",
        "Status",
        "Last Updated"
    ]
    ws.append(headers)

    # Sample rows corresponding to new columns and status (Working, Checked Out, Absent)
    sample_records = [
        ("EMP001", "John Doe", today, time(9, 0), None, time(9, 0), "Working", datetime.combine(today, time(9, 0))),
        ("EMP002", "Sarah Smith", today, time(9, 2), time(17, 30), time(17, 30), "Checked Out", datetime.combine(today, time(17, 30))),
        ("EMP003", "Michael Johnson", today, time(8, 55), None, time(8, 55), "Working", datetime.combine(today, time(8, 55))),
        ("EMP004", "Emily Davis", today, None, None, None, "Absent", datetime.combine(today, time(9, 0))),
        ("EMP005", "David Wilson", today, time(9, 10), None, time(9, 10), "Working", datetime.combine(today, time(9, 10))),
        ("EMP006", "Jessica Taylor", today, time(9, 0), time(17, 0), time(17, 0), "Checked Out", datetime.combine(today, time(17, 0))),
        ("EMP007", "James Anderson", today, None, None, None, "Absent", datetime.combine(today, time(9, 0))),
        ("EMP008", "Amanda Thomas", today, time(8, 50), None, time(8, 50), "Working", datetime.combine(today, time(8, 50))),
        ("EMP009", "Robert Martinez", today, time(9, 15), time(17, 15), time(17, 15), "Checked Out", datetime.combine(today, time(17, 15))),
        ("EMP010", "Mary Jackson", today, time(9, 5), None, time(9, 5), "Working", datetime.combine(today, time(9, 5))),
    ]

    for emp_id, name, d, in_t, out_t, last_p, status, last_u in sample_records:
        ws.append([
            emp_id,
            name,
            d,
            in_t,
            out_t,
            last_p,
            status,
            last_u
        ])

    file_name = "HR_Master.xlsm"
    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), file_name)
    
    wb.save(output_path)
    print(f"Successfully generated sample spreadsheet: {output_path}")

if __name__ == "__main__":
    main()
