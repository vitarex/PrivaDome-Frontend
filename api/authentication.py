"""
Expiring token authentication.
"""
import datetime

from rest_framework.authentication import TokenAuthentication
from rest_framework import exceptions

from django.utils.translation import ugettext_lazy as _

class ExpiringTokenAuthentication(TokenAuthentication):
    """
    Expiring token authentication.
    """
    def authenticate_credentials(self, key):
        model = self.get_model()
        try:
            token = model.objects.select_related('user').get(key=key)
        except model.DoesNotExist:
            raise exceptions.AuthenticationFailed(_('Invalid token.'))

        if not token.user.is_active:
            raise exceptions.AuthenticationFailed(_('User inactive or deleted.'))

        utc_now = datetime.datetime.utcnow()

        if token.created < utc_now - datetime.timedelta(hours=24):
            raise exceptions.AuthenticationFailed(_('Token has expired'))

        return (token.user, token)
