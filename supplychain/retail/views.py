from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout
from django.contrib.auth import login as auth_login
from django.contrib import messages
from django.http import JsonResponse
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.urls import reverse_lazy
from django.db.models import Sum, F, Q, Count
from django.utils import timezone
from datetime import timedelta
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
import plotly.express as px
import json
from django_tables2 import SingleTableView
from .models import Order
from .tables import OrderTable
from .models import *
from .forms import CustomUserCreationForm, RetailerRegistrationForm, CustomAuthenticationForm
from .utils.forecasting import generate_demand_forecast
from .utils.optimization import optimize_delivery_routes

# Authentication Views
def register(request):
    if request.method == 'POST':
        user_form = CustomUserCreationForm(request.POST)
        retailer_form = RetailerRegistrationForm(request.POST)
        
        if user_form.is_valid() and retailer_form.is_valid():
            user = user_form.save()
            retailer = retailer_form.save(commit=False)
            retailer.user = user
            retailer.save()
            
            login(request, user)
            messages.success(request, 'Registration successful!')
            return redirect('dashboard')
    else:
        user_form = CustomUserCreationForm()
        retailer_form = RetailerRegistrationForm()
    
    return render(request, 'retail/registration/register.html', {
        'user_form': user_form,
        'retailer_form': retailer_form
    })

class OrderListView(SingleTableView):
    model = Order
    table_class = OrderTable
    template_name = 'retail/order_list.html'
    
    def get_queryset(self):
        retailer = Retailer.objects.get(user=self.request.user)
        return super().get_queryset().filter(items__product__retailer=retailer).distinct()
    
def user_login(request):
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('dashboard')
    else:
        form = CustomAuthenticationForm()
    return render(request, 'retail/registration/login.html', {'form': form})

def user_logout(request):
    logout(request)
    return redirect('login')

@login_required
def dashboard(request):
    try:
        retailer = Retailer.objects.get(user=request.user)
    except Retailer.DoesNotExist:
        # Redirect to profile completion if retailer doesn't exist
        messages.warning(request, 'Please complete your retailer profile')
        return redirect('create_retailer_profile')
    
    # Rest of your dashboard logic
    total_products = Product.objects.filter(retailer=retailer).count()
    low_stock_products = Product.objects.filter(
        retailer=retailer,
        current_stock__lt=F('min_stock_level')
    ).count()
    
    recent_orders = Order.objects.filter(
        items__product__retailer=retailer
    ).distinct().order_by('-order_date')[:5]
    
    return render(request, 'retail/dashboard.html', {
        'retailer': retailer,
        'total_products': total_products,
        'low_stock_products': low_stock_products,
        'recent_orders': recent_orders,
    })

# Inventory Management Views
@login_required
def inventory_list(request):
    try:
        retailer = Retailer.objects.get(user=request.user)
        products = Product.objects.filter(retailer=retailer).select_related('retailer').prefetch_related('inventory_set')
        
        # Debug print (remove in production)
        print(f"Found {products.count()} products for {retailer.company_name}")
        for p in products:
            print(f"{p.name} - Inventory: {p.inventory_set.count()} records")

        # Calculate metrics
        low_stock_count = products.filter(current_stock__lt=F('min_stock_level')).count()
        
        return render(request, 'retail/inventory.html', {
            'products': products,
            'retailer': retailer,
            'low_stock_count': low_stock_count,
            'total_products': products.count()
        })
        
    except Retailer.DoesNotExist:
        messages.error(request, "Retailer profile not found")
        return redirect('create_retailer_profile')
# @login_required
# def inventory_list(request):
#     retailer = get_object_or_404(Retailer, user=request.user)
#     products = Product.objects.filter(retailer=retailer).order_by('name')
    
#     # Calculate metrics for the dashboard
#     low_stock_count = products.filter(current_stock__lt=F('min_stock_level')).count()
#     total_products = products.count()
    
