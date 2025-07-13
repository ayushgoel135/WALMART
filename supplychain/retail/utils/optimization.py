import json
from datetime import timedelta
from geopy.distance import geodesic
from django.db.models import Q
from ..models import DeliveryRoute, Warehouse, Order, Inventory

def optimize_delivery_routes(orders):
    """
    Optimize delivery routes for a set of orders
    Args:
        orders: QuerySet of Order objects
    Returns:
        list: Created DeliveryRoute instances
    """
    if not orders:
        return []
    
    routes = []
    retailer = orders[0].items.first().product.retailer
    warehouses = Warehouse.objects.filter(retailer=retailer)
    
    for order in orders:
        if hasattr(order, 'deliveryroute'):
            continue
            
        best_warehouse = _find_optimal_warehouse(order, warehouses)
        if best_warehouse:
            route = _create_delivery_route(order, best_warehouse)
            routes.append(route)
    
    return routes

def _find_optimal_warehouse(order, warehouses):
    """Find the best warehouse to fulfill an order"""
    best_warehouse = None
    min_distance = float('inf')
    
    for warehouse in warehouses:
        if _can_fulfill_order(order, warehouse):
            distance = _calculate_distance(order, warehouse)
            if distance < min_distance:
                best_warehouse = warehouse
                min_distance = distance
    
    return best_warehouse

def _can_fulfill_order(order, warehouse):
    """Check if warehouse can fulfill all items in order"""
    for item in order.items.all():
        inventory = Inventory.objects.filter(
            product=item.product,
            warehouse=warehouse
        ).first()
        if not inventory or inventory.quantity < item.quantity:
            return False
    return True

def _calculate_distance(order, warehouse):
    """Calculate approximate delivery distance (simplified)"""
    # In production, use geocoding APIs for real addresses
    if warehouse.latitude and warehouse.longitude:
        # Mock customer location (in reality, geocode shipping address)
        cust_lat = warehouse.latitude + 0.01
        cust_lng = warehouse.longitude + 0.01
        return geodesic(
            (warehouse.latitude, warehouse.longitude),
            (cust_lat, cust_lng)
        ).miles
    return float('inf')

def _create_delivery_route(order, warehouse):
    """Create and save delivery route"""
    # Update inventory and fulfillment info
    for item in order.items.all():
        item.fulfilled_from = warehouse
        item.save()
        
        # Reduce inventory
        inventory = Inventory.objects.get(
            product=item.product,
            warehouse=warehouse
        )
        inventory.quantity -= item.quantity
        inventory.save()
    
    # Create route data (simplified)
    route_data = {
        'waypoints': [
            {
                'lat': warehouse.latitude,
                'lng': warehouse.longitude,
                'name': warehouse.name,
                'type': 'warehouse'
            },
            {
                'lat': warehouse.latitude + 0.01,  # Mock customer location
                'lng': warehouse.longitude + 0.01,
                'name': f"Customer #{order.customer.id}",
                'type': 'customer'
            }
        ],
        'total_distance': _calculate_distance(order, warehouse),
        'estimated_time': _calculate_distance(order, warehouse) * 3  # 3 minutes per mile
    }
    
    # Create and return route
    return DeliveryRoute.objects.create(
        order=order,
        driver_name="Auto-assigned",
        driver_contact="555-0100",
        vehicle_type="Van",
        start_time=order.order_date + timedelta(hours=1),
        optimized_route=json.dumps(route_data),
        status='PENDING'
    )