from django.utils.translation import gettext_lazy as _
from jet.dashboard.modules import DashboardModule
from django.utils.dates import WEEKDAYS_ABBR
from django.utils.formats import date_format
from datetime import timedelta, datetime
from django.db.models import Count, Avg
from apps.post.models import Post
from django.urls import reverse


class NewCustomerStatisticsModule(DashboardModule):
    template = 'dashboard/modules/new_customer_statistics.html'
    deletable = False
    collapsible = False
    draggable = False


class AveragePostModule(DashboardModule):
    template = 'dashboard/modules/average_post_statistics.html'
    deletable = False
    collapsible = False
    draggable = False


class ActiveCustomerStatisticsModule(DashboardModule):
    template = 'dashboard/modules/active_customer_statistics.html'
    deletable = False
    collapsible = False
    draggable = False


class CustomerTotal(DashboardModule):
    template = 'dashboard/modules/customer_total.html'
    deletable = False
    collapsible = False
    draggable = False


class PointsStatistics(DashboardModule):
    template = 'dashboard/modules/point_statistics.html'
    deletable = False
    collapsible = False
    draggable = False


class PostStatisticsModule(DashboardModule):
    template = 'dashboard/modules/post_statistics.html'
    deletable = False
    collapsible = False
    draggable = False


class ActivityModule(DashboardModule):
    title = _('Posts activity')
    template = 'dashboard/modules/activity_info.html'
    deletable = False
    collapsible = False
    draggable = False

    def init_with_context(self, context):
        context = context if context else {}
        days_count = 366
        date_end = datetime.today().date()
        date_start = date_end - timedelta(days=days_count)
        qs = Post.objects.filter(created_at__date__gte=date_start, created_at__date__lte=date_end).order_by(
            'created_at__date')
        qs = qs.values('created_at__date').annotate(count=Count('id')).values('created_at__date', 'count')
        posts_dict = {d['created_at__date']: d['count'] for d in qs}
        res = {0: [], 1: [], 2: [], 3: [], 4: [], 5: [], 6: []}
        info = Post._meta.app_label, Post._meta.model_name
        post_url = reverse('admin:%s_%s_changelist' % info)
        # Shift the calendar a little...
        for i in range(date_start.weekday()):
            res[i].append({'x': '', 'y': 0})
        week_days = [_(WEEKDAYS_ABBR[i]) for i in range(7)]
        for i in range(days_count + 1):
            date = date_start + timedelta(days=i)
            res[date.weekday()].append(
                {
                    'x': date_format(date, format='j F Y', use_l10n=True),
                    'y': posts_dict.get(date, 0),
                    'iso_date': date.isoformat(),
                }
            )
        context.update({'activity_data': res, 'post_url': post_url, 'week_days': week_days})
        return context


class PointsEarnedModule(DashboardModule):
    template = 'dashboard/modules/customer_points_earned.html'
    deletable = False
    collapsible = False
    draggable = False


class PointsUsedModule(DashboardModule):
    # title = _('Revenue statistics')
    template = 'dashboard/modules/customer_points_used.html'
    deletable = False
    collapsible = False
    draggable = False
