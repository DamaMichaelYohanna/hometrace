from django.urls import path
from . import views

urlpatterns = [
    path('', views.inbox_view, name='inbox'),
    path('<uuid:conversation_id>/', views.conversation_detail_view, name='conversation_detail'),
    path('enquire/<slug:property_slug>/', views.send_enquiry_view, name='send_enquiry'),
    path('api/poll/<uuid:conversation_id>/', views.poll_messages_api, name='poll_messages_api'),
]