#     # Get category distribution
#     category_distribution = products.values('category').annotate(count=Count('id'))
#     category_labels = [dict(Product.CATEGORY_CHOICES).get(item['category']) for item in category_distribution]
#     category_counts = [item['count'] for item in category_distribution]
    
#     # Check for low stock items
#     for product in products:
#         product.is_low_stock = product.current_stock < product.min_stock_level
    
#     return render(request, 'retail/inventory.html', {
#         'products': products,
#         'retailer': retailer,
#         'low_stock_count': low_stock_count,
#         'total_products': total_products,
#         'category_labels': json.dumps(category_labels),
#         'category_counts': json.dumps(category_counts),
#     })

@login_required
def add_inventory(request, product_id):
    product = get_object_or_404(Product, id=product_id, retailer__user=request.user)
    
    if request.method == 'POST':
        form = InventoryUpdateForm(request.POST)
        if form.is_valid():
            # Get or create inventory record
            inventory, created = Inventory.objects.get_or_create(
                product=product,
                warehouse=form.cleaned_data['warehouse'],
                defaults={'quantity': form.cleaned_data['quantity']}
            )
            
            if not created:
                inventory.quantity = form.cleaned_data['quantity']
                inventory.save()
            
            # Update product's total stock
            product.current_stock = product.inventory_set.aggregate(
                total=Sum('quantity')
            )['total'] or 0
            product.save()
            
            messages.success(request, "Inventory updated successfully!")
            return redirect('inventory_list')
    else:
        form = InventoryUpdateForm()
    
    return render(request, 'retail/add_inventory.html', {
        'product': product,
        'form': form
    })

@login_required
def inventory_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id, retailer__user=request.user)
    inventory = Inventory.objects.filter(product=product)
    
    # Get sales history for forecasting
    sales_history = OrderItem.objects.filter(
        product=product,
        order__status='DELIVERED'
    ).values('order__order_date').annotate(quantity=Sum('quantity')).order_by('order__order_date')
    
    # Generate forecast if requested
    if request.method == 'POST' and 'generate_forecast' in request.POST:
        forecast = generate_demand_forecast(product)
        messages.success(request, f"Forecast generated: {forecast.forecasted_quantity} units needed for {forecast.forecast_period}")
        return redirect('inventory_detail', product_id=product.id)
    
    # Get existing forecasts
    forecasts = DemandForecast.objects.filter(product=product).order_by('-forecast_date')
    
    context = {
        'product': product,
        'inventory': inventory,
        'sales_history': sales_history,
        'forecasts': forecasts,
    }
    
    return render(request, 'retail/inventory_detail.html', context)

# Order Management Views
@login_required
def order_list(request):
    retailer = get_object_or_404(Retailer, user=request.user)
    orders = Order.objects.filter(
        items__product__retailer=retailer
    ).distinct().order_by('-order_date')
    
    # Filtering
    status_filter = request.GET.get('status')
    if status_filter:
        orders = orders.filter(status=status_filter)
    
    return render(request, 'retail/order_list.html', {
        'orders': orders,
        'status_filter': status_filter
    })

@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, items__product__retailer__user=request.user)
    
    # Check if we need to optimize delivery
    if order.status == 'PROCESSING' and not hasattr(order, 'deliveryroute'):
        # Auto-optimize delivery if not already done
        optimize_delivery_routes([order])
    
    return render(request, 'retail/order_detail.html', {'order': order})

@login_required
def update_order_status(request, order_id):
    order = get_object_or_404(Order, id=order_id, items__product__retailer__user=request.user)
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(Order.ORDER_STATUS).keys():
            order.status = new_status
            order.save()
            
            # If status is shipped, create delivery route if not exists
            if new_status == 'SHIPPED' and not hasattr(order, 'deliveryroute'):
                optimize_delivery_routes([order])
            
            messages.success(request, f"Order status updated to {order.get_status_display()}")
        else:
            messages.error(request, "Invalid status")
    
    return redirect('order_detail', order_id=order.id)

