from django.contrib import admin
from .models import User, AgentProfile, BuyerProfile


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'full_name', 'phone_number', 'role', 'is_verified', 'is_active', 'date_joined')
    list_filter = ('role', 'is_verified', 'is_active')
    search_fields = ('email', 'full_name', 'phone_number')
    ordering = ('-date_joined',)
    readonly_fields = ('date_joined', 'updated_at')


@admin.register(AgentProfile)
class AgentProfileAdmin(admin.ModelAdmin):
    list_display = ('agency_name', 'user', 'state', 'city', 'whatsapp_number', 'is_verified_agent')
    list_filter = ('is_verified_agent', 'state')
    search_fields = ('agency_name', 'user__email', 'user__full_name', 'license_number')


@admin.register(BuyerProfile)
class BuyerProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'preferred_state', 'preferred_city', 'max_budget')
    search_fields = ('user__email', 'user__full_name')
