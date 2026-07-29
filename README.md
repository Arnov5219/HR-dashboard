# CARLine Employee Attendance Dashboard

A Django web application for demonstrating Django fundamentals

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

- **Attendance Dashboard**: `http://127.0.0.1:8000/`


