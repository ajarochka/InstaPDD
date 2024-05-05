from django.contrib.gis import forms


class OSMPointForm(forms.PointField):
    widget = forms.OSMWidget
