import pandas as pd
import numpy as np
from sklearn.metrics import mean_absolute_error, mean_squared_error
from statsmodels.tsa.seasonal import seasonal_decompose
from django.db.models import Sum, F
from ..models import OrderItem

def calculate_inventory_turnover(sales_quantity, average_inventory):
    """
    Calculate inventory turnover ratio
    Args:
        sales_quantity: Total quantity sold in period
        average_inventory: Average inventory level during period
    Returns:
        float: Inventory turnover ratio
    """
    return sales_quantity / average_inventory if average_inventory != 0 else 0

def analyze_sales_trends(sales_data, period='M'):
    """
    Perform time series decomposition on sales data
    Args:
        sales_data: DataFrame with 'date' and 'sales' columns
        period: Seasonality period
    Returns:
        dict: Decomposition results or None if insufficient data
    """
    if len(sales_data) < 2:
        return None
        
    try:
        sales_data = sales_data.set_index('date').asfreq('D').fillna(0)
        result = seasonal_decompose(sales_data['sales'], model='additive', period=12)
        return {
            'trend': result.trend,
            'seasonal': result.seasonal,
            'residual': result.resid
        }
    except Exception as e:
        print(f"Decomposition error: {e}")
        return None

def calculate_forecast_accuracy(actual, forecast):
    """
    Calculate multiple forecast accuracy metrics
    Args:
        actual: Array of actual values
        forecast: Array of forecasted values
    Returns:
        dict: Accuracy metrics (MAE, MSE, RMSE, MAPE)
    """
    if len(actual) == 0 or len(forecast) == 0:
        return None
        
    actual = np.array(actual)
    forecast = np.array(forecast)
    
    metrics = {
        'mae': mean_absolute_error(actual, forecast),
        'mse': mean_squared_error(actual, forecast),
        'rmse': np.sqrt(mean_squared_error(actual, forecast)),
        'mape': np.mean(np.abs((actual - forecast) / actual)) * 100,
    }
    
    return metrics

def get_product_performance(product_id):
    """
    Calculate key performance metrics for a product
    Args:
        product_id: ID of product to analyze
    Returns:
        dict: Performance metrics
    """
  
    
    # Get sales data
    sales_data = OrderItem.objects.filter(
        product_id=product_id,
        order__status='DELIVERED'
    ).annotate(
        date=F('order__order_date')
    ).values('date', 'quantity')
    
    # Convert to DataFrame
    df = pd.DataFrame(list(sales_data))
    
    if df.empty:
        return None
    
    # Calculate metrics
    total_sold = df['quantity'].sum()
    avg_monthly = df.resample('M', on='date')['quantity'].sum().mean()
    
    return {
        'total_sold': total_sold,
        'avg_monthly': avg_monthly,
        'sales_trend': analyze_sales_trends(df)
    }