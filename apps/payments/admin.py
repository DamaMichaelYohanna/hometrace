from django.contrib import admin
from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('reference', 'user', 'amount', 'currency', 'purpose', 'status', 'created_at', 'verified_at')
    list_filter = ('status', 'purpose', 'currency', 'created_at')
    search_fields = ('reference', 'paystack_reference', 'user__email', 'user__full_name')
    readonly_fields = ('created_at', 'verified_at')
