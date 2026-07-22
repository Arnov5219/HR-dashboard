# CARLine Employee Attendance Dashboard

A simple, clean, internship-level Django web application for demonstrating Django fundamentals (Models, Views, Templates, Admin, and ORM).

---

## 🎯 Attendance Workflow

The attendance system follows a fixed 4-punch daily workflow (maximum 4 punches per day):

1. **In** (`in_time`) &rarr; Status: **Working**
2. **Break Start** (`break_start`) &rarr; Status: **On Break**
3. **Break End** (`break_end`) &rarr; Status: **Working**
4. **Final Out** (`final_out`) &rarr; Status: **Checked Out**

*Note: If no punches are recorded, the status defaults to **Absent**.*

---

## 📊 Features

- 📈 **5 Summary Cards**: Total Employees, Present Today, Working, On Break, Checked Out.
- 📋 **Today's Attendance Table**: Displays Employee ID, Employee Name, Date, In, Break Start, Break End, Final Out, and Status.
- 🔍 **Employee Search**: Search attendance records by Employee ID or Employee Name.
- 🛠️ **Django Admin**: Manage Employee and Attendance records with 4-punch fields and search filtering.
- 🎨 **Clean Bootstrap 5 UI**: Responsive corporate blue and white design with color-coded status badges.
- 🗄️ **SQLite Database**: Out-of-the-box local setup with database constraints enforcing one attendance record per employee per day.

---

## 📁 Folder Structure

```text
carline_attendance/
│
├── carline_attendance/      # Django project settings and URLs
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── attendance/              # Main attendance Django app
│   ├── models.py            # Employee and Attendance (4-punch) models
│   ├── views.py             # Dashboard view with summary stats & search
│   ├── urls.py              # URL routing for dashboard
│   ├── admin.py             # Registered Employee and Attendance models
│   ├── tests.py             # Unit tests for models, constraints, and views
│   └── management/
│       └── commands/
│           └── seed_data.py # Sample data generator (4-punch flow)
├── templates/               # HTML5 Bootstrap 5 templates
│   ├── base.html
│   └── dashboard.html
├── static/                  # Static assets (CSS)
│   └── css/style.css
├── manage.py
├── db.sqlite3               # SQLite database
├── requirements.txt         # Dependencies (Django 5.x)
└── README.md
```

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
Populate the database with sample employees (`EMP001` - `EMP010`) and today's attendance records following the 4-punch workflow:
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

- **Attendance Dashboard**: `http://127.0.0.1:8000/`
- **Django Admin Panel**: `http://127.0.0.1:8000/admin/`

