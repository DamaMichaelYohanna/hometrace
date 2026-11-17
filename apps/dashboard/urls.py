from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_dispatch_view, name='dashboard_dispatch'),

    # Agent Routes
    path('agent/', views.agent_overview_view, name='agent_overview'),
    path('agent/properties/', views.agent_properties_view, name='agent_properties'),
    path('agent/enquiries/', views.agent_enquiries_view, name='agent_enquiries'),

    # Buyer Routes
    path('buyer/', views.buyer_overview_view, name='buyer_overview'),

    # Admin Routes
    path('admin-portal/', views.admin_overview_view, name='admin_overview'),
    path('admin-portal/users/', views.admin_users_view, name='admin_users'),
    path('admin-portal/users/<uuid:user_id>/toggle/', views.admin_user_toggle_status_view, name='admin_user_toggle_status'),
    path('admin-portal/properties/', views.admin_properties_view, name='admin_properties'),
    path('admin-portal/approvals/', views.admin_pending_approvals_view, name='admin_pending_approvals'),
    path('admin-portal/approvals/<uuid:property_id>/approve/', views.admin_approve_property_view, name='admin_approve_property'),
    path('admin-portal/approvals/<uuid:property_id>/reject/', views.admin_reject_property_view, name='admin_reject_property'),
    path('admin-portal/reports/', views.admin_reports_view, name='admin_reports'),
    path('admin-portal/reports/<uuid:report_id>/<str:action>/', views.admin_report_action_view, name='admin_report_action'),
    path('admin-portal/transactions/', views.admin_transactions_view, name='admin_transactions'),
    path('admin-portal/taxonomy/', views.admin_taxonomy_view, name='admin_taxonomy'),
]
