from django.urls import path
from .views import home, mpesa_payment, mpesa_callback

urlpatterns = [
    path('', home, name='home'),
    path('api/payment/', mpesa_payment, name='mpesa_payment'),
    path('api/mpesa-callback/', mpesa_callback, name='mpesa_callback'),  # Add this line
]