# CARLine Live Attendance Dashboard

A Django-based web application for monitoring employee attendance in real time. The dashboard displays live attendance records, employee status, check-in/check-out times, total working hours, and supports attendance data synchronization from the HR Excel attendance system.

---

## Features

- **Live Attendance Dashboard**: Real-time view of all employee attendance records
- **Employee Status**: Track current attendance status (Present, Absent, Late, On Leave)
- **Check-in/Check-out**: Log daily attendance with timestamps
- **Total Working Hours**: Automatic calculation of daily working hours
- **Data Synchronization**: Import and sync attendance data from Excel files

---

## 🚀 Running the Project

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Apply Database Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 3. Seed Sample Data (Optional)
Populate the database with sample employees (`EMP001` - `EMP010`) and today's attendance records:
```bash
python manage.py seed_data
```

### 4. Create Admin Superuser (Optional)
```bash
python manage.py createsuperuser
```

### 5. Run Development Server
```bash
python manage.py runserver
```
- **Live Attendance Dashboard:** http://127.0.0.1:4000/
- **Admin Panel:** http://127.0.0.1:4000/admin/
---