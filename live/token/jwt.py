"""
Brief: Django views.py file.

Description: This file contains the views for the Django live app.

Author: Divij Sharma <divijs75@gmail.com>
"""


class TokenStrategy:
    """
    Custom token strategy class for obtaining the token.
    """
    @classmethod
    def obtain(cls, user):
        """
        Obtain the token for the user.
        """
        import jwt
        import datetime
        from django.conf import settings
        payload = {
            'social_user_id': user.id,
            'username': user.username,
            'exp': datetime.datetime.now() + datetime.timedelta(days=1)
        }
        token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
        return {"access": token, "user": user.username}
