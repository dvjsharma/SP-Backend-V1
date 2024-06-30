"""
Brief: ASGI config for config project.

Description: It exposes the ASGI callable as a module-level variable named ``application``.

Author: Divij Sharma <divijs75@gmail.com>
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

application = get_asgi_application()
