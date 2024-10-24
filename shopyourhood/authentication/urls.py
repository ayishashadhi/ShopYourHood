from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    # Customer registration
    path('register/customer/', views.customer_register, name='customer_register'),

    # Shop owner registration
    path('register/shop/', views.shop_owner_register, name='shop_owner_register'),

    # Dashboards
    path('customer/dashboard/', views.customer_dashboard, name='customer_dashboard'),
    path('shop/dashboard/', views.shop_owner_dashboard, name='shop_owner_dashboard'),

    # Shop pending verification
    path('shop/pending_verification/', views.shop_pending_verification, name='shop_pending_verification'),

    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),


     # Admin dashboard (for verifying shops)
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    
    # Verify or reject a shop
    path('admin/verify_shop/<int:shop_id>/', views.verify_shop, name='verify_shop'),
]   