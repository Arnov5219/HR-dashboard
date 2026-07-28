"""WSGI config for carline_attendance project."""

import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'carline_attendance.settings')

application = get_wsgi_application()
