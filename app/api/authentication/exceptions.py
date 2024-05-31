from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import APIException
from rest_framework import status as http_status


class UserNotActiveError(APIException):
    status_code = http_status.HTTP_401_UNAUTHORIZED
    default_detail = _('User is not active')
    default_code = 'invalid_user'


class WrongPassword(APIException):
    status_code = http_status.HTTP_401_UNAUTHORIZED
    default_detail = _('Wrong user password')
    default_code = 'invalid_credentials'


class UsernameAlreadyUsed(APIException):
    status_code = http_status.HTTP_403_FORBIDDEN
    default_detail = _('Username already in use')
    default_code = 'invalid_username'
