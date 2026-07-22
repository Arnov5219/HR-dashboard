"""Views for rendering attendance dashboard and search."""

from datetime import date
from django.shortcuts import render
from attendance.excel_reader import read_attendance_data


def dashboard_view(request):
    """Render the main attendance dashboard with summary cards and search."""
    today = date.today()
    search_query = request.GET.get('search', '').strip()
    error_message = None

    today_records = []

    try:
        # Load all records from Excel
        all_records = read_attendance_data()

        # Filter for today's records
        today_records = [rec for rec in all_records if rec['date'] == today]

    except FileNotFoundError:
        error_message = "The Excel file (HR_Master.xlsm) could not be found. Please make sure it is located at the configured path."
    except PermissionError:
        error_message = "The Excel file (HR_Master.xlsm) is currently locked or open in another application. Please close the file and try again."
    except Exception as e:
        error_message = f"An error occurred while reading the Excel file: {str(e)}"

    # Apply search filter (by Employee ID or Employee Name)
    filtered_records = today_records
    if search_query:
        q = search_query.lower()
        filtered_records = [
            rec for rec in today_records
            if q in rec['employee_id'].lower() or q in rec['employee_name'].lower()
        ]

    # Calculate summary card metrics from unfiltered records
    # total_employees is all unique employees in today's records
    unique_emp_ids = {rec['employee_id'] for rec in today_records}
    total_employees = len(unique_emp_ids)

    # Compute status stats based on the filtered records
    present_today = 0
    working = 0
    on_break = 0
    checked_out = 0

    for rec in filtered_records:
        status_val = rec['status']
        # Any status other than 'Absent' counts as present
        if status_val.lower() not in ['absent', '']:
            present_today += 1
        
        if status_val.lower() == 'working':
            working += 1
        elif status_val.lower() == 'on break':
            on_break += 1
        elif status_val.lower() == 'checked out':
            checked_out += 1

    context = {
        'today_date': today,
        'search_query': search_query,
        'attendance_records': filtered_records,
        'total_employees': total_employees,
        'present_today': present_today,
        'working': working,
        'on_break': on_break,
        'checked_out': checked_out,
        'error_message': error_message,
    }
    return render(request, 'dashboard.html', context)

