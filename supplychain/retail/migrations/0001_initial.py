# Generated by Django 5.2.4 on 2025-07-13 10:56

import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('sku', models.CharField(max_length=50, unique=True)),
                ('category', models.CharField(choices=[('ELEC', 'Electronics'), ('CLOTH', 'Clothing'), ('FOOD', 'Grocery & Food'), ('HOME', 'Home & Kitchen'), ('OTHER', 'Other')], max_length=10)),
                ('description', models.TextField(blank=True)),
                ('price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('current_stock', models.PositiveIntegerField(default=0)),
                ('min_stock_level', models.PositiveIntegerField(default=10)),
                ('lead_time_days', models.PositiveIntegerField(default=7)),
                ('image', models.ImageField(blank=True, null=True, upload_to='products/')),
                ('last_updated', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Customer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('email', models.EmailField(max_length=254)),
                ('phone', models.CharField(max_length=20)),
                ('address', models.TextField()),
                ('registration_date', models.DateTimeField(auto_now_add=True)),
                ('user', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order_date', models.DateTimeField(auto_now_add=True)),
                ('status', models.CharField(choices=[('PENDING', 'Pending'), ('PROCESSING', 'Processing'), ('SHIPPED', 'Shipped'), ('OUT_FOR_DELIVERY', 'Out for Delivery'), ('DELIVERED', 'Delivered'), ('CANCELLED', 'Cancelled')], default='PENDING', max_length=20)),
                ('total_amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('shipping_address', models.TextField()),
                ('estimated_delivery', models.DateTimeField(blank=True, null=True)),
                ('tracking_number', models.CharField(blank=True, max_length=50, unique=True)),
                ('delivery_notes', models.TextField(blank=True)),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='retail.customer')),
            ],
        ),
        migrations.CreateModel(
            name='DeliveryRoute',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('driver_name', models.CharField(max_length=100)),
                ('driver_contact', models.CharField(max_length=20)),
                ('vehicle_type', models.CharField(max_length=50)),
                ('start_time', models.DateTimeField()),
                ('end_time', models.DateTimeField(blank=True, null=True)),
                ('optimized_route', models.TextField()),
                ('actual_route', models.TextField(blank=True)),
                ('status', models.CharField(default='PENDING', max_length=20)),
                ('order', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='retail.order')),
            ],
        ),
        migrations.CreateModel(
            name='DemandForecast',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('forecast_date', models.DateTimeField(auto_now_add=True)),
                ('forecast_period', models.CharField(max_length=20)),
                ('forecasted_quantity', models.PositiveIntegerField()),
                ('confidence_level', models.DecimalField(decimal_places=2, max_digits=5)),
                ('actual_quantity', models.PositiveIntegerField(blank=True, null=True)),
                ('accuracy', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='retail.product')),
            ],
        ),
        migrations.CreateModel(
            name='Retailer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('company_name', models.CharField(max_length=100)),
                ('address', models.TextField()),
                ('contact_number', models.CharField(max_length=20)),
                ('registration_date', models.DateTimeField(auto_now_add=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='product',
            name='retailer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='retail.retailer'),
        ),
        migrations.CreateModel(
            name='Supplier',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('contact_person', models.CharField(max_length=100)),
                ('email', models.EmailField(max_length=254)),
                ('phone', models.CharField(max_length=20)),
                ('lead_time', models.PositiveIntegerField(help_text='Average lead time in days')),
                ('reliability_score', models.DecimalField(decimal_places=1, default=5.0, max_digits=3)),
                ('retailer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='retail.retailer')),
            ],
        ),
        migrations.CreateModel(
            name='Warehouse',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('location', models.CharField(max_length=100)),
                ('latitude', models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True)),
                ('longitude', models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True)),
                ('capacity', models.PositiveIntegerField()),
                ('current_occupancy', models.PositiveIntegerField(default=0)),
                ('retailer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='retail.retailer')),
            ],
        ),
        migrations.CreateModel(
            name='OrderItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.PositiveIntegerField(validators=[django.core.validators.MinValueValidator(1)])),
                ('price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='retail.order')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='retail.product')),
                ('fulfilled_from', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='retail.warehouse')),
            ],
        ),
        migrations.CreateModel(
            name='Inventory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.PositiveIntegerField(default=0)),
                ('last_restocked', models.DateTimeField(auto_now=True)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='retail.product')),
                ('warehouse', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='retail.warehouse')),
            ],
            options={
                'unique_together': {('product', 'warehouse')},
            },
        ),
    ]
