from django.urls import path
from . import views

urlpatterns = [
    path('', views.notification_list_view, name='notification_list'),
    path('mark-read/<uuid:notification_id>/', views.mark_notification_read_view, name='mark_notification_read'),
    path('mark-all-read/', views.mark_all_notifications_read_view, name='mark_all_notifications_read'),
    path('api/count/', views.notification_count_api, name='notification_count_api'),
]
