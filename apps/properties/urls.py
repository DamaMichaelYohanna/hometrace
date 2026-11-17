from django.urls import path
from . import views

urlpatterns = [
    path('', views.property_list_view, name='property_list'),
    path('create/', views.property_create_view, name='property_create'),
    path('agent/<uuid:agent_id>/', views.agent_public_profile_view, name='agent_public_profile'),
    path('<slug:slug>/', views.property_detail_view, name='property_detail'),
    path('<slug:slug>/edit/', views.property_edit_view, name='property_edit'),
    path('<slug:slug>/delete/', views.property_delete_view, name='property_delete'),
    path('<slug:slug>/status/<str:new_status>/', views.property_status_toggle_view, name='property_status_toggle'),
    path('<slug:slug>/report/', views.property_report_view, name='property_report'),
]
