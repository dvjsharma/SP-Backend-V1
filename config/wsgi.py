"""
Brief: WSGI config for config project.

Description: It exposes the WSGI callable as a module-level variable named ``application``.

Author : Divij Sharma <divijs75@gmail.com>
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

application = get_wsgi_application()
