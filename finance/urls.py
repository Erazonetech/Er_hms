from django.urls import path
from . import views
# urls.py


urlpatterns = [
    # Prescription URLs
   path('cashier_dashboard/', views.cashier_dashboard, name='cashier_dashboard'),
   path('process_payment/<int:payment_id>', views.process_payment, name='process_payment'),
]
