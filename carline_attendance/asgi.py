"""ASGI config for carline_attendance project."""

import os
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'carline_attendance.settings')

application = get_asgi_application()
