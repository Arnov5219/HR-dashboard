@echo off

echo Creating virtual environment...
python -m venv .venv

echo Activating virtual environment...
call .venv\Scripts\activate

echo Installing dependencies...
pip install -r requirements.txt

echo Running migrations...
python manage.py migrate

echo Starting Django server...
python manage.py runserver

pause
