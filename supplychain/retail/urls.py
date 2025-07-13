from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .views import OrderListView

urlpatterns = [
    # Authentication
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
     path('password_reset/', 
         auth_views.PasswordResetView.as_view(
             template_name='retail/registration/password_reset.html',
             email_template_name='retail/registration/password_reset_email.html',
             subject_template_name='retail/registration/password_reset_subject.txt'
         ), 
         name='password_reset'),
    path('password_reset/done/', 
         auth_views.PasswordResetDoneView.as_view(
             template_name='retail/registration/password_reset_done.html'
         ), 
         name='password_reset_done'),
    path('reset/<uidb64>/<token>/', 
         auth_views.PasswordResetConfirmView.as_view(
             template_name='retail/registration/password_reset_confirm.html'
         ), 
         name='password_reset_confirm'),
    path('reset/done/', 
         auth_views.PasswordResetCompleteView.as_view(
             template_name='retail/registration/password_reset_complete.html'
         ), 
         name='password_reset_complete'),

    path('create-retailer-profile/', views.create_retailer_profile, name='create_retailer_profile'),
    
    # Dashboard
    path('', views.dashboard, name='dashboard'),
    
    # Inventory
    path('inventory/', views.inventory_list, name='inventory_list'),
    path('inventory/<int:product_id>/', views.inventory_detail, name='inventory_detail'),
    
    # Orders
    path('orders/', OrderListView.as_view(), name='order_list'),
    #path('orders/', views.order_list, name='order_list'),
    path('orders/<int:order_id>/', views.order_detail, name='order_detail'),
    path('orders/<int:order_id>/update-status/', views.update_order_status, name='update_order_status'),
    
    # Analytics
    path('analytics/', views.predictive_analytics, name='predictive_analytics'),
    
    # Delivery
    path('delivery/', views.delivery_optimization, name='delivery_optimization'),
    
    # Customer-facing
    path('track/', views.track_order, name='track_order'),
    path('api/track/<str:tracking_number>/', views.order_tracking_api, name='order_tracking_api'),
]