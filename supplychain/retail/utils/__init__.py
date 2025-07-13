# Expose key functions at package level
from .analytics import (
    calculate_inventory_turnover,
    analyze_sales_trends,
    calculate_forecast_accuracy
)
from .forecasting import generate_demand_forecast
from .optimization import optimize_delivery_routes

__all__ = [
    'calculate_inventory_turnover',
    'analyze_sales_trends',
    'calculate_forecast_accuracy',
    'generate_demand_forecast',
    'optimize_delivery_routes'
]