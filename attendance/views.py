import math
from datetime import date, timedelta

from django.shortcuts import render
from django.http import JsonResponse

from attendance.services import ExcelAttendanceService

def dashboard_view(request):
    """Render the main attendance dashboard template."""
    return render(request, 'dashboard.html')

def filters_view(request):
    """Render the standalone attendance filters page."""
    return render(request, 'filters.html')

def api_filters_view(request):
    """Return the options used by the Filters page."""
    try:
        employees, records = ExcelAttendanceService.load_data()
        unique_dates = sorted(list(set(r['date'] for r in records if r['date'])), reverse=True)
        available_dates = [
            {'value': d.strftime('%Y-%m-%d'), 'label': d.strftime('%d-%m-%Y')}
            for d in unique_dates
        ]
        weeks = sorted(
            {f"Week {record['date'].isocalendar().week} ({record['date'].year})" for record in records if record['date']},
            reverse=True
        )
        return JsonResponse({
            'employees': [{'id': emp_id, 'name': emp_name} for emp_id, emp_name in sorted(employees.items())],
            'available_dates': available_dates,
            'weeks': weeks,
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def _parse_request_filters(request):
    """Parse the filters supported by the dashboard pages."""
    search_query = request.GET.get('search', '').strip()
    
    employee_ids = request.GET.get('employees', '')
    if employee_ids:
        employee_ids = [x.strip() for x in employee_ids.split(',') if x.strip()]
    else:
        employee_ids = []
        
    weeks = request.GET.get('weeks', '')
    if weeks:
        weeks = [x.strip() for x in weeks.split(',') if x.strip()]
    else:
        weeks = []
        
    # Date Range Filter
    date_range_type = request.GET.get('date_range', '')
    start_date, end_date = None, None
    today = date.today()
    
    if date_range_type == 'all':
        # Keep both bounds unset so the complete attendance history is returned.
        start_date, end_date = None, None
    elif date_range_type == 'yesterday':
        yest = today - timedelta(days=1)
        start_date, end_date = yest, yest
    elif date_range_type == 'last_7_days':
        start_date, end_date = today - timedelta(days=6), today
    elif date_range_type == 'this_month':
        start_date, end_date = today.replace(day=1), today
    elif date_range_type == 'custom':
        custom_start = request.GET.get('start_date', '')
        custom_end = request.GET.get('end_date', '')
        start_date = ExcelAttendanceService._parse_date(custom_start)
        end_date = ExcelAttendanceService._parse_date(custom_end)
    elif date_range_type == 'selected_dates':
        # Used for Excel-like multi-select hierarchical date checklist
        # Expected format: dates=2026-07-22,2026-07-23...
        selected_dates_str = request.GET.get('dates', '')
        if selected_dates_str:
            dates_list = [ExcelAttendanceService._parse_date(x.strip()) for x in selected_dates_str.split(',') if x.strip()]
            dates_list = [d for d in dates_list if d is not None]
            return search_query, employee_ids, None, None, dates_list, weeks
            
    return search_query, employee_ids, start_date, end_date, None, weeks

def _apply_filters(records, search_query, employee_ids, start_date, end_date, selected_dates, weeks):
    """Apply the filters supported by the dashboard pages."""
    date_range = None
    if start_date or end_date:
        date_range = {'start': start_date, 'end': end_date}
        
    filtered = ExcelAttendanceService.get_filtered_records(
        records,
        search_query=search_query,
        employee_ids=employee_ids,
        date_range=date_range,
        weeks=weeks
    )
    if selected_dates:
        dates_set = set(selected_dates)
        filtered = [r for r in filtered if r['date'] in dates_set]
        
    return filtered

def _paginate_and_serialize(request, records, default_sort_col='', default_sort_dir='asc'):
    """Helper to sort, paginate and serialize JSON response."""
    # Sorting parameters
    sort_col = request.GET.get('sort_col', default_sort_col)
    sort_dir = request.GET.get('sort_dir', default_sort_dir) # asc or desc
    
    # Sort
    sorted_records = ExcelAttendanceService.get_filtered_records(records, sort_col=sort_col, sort_dir=sort_dir)
    
    # Pagination parameters
    try:
        page = int(request.GET.get('page', 1))
        limit = int(request.GET.get('limit', 25))
    except ValueError:
        page = 1
        limit = 25
        
    total_count = len(sorted_records)
    
    # Calculate slices
    start = (page - 1) * limit
    end = start + limit
    paginated = sorted_records[start:end]
    
    # Serialize times & dates for JSON
    serialized = []
    for r in paginated:
        serialized.append({
            'employee_id': r['employee_id'],
            'employee_name': r['employee_name'],
            'date': r['date'].strftime('%d-%m-%Y') if r['date'] else None,
            'in_time': r['in_time'].strftime('%H:%M') if r['in_time'] else None,
            'out_time': r['out_time'].strftime('%H:%M') if r['out_time'] else None,
            'total_hours': r['total_hours']
        })
        
    pages = math.ceil(total_count / limit) if limit > 0 else 1
    
    return {
        'records': serialized,
        'total_count': total_count,
        'page': page,
        'limit': limit,
        'pages': pages
    }

def api_attendance_today_view(request):
    """JSON endpoint for Today's Attendance records."""
    try:
        today = date.today()
        # Today's records are processed (with synthethic Absent records for employees not present)
        records = ExcelAttendanceService.get_processed_records(today)
        
        # Parse and apply search/filters
        search_q, emp_ids, start_d, end_d, sel_dates, weeks = _parse_request_filters(request)
        filtered = _apply_filters(records, search_q, emp_ids, start_d, end_d, sel_dates, weeks)
        
        # Paginate & return
        data = _paginate_and_serialize(request, filtered)
        return JsonResponse(data)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def api_attendance_history_view(request):
    """JSON endpoint for Historical Attendance records."""
    try:
        today = date.today()
        records = ExcelAttendanceService.get_all_attendance_history(today)
        
        # Parse and apply search/filters
        search_q, emp_ids, start_d, end_d, sel_dates, weeks = _parse_request_filters(request)
        filtered = _apply_filters(records, search_q, emp_ids, start_d, end_d, sel_dates, weeks)
        
        # Paginate & return
        data = _paginate_and_serialize(
            request,
            filtered,
            default_sort_col='date',
            default_sort_dir='desc'
        )
        return JsonResponse(data)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
