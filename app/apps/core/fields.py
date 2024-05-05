from django.contrib.gis.db.models import PointField
from apps.core.forms import OSMPointForm


class OSMPointField(PointField):
    form_class = OSMPointForm
