import uuid
from django.db import models
from django.conf import settings


class Payment(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending Verification'
        SUCCESS = 'success', 'Successful'
        FAILED = 'failed', 'Failed'
        ABANDONED = 'abandoned', 'Abandoned'

    class Purpose(models.TextChoices):
        AGENT_VERIFICATION = 'agent_verification', 'Agent Verification & Credential Audit'
        LISTING_FEATURE = 'listing_feature', 'Featured Listing Promotion'
        INSPECTION_FEE = 'inspection_fee', 'Property Physical Inspection Deposit'
        SUBSCRIPTION = 'subscription', 'Agent Pro Monthly Subscription'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='payments')
    reference = models.CharField(max_length=100, unique=True, db_index=True)
    paystack_reference = models.CharField(max_length=100, blank=True, default="")
    amount = models.DecimalField(max_digits=12, decimal_places=2, help_text="Amount in NGN")
    currency = models.CharField(max_length=10, default="NGN")
    purpose = models.CharField(max_length=30, choices=Purpose.choices, default=Purpose.INSPECTION_FEE)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING, db_index=True)
    channel = models.CharField(max_length=50, blank=True, default="card")
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    verified_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'Payment Transaction'
        verbose_name_plural = 'Payment Transactions'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.reference} - ₦{self.amount:,.2f} ({self.get_status_display()})"

    @property
    def amount_in_kobo(self):
        return int(self.amount * 100)

    @property
    def formatted_amount(self):
        return f"₦{self.amount:,.2f}"
