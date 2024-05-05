from django_filters import rest_framework as django_filters
from api.statistics.choices import PeriodChoice
from django.contrib.auth import get_user_model
from apps.post.models import Post

UserModel = get_user_model()


class DateRangeFilter(django_filters.FilterSet):
    date_from = django_filters.DateFilter(field_name='created_at__date', lookup_expr='gte')
    date_to = django_filters.DateFilter(field_name='created_at__date', lookup_expr='lte')


class PostReportFilter(DateRangeFilter):
    period = django_filters.ChoiceFilter(choices=PeriodChoice.choices, method='period_filter')

    class Meta:
        model = Post
        fields = ()

    def period_filter(self, queryset, name, value):
        return queryset


class CustomerFilter(django_filters.FilterSet):
    date_from = django_filters.DateFilter(field_name='date_joined__date', lookup_expr='gte')
    date_to = django_filters.DateFilter(field_name='date_joined__date', lookup_expr='lte')

    class Meta:
        model = UserModel
        fields = ()