# Analytics Views
@login_required
def predictive_analytics(request):
    retailer = get_object_or_404(Retailer, user=request.user)
    
    # Get products with sales history
    products = Product.objects.filter(
        retailer=retailer,
        orderitem__order__status='DELIVERED'
    ).distinct()
    
    # Generate forecasts for all products if requested
    if request.method == 'POST' and 'generate_all_forecasts' in request.POST:
        for product in products:
            generate_demand_forecast(product)
        messages.success(request, "Forecasts generated for all products!")
        return redirect('predictive_analytics')
    
    # Get existing forecasts
    forecasts = DemandForecast.objects.filter(product__retailer=retailer).order_by('-forecast_date')
    
    # Calculate forecast accuracy where actual data exists
    for forecast in forecasts:
        if forecast.actual_quantity:
            forecast.accuracy = (1 - abs(forecast.forecasted_quantity - forecast.actual_quantity) / forecast.actual_quantity) * 100
    
    context = {
        'products': products,
        'forecasts': forecasts,
    }
    
    return render(request, 'retail/predictive_analytics.html', context)

# Delivery Optimization Views
@login_required
def delivery_optimization(request):
    retailer = get_object_or_404(Retailer, user=request.user)
    
    # Get pending deliveries
    pending_orders = Order.objects.filter(
        items__product__retailer=retailer,
        status__in=['PROCESSING', 'SHIPPED']
    ).distinct()
    
    # Optimize routes if requested
    if request.method == 'POST' and 'optimize_routes' in request.POST:
        selected_orders = request.POST.getlist('selected_orders')
        orders_to_optimize = pending_orders.filter(id__in=selected_orders)
        
        if orders_to_optimize:
            optimize_delivery_routes(orders_to_optimize)
            messages.success(request, f"Optimized routes for {len(orders_to_optimize)} orders!")
        else:
            messages.warning(request, "No orders selected for optimization")
        
        return redirect('delivery_optimization')
    
    context = {
        'pending_orders': pending_orders,
    }
    
    return render(request, 'retail/delivery_optimization.html', context)

# API Views
@login_required
def order_tracking_api(request, tracking_number):
    order = get_object_or_404(Order, tracking_number=tracking_number)
    
    # Basic order info
    data = {
        'order_id': order.id,
        'customer': order.customer.name,
        'status': order.get_status_display(),
        'order_date': order.order_date.strftime("%Y-%m-%d %H:%M"),
        'estimated_delivery': order.estimated_delivery.strftime("%Y-%m-%d %H:%M") if order.estimated_delivery else None,
        'total_amount': float(order.total_amount),
        'items': [],
    }
    
    # Add items
    for item in order.items.all():
        data['items'].append({
            'product': item.product.name,
            'quantity': item.quantity,
            'price': float(item.price),
            'subtotal': float(item.quantity * item.price),
        })
    
    # Add delivery info if available
    if hasattr(order, 'deliveryroute'):
        route = order.deliveryroute
        data['delivery'] = {
            'driver': route.driver_name,
            'contact': route.driver_contact,
            'vehicle': route.vehicle_type,
            'route_status': route.status,
            'optimized_route': json.loads(route.optimized_route),
        }
    
    return JsonResponse(data)

# Customer-facing Views
def track_order(request):
    if request.method == 'POST':
        tracking_number = request.POST.get('tracking_number')
        try:
            order = Order.objects.get(tracking_number=tracking_number)
            return render(request, 'retail/order_tracking.html', {'order': order})
        except Order.DoesNotExist:
            messages.error(request, "Order not found. Please check your tracking number.")
    
    return render(request, 'retail/order_tracking.html')

@login_required
def create_retailer_profile(request):
    if request.method == 'POST':
        form = RetailerRegistrationForm(request.POST)
        if form.is_valid():
            retailer = form.save(commit=False)
            retailer.user = request.user
            retailer.save()
            messages.success(request, 'Retailer profile created successfully!')
            return redirect('dashboard')
    else:
        form = RetailerRegistrationForm()
    
    return render(request, 'retail/create_retailer_profile.html', {
        'form': form
    })
