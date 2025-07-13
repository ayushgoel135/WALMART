import django_tables2 as tables
from .models import Order

class OrderTable(tables.Table):
    actions = tables.TemplateColumn(
        template_name='retail/order_actions_column.html',
        orderable=False
    )
    
    class Meta:
        model = Order
        template_name = "django_tables2/bootstrap5.html"
        fields = ('id', 'customer', 'order_date', 'status', 'total_amount')
        attrs = {'class': 'table table-striped table-bordered'}