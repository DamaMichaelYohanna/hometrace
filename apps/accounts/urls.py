from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('send-verification/', views.send_verification_email_view, name='send_verification_email'),
    path('verify-email/<str:token>/', views.verify_email_token_view, name='verify_email_token'),
    path('password-reset/', views.password_reset_request_view, name='password_reset'),
]
