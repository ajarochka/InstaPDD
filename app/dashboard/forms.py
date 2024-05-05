from django.contrib.admin.widgets import AdminDateWidget
from django.utils.translation import gettext_lazy as _
from datetime import datetime, timedelta
from django import forms


class DashboardFilterForm(forms.Form):
    date_from = forms.DateField(label='', widget=AdminDateWidget(attrs={'placeholder': _('From date')}))
    date_to = forms.DateField(label='', widget=AdminDateWidget(attrs={'placeholder': _('To date')}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.initial['date_from'] = datetime.today().date() - timedelta(days=30)
        self.initial['date_to'] = datetime.today().date()
        # self.fields['date_from'].initial = datetime.today().date() - timedelta(days=7)
        # self.fields['date_to'].initial = datetime.today().date()
