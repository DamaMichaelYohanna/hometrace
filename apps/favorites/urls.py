from django.urls import path
from . import views

urlpatterns = [
    path('', views.favorites_list_view, name='favorites_list'),
    path('toggle/<uuid:property_id>/', views.toggle_favorite_view, name='toggle_favorite'),
]
