from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework import status as http_status, permissions, exceptions
from rest_framework.pagination import PageNumberPagination
from apps.authentication.models import CustomToken
from rest_framework.renderers import BaseRenderer
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from collections import defaultdict
from django.utils import timezone
from datetime import timedelta
from constance import config


class CustomTokenAuthentication(TokenAuthentication):
    keyword = 'Bearer'
    model = CustomToken

    def authenticate_credentials(self, key):
        user, token = super().authenticate_credentials(key)
        if token.expires_at:
            if token.expires_at < timezone.now():
                raise exceptions.AuthenticationFailed('Token has expired')
            # If token is in use, move the expiration date forward...
            token.expires_at = timezone.now() + timedelta(seconds=config.TOKEN_TTL)
            token.save(update_fields=('expires_at',))
        return token.user, token


class CustomDjangoModelPermissions(permissions.DjangoModelPermissions):
    def __init__(self):
        self.perms_map['GET'] = ['%(app_label)s.view_%(model_name)s']

    def has_permission(self, request, view):
        if getattr(view, '_ignore_model_permissions', False):
            return True

        if not request.user or (
                not request.user.is_authenticated and self.authenticated_users_only):
            return False

        if request.user.is_superuser:
            return True

        queryset = self._queryset(view)
        perms = self.get_required_permissions(request.method, queryset.model)

        custom_permissions = getattr(view, 'custom_permissions', None)
        if custom_permissions:
            perms = custom_permissions

        additional_permissions = getattr(view, 'additional_permissions', None)
        if additional_permissions:
            perms.extend(additional_permissions)

        return request.user.has_perms(perms)


class CustomPageNumberPagination(PageNumberPagination):
    page_size_query_param = 'size'

    def get_paginated_response(self, data):
        return Response(data)


class CsrfExemptSessionAuthentication(SessionAuthentication):
    def enforce_csrf(self, request):
        return


class CustomJsonRenderer(JSONRenderer):
    def render(self, data, accepted_media_type=None, renderer_context=None):
        res = renderer_context.pop('response')
        if res.exception:
            return super().render(data, accepted_media_type, renderer_context)
        if not renderer_context:
            renderer_context = defaultdict()

        # pop not used params
        renderer_context.pop('view', None)
        renderer_context.pop('args', None)
        renderer_context.pop('kwargs', None)
        renderer_context.pop('request', None)

        renderer_context.setdefault('message', 'OK')
        renderer_context.setdefault('status', 'success')
        renderer_context.setdefault('code', http_status.HTTP_200_OK)

        response = {
            'code': renderer_context.get('code'),
            'status': renderer_context.get('status'),
            'message': renderer_context.get('message'),
            'data': data,
        }
        return super().render(response, accepted_media_type, renderer_context)


class XLSXFileMixin(object):
    filename = "export.xlsx"

    def get_filename(self, request=None, *args, **kwargs):
        return self.filename

    def finalize_response(self, request, response, *args, **kwargs):
        response = super().finalize_response(
            request, response, *args, **kwargs
        )
        if (isinstance(response, Response) and response.accepted_renderer.format == "xlsx"):
            response["content-disposition"] = "attachment; filename={}".format(
                self.get_filename(request=request, *args, **kwargs),
            )
        return response


class CSVFileMixin(object):
    filename = "export.csv"

    def get_filename(self, request=None, *args, **kwargs):
        return self.filename

    def finalize_response(self, request, response, *args, **kwargs):
        response = super().finalize_response(
            request, response, *args, **kwargs
        )
        if (isinstance(response, Response) and response.accepted_renderer.format == "csv"):
            response["content-disposition"] = "attachment; filename={}".format(
                self.get_filename(request=request, *args, **kwargs),
            )
        return response


class DOCXFileMixin(object):
    filename = "export.docx"

    def get_filename(self, request=None, *args, **kwargs):
        return self.filename

    def finalize_response(self, request, response, *args, **kwargs):
        response = super().finalize_response(
            request, response, *args, **kwargs
        )
        if (isinstance(response, Response) and response.accepted_renderer.format == "docx"):
            response["content-disposition"] = "attachment; filename={}".format(
                self.get_filename(request=request, *args, **kwargs),
            )
        return response


class PDFFileMixin(object):
    filename = "export.pdf"

    def get_filename(self, request=None, *args, **kwargs):
        return self.filename

    def finalize_response(self, request, response, *args, **kwargs):
        response = super().finalize_response(
            request, response, *args, **kwargs
        )
        if (isinstance(response, Response) and response.accepted_renderer.format == "pdf"):
            response["content-disposition"] = "attachment; filename={}".format(
                self.get_filename(request=request, *args, **kwargs),
            )
        return response


class XLSXRenderer(BaseRenderer):
    media_type = "application/xlsx"
    format = "xlsx"
    render_style = 'binary'

    def render(self, data, media_type=None, renderer_context=None):
        return data


class CSVRenderer(BaseRenderer):
    media_type = "text/csv"
    format = "csv"

    def render(self, data, media_type=None, renderer_context=None):
        return data


class DOCXRenderer(BaseRenderer):
    media_type = "application/docx"
    format = "docx"
    render_style = 'binary'

    def render(self, data, media_type=None, renderer_context=None):
        return data


class PDFRenderer(BaseRenderer):
    media_type = 'application/pdf'
    format = 'pdf'
    charset = None
    render_style = 'binary'

    def render(self, data, media_type=None, renderer_context=None):
        return data


class BinaryRenderer(BaseRenderer):
    media_type = 'application/x-binary'
    charset = None
    render_style = 'binary'

    def render(self, data, media_type=None, renderer_context=None):
        return data


class ZipRenderer(BaseRenderer):
    media_type = 'application/zip'
    format = 'zip'
    render_style = 'binary'

    def render(self, data, media_type=None, renderer_context=None):
        return data
