from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView
from . import views

urlpatterns = [
    # Retailer authentication
    path('retailer/signup/', views.retailer_signup, name='retailer_signup'),
    path('retailer/login/', views.retailer_login, name='retailer_login'),
    
    # Customer authentication
    path('customer/signup/', views.customer_signup, name='customer_signup'),
    
    # CORRECTED: This path now correctly points to the view that handles phone/password login.
    # The old path was trying to use a view named 'customer_login' which doesn't exist.
    path('customer/login-with-password/', views.customer_login_with_password, name='customer_login_with_password'),
    
    # Common authentication
    path('profile/', views.get_profile, name='get_profile'),
    # You might have other URLs here for profile updates, password changes, etc.
    # Ensure they point to valid views in your views.py file.
    
    # JWT token management
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
]