import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from datetime import timedelta
from django.db.models import Sum
from ..models import DemandForecast, OrderItem

def generate_demand_forecast(product, period='weekly'):
    """
    Generate demand forecast for a product using machine learning
    Args:
        product: Product instance
        period: Forecast period ('weekly' or 'monthly')
    Returns:
        DemandForecast: Saved forecast instance
    """
    # Get historical sales data
    sales_data = OrderItem.objects.filter(
        product=product,
        order__status='DELIVERED'
    ).values('order__order_date').annotate(quantity=Sum('quantity')).order_by('order__order_date')
    
    # Handle empty data
    if not sales_data:
        return _create_simple_forecast(product, period)
    
    # Prepare DataFrame
    df = pd.DataFrame(list(sales_data))
    df.columns = ['date', 'sales']
    df['date'] = pd.to_datetime(df['date'])
    
    # Feature engineering
    df = _create_features(df)
    
    # Handle insufficient data
    if len(df) < 30:
        return _create_simple_forecast(product, period)
    
    # Train-test split
    X = df.drop(['date', 'sales'], axis=1)
    y = df['sales']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)
    
    # Train model
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    
    # Generate forecast
    forecast_days = 7 if period == 'weekly' else 30
    forecast = _generate_forecast_values(model, df, forecast_days)
    
    # Create and save forecast
    return DemandForecast.objects.create(
        product=product,
        forecast_period=period,
        forecasted_quantity=int(forecast.sum()),
        confidence_level=_calculate_confidence(model, X_test, y_test)
    )

def _create_features(df):
    """Create time series features"""
    df = df.set_index('date').asfreq('D').fillna(0).reset_index()
    df['day_of_week'] = df['date'].dt.dayofweek
    df['month'] = df['date'].dt.month
    df['day_of_year'] = df['date'].dt.dayofyear
    df['lag_7'] = df['sales'].shift(7)
    df['lag_14'] = df['sales'].shift(14)
    df['rolling_7_mean'] = df['sales'].shift(1).rolling(7).mean()
    return df.dropna()

def _generate_forecast_values(model, df, days):
    """Generate forecast values for given days"""
    forecast = []
    last_date = df['date'].max()
    
    for i in range(1, days+1):
        date = last_date + timedelta(days=i)
        features = {
            'day_of_week': date.dayofweek,
            'month': date.month,
            'day_of_year': date.dayofyear,
            'lag_7': forecast[i-2] if i > 1 else df['sales'].iloc[-1],
            'lag_14': forecast[i-8] if i > 7 else df['sales'].iloc[-7],
            'rolling_7_mean': np.mean(forecast[max(0,i-7):i] + list(df['sales'].iloc[-(7-i):]))
        }
        forecast.append(model.predict(pd.DataFrame([features]))[0])
    
    return forecast

def _calculate_confidence(model, X_test, y_test):
    """Calculate model confidence score"""
    score = model.score(X_test, y_test)
    return min(95, max(70, score * 100))  # Cap between 70-95%

def _create_simple_forecast(product, period):
    """Fallback forecast for insufficient data"""
    return DemandForecast.objects.create(
        product=product,
        forecast_period=period,
        forecasted_quantity=max(product.min_stock_level - product.current_stock, 0),
        confidence_level=50.0
    )