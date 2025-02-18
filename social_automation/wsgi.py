"""
WSGI config for social_automation project.
"""

import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'social_automation.settings')

# This is the Django WSGI application
application = get_wsgi_application()

# This is the handler that Vercel looks for
app = application

# This is also needed for Vercel
handler = app 