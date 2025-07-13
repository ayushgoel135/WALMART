from django.contrib import admin
from .models import *

@admin.register(Retailer)
class RetailerAdmin(admin.ModelAdmin):
    list_display = ('company_name', 'user', 'contact_number')
    search_fields = ('company_name', 'user__username')

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'sku', 'category', 'current_stock')
    list_filter = ('category',)
    search_fields = ('name', 'sku')

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'status', 'total_amount')
    list_filter = ('status',)
    raw_id_fields = ('customer',)

admin.site.register([Warehouse, Inventory, Customer, DeliveryRoute, DemandForecast])