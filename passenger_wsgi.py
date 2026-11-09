import os
import sys

# Path direktori root project
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

# Menentukan settings module Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bph_project.settings')

# Inisialisasi WSGI application untuk Passenger cPanel
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
