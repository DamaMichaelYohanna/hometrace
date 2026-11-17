from django.urls import path
from . import views

urlpatterns = [
    path('', views.payment_history_view, name='payment_history'),
    path('checkout/', views.payment_checkout_view, name='payment_checkout'),
    path('callback/', views.payment_callback_view, name='payment_callback'),
    path('receipt/<str:reference>/', views.payment_receipt_view, name='payment_receipt'),
    path('webhook/', views.paystack_webhook_view, name='paystack_webhook'),
]
