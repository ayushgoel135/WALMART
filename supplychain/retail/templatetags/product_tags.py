from django import template
from ..models import Product

register = template.Library()

@register.filter
def get_category_label(value):
    return dict(Product.CATEGORY_CHOICES).get(value, value)