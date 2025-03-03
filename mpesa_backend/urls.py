from django.urls import path
from .views import mpesa_payment, mpesa_callback  # Import callback view

urlpatterns = [
    path('api/payment/', mpesa_payment, name='mpesa_payment'),
    path('api/mpesa-callback/', mpesa_callback, name='mpesa_callback'),  # Add callback route
]
