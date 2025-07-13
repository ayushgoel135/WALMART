from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import MinValueValidator

class Retailer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    company_name = models.CharField(max_length=100)
    address = models.TextField()
    contact_number = models.CharField(max_length=20)
    registration_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.company_name

class Product(models.Model):
    CATEGORY_CHOICES = [
        ('ELEC', 'Electronics'),
        ('CLOTH', 'Clothing'),
        ('FOOD', 'Grocery & Food'),
        ('HOME', 'Home & Kitchen'),
        ('OTHER', 'Other'),
    ]
    
    retailer = models.ForeignKey(Retailer, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    sku = models.CharField(max_length=50, unique=True)
    category = models.CharField(max_length=10, choices=CATEGORY_CHOICES)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    current_stock = models.PositiveIntegerField(default=0)
    min_stock_level = models.PositiveIntegerField(default=10)
    lead_time_days = models.PositiveIntegerField(default=7)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.sku})"

class Warehouse(models.Model):
    retailer = models.ForeignKey(Retailer, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    capacity = models.PositiveIntegerField()
    current_occupancy = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.name} - {self.location}"

class Inventory(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=0)
    last_restocked = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('product', 'warehouse')

    def __str__(self):
        return f"{self.product.name} at {self.warehouse.name}"

class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    address = models.TextField()
    registration_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Order(models.Model):
    ORDER_STATUS = [
        ('PENDING', 'Pending'),
        ('PROCESSING', 'Processing'),
        ('SHIPPED', 'Shipped'),
        ('OUT_FOR_DELIVERY', 'Out for Delivery'),
        ('DELIVERED', 'Delivered'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    order_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=ORDER_STATUS, default='PENDING')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    shipping_address = models.TextField()
    estimated_delivery = models.DateTimeField(null=True, blank=True)
    tracking_number = models.CharField(max_length=50, unique=True, blank=True)
    delivery_notes = models.TextField(blank=True)

    def __str__(self):
        return f"Order #{self.id} - {self.customer.name}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    price = models.DecimalField(max_digits=10, decimal_places=2)
    fulfilled_from = models.ForeignKey(Warehouse, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.quantity} x {self.product.name} for order #{self.order.id}"

class DeliveryRoute(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE)
    driver_name = models.CharField(max_length=100)
    driver_contact = models.CharField(max_length=20)
    vehicle_type = models.CharField(max_length=50)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True, blank=True)
    optimized_route = models.TextField()  # JSON stored as text
    actual_route = models.TextField(blank=True)  # For tracking actual path taken
    status = models.CharField(max_length=20, default='PENDING')

    def __str__(self):
        return f"Route for Order #{self.order.id}"

class DemandForecast(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    forecast_date = models.DateTimeField(auto_now_add=True)
    forecast_period = models.CharField(max_length=20)  # e.g., 'weekly', 'monthly'
    forecasted_quantity = models.PositiveIntegerField()
    confidence_level = models.DecimalField(max_digits=5, decimal_places=2)  # Percentage
    actual_quantity = models.PositiveIntegerField(null=True, blank=True)  # To be filled later
    accuracy = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return f"{self.product.name} forecast for {self.forecast_period}"

class Supplier(models.Model):
    retailer = models.ForeignKey(Retailer, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    contact_person = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    lead_time = models.PositiveIntegerField(help_text="Average lead time in days")
    reliability_score = models.DecimalField(max_digits=3, decimal_places=1, default=5.0)

    def __str__(self):
        return self.name