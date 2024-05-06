#
#       |               |      |                              |
#    _` |   _` |   __|  __ \   __ \    _ \    _` |   __|   _` |     __ \   |   |
#   (   |  (   | \__ \  | | |  |   |  (   |  (   |  |     (   |     |   |  |   |
#  \__,_| \__,_| ____/ _| |_| _.__/  \___/  \__,_| _|    \__,_| _|  .__/  \__, |
#                                                                  _|     ____/
#

from django.template.context_processors import csrf
from django.template.loader import render_to_string
from jet.dashboard.dashboard import Dashboard
from . import dashboard_modules as modules
from .forms import DashboardFilterForm
from jet.utils import context_to_dict


# Tricky part here...
# <columns> property modified, previously: <int>, now: <tuple>.
# Made so for the sake of dynamic dashboard layout, Like:
# columns = (2, 4, 3)
# +-----------------------------------+
# |        1        |        2        |
# |-----------------------------------|
# |    1   |    2   |    3   |    4   |
# |-----------------------------------|
# |     1     |     2     |     3     |
# +-----------------------------------+
# If you want to switch to default dasboard layout,
# change the <column> property to some integer value.
# and comment the <self.set_modules_columns> function call
# inside the <init_with_context> function.
# The template is also modified in /templates/custom_dashboard.html.
# If you wish to switch back to default layout, change the template too.
# There is commented original columns rendering loop in the template.
# Read comments in /templates/custom_dashboard.html template.
class CustomIndexDashboard(Dashboard):
    columns = (3,)

    class Media:
        css = ('css/styles.css',)
        js = ('js/apexcharts.min.js',)

    def init_with_context(self, context):
        request = self.context.get('request')
        if not request or not request.user:
            return
        self.children.append(modules.CustomerTotal())
        self.children.append(modules.PostTotalModule())
        self.children.append(modules.NewCustomerStatisticsModule())
        # self.children.append(modules.PostStatisticsModule())
        # If you want to switch back to default dashboard layout,
        # comment the below <self.set_modules_columns> function call.
        self.set_modules_columns()

    def render(self):
        context = context_to_dict(self.context)
        context.update({
            'columns': self.columns,
            # 'columns': range(self.columns),
            'modules': self.modules,
            'app_label': self.app_label,
            # Number of modules that are didn't fit into columns layout...
            'overflow': getattr(self, 'overflow', 0),
        })
        context.update(csrf(context['request']))
        filter_form = DashboardFilterForm()
        context.update({'filter_form': filter_form})
        # IMPORTANT NOTE:
        # There is template named /templates/dashboard_modules/filter_module.html
        # It contains the Js code responsible for calling the
        # functions that are loading data into charts.
        return render_to_string('dashboard/custom_dashboard.html', context)

    def render_tools(self):
        context = context_to_dict(self.context)
        context.update({
            'app_label': self.app_label,
        })
        context.update(csrf(context['request']))
        return render_to_string('dashboard/custom_dashboard_tools.html', context)

    # Set the order (row) and column for each module
    # in self.children list.
    def set_modules_columns(self):
        counter = 0
        order = 0
        for cols in self.columns:
            for index in range(cols):
                # if modules count is less than
                # <columns> prperty sum, stop iteration.
                if counter >= len(self.children):
                    return
                self.children[counter].column = index
                self.children[counter].order = order
                counter += 1
            order += 1
        if counter < len(self.children):
            # Also tricky part, I pass the extra variablle <overflow> to context,
            # if modules count is more than sum of <columns> property.
            # <overflow> is the range of extra rows (order).
            # So it became possible to render the modules,
            # that exceeded the sum of <columns> property.
            cols = self.columns[-1]
            overflow_order_start = order
            index = 0
            # Here I set the <order> (row) and <column> attrs of extra modules.
            for module in self.children[counter:]:
                module.order = order + int(index / cols)
                module.column = index % cols
                index += 1
            self.overflow = range(overflow_order_start, order + int(index / cols) + 1)
