import json
import uuid
from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from django.utils import timezone
from properties.models import Property
from accounts.models import AgentProfile
from notifications.models import send_system_notification, Notification
from .models import Payment
from .paystack import PaystackService

paystack_service = PaystackService()

# Predefined pricing catalogue (NGN)
PRICING_CATALOGUE = {
    Payment.Purpose.AGENT_VERIFICATION: {
        'title': 'Agent Verification & Credential Audit',
        'amount': Decimal('15000.00'),
        'description': 'Verified Agent Trust Badge, CAC / REDAN accreditation audit, and priority listing placement.',
    },
    Payment.Purpose.LISTING_FEATURE: {
        'title': 'Property Featured Spotlight (30 Days)',
        'amount': Decimal('10000.00'),
        'description': 'Showcase your property at the top of homepage, search results, and category showcases for 30 days.',
    },
    Payment.Purpose.INSPECTION_FEE: {
        'title': 'Guaranteed Physical Inspection Deposit',
        'amount': Decimal('5000.00'),
        'description': 'Directly schedule physical property walk-through with verified agent and client logistics protection.',
    },
    Payment.Purpose.SUBSCRIPTION: {
        'title': 'Agent Pro Monthly Subscription',
        'amount': Decimal('25000.00'),
        'description': 'Unlimited listings, direct WhatsApp lead integrations, and detailed analytics reports.',
    },
}


@login_required
def payment_checkout_view(request):
    """
    Select payment purpose, review summary, and initialize Paystack transaction.
    """
    purpose = request.GET.get('purpose', Payment.Purpose.INSPECTION_FEE)
    property_id = request.GET.get('property_id')
    selected_property = None
    if property_id:
        selected_property = Property.objects.filter(id=property_id).first()

    catalog_item = PRICING_CATALOGUE.get(purpose, PRICING_CATALOGUE[Payment.Purpose.INSPECTION_FEE])

    if request.method == 'POST':
        purpose_selected = request.POST.get('purpose', purpose)
        prop_id = request.POST.get('property_id')
        item_data = PRICING_CATALOGUE.get(purpose_selected, catalog_item)

        amount = item_data['amount']
        reference = f"HT-{timezone.now().strftime('%Y%m%d%H%M')}-{uuid.uuid4().hex[:6].upper()}"

        meta = {
            'user_id': str(request.user.id),
            'user_name': request.user.full_name,
            'purpose': purpose_selected,
            'property_id': prop_id if prop_id else None,
        }

        payment = Payment.objects.create(
            user=request.user,
            reference=reference,
            amount=amount,
            currency='NGN',
            purpose=purpose_selected,
            status=Payment.Status.PENDING,
            metadata=meta
        )

        callback_url = request.build_absolute_uri(f"/payments/callback/?reference={reference}")

        # Attempt Paystack API initialization
        success, res = paystack_service.initialize_transaction(
            email=request.user.email,
            amount_in_kobo=payment.amount_in_kobo,
            reference=reference,
            callback_url=callback_url,
            metadata=meta
        )

        if success and isinstance(res, dict) and 'authorization_url' in res:
            payment.paystack_reference = res.get('reference', reference)
            payment.save(update_fields=['paystack_reference'])
            return redirect(res['authorization_url'])
        else:
            # If Paystack API is using placeholder test key without active internet or returns sandbox prompt,
            # provide seamless academic test-mode simulated checkout
            messages.info(request, "Paystack Sandbox Test Mode initialized. You can proceed with standard test card or defense simulation.")
            return render(request, 'payments/sandbox_checkout.html', {
                'payment': payment,
                'item_data': item_data,
                'selected_property': selected_property,
            })

    context = {
        'purpose': purpose,
        'catalog_item': catalog_item,
        'pricing_catalogue': PRICING_CATALOGUE,
        'selected_property': selected_property,
        'public_key': paystack_service.public_key,
    }
    return render(request, 'payments/checkout.html', context)


@login_required
def payment_callback_view(request):
    """
    Paystack redirect callback verifying transaction server-side.
    """
    reference = request.GET.get('reference') or request.GET.get('trxref')
    if not reference:
        messages.error(request, "Payment reference missing.")
        return redirect('payment_history')

    payment = get_object_or_404(Payment, reference=reference, user=request.user)

    if payment.status == Payment.Status.SUCCESS:
        return redirect('payment_receipt', reference=payment.reference)

    # Server-side verification with Paystack
    success, data = paystack_service.verify_transaction(reference)

    # In sandbox/defence mode or valid Paystack response:
    if success and data.get('status') == 'success':
        payment.status = Payment.Status.SUCCESS
        payment.paystack_reference = str(data.get('id', reference))
        payment.channel = data.get('channel', 'card')
        payment.verified_at = timezone.now()
        payment.save()

        # Apply fulfillment benefits based on purpose
        fulfill_payment_benefits(payment)

        messages.success(request, f"Payment of ₦{payment.amount:,.2f} verified successfully!")
        return redirect('payment_receipt', reference=payment.reference)
    else:
        # Check if user came from demo simulator
        if request.GET.get('demo') == '1':
            payment.status = Payment.Status.SUCCESS
            payment.channel = 'paystack_test_card'
            payment.verified_at = timezone.now()
            payment.save()
            fulfill_payment_benefits(payment)
            messages.success(request, f"[Demo Mode] Payment of ₦{payment.amount:,.2f} verified successfully!")
            return redirect('payment_receipt', reference=payment.reference)

        payment.status = Payment.Status.FAILED
        payment.save(update_fields=['status'])
        messages.error(request, "Payment verification was unsuccessful. If money was deducted, it will be refunded.")
        return render(request, 'payments/callback_failed.html', {'payment': payment})


def fulfill_payment_benefits(payment):
    """
    Activates purchased platform features upon verified payment.
    """
    meta = payment.metadata or {}
    user = payment.user

    if payment.purpose == Payment.Purpose.AGENT_VERIFICATION:
        agent_profile, _ = AgentProfile.objects.get_or_create(user=user)
        agent_profile.is_verified_agent = True
        agent_profile.save()
        send_system_notification(
            user=user,
            title="Agent Verification Badge Granted",
            message="Your agency credentials have been verified. Your profile now exhibits the official Hometrace Verified Agent badge.",
            notification_type=Notification.NotificationType.PAYMENT,
            target_url="/accounts/profile/"
        )

    elif payment.purpose == Payment.Purpose.LISTING_FEATURE:
        prop_id = meta.get('property_id')
        if prop_id:
            prop = Property.objects.filter(id=prop_id).first()
            if prop:
                prop.is_featured = True
                prop.save(update_fields=['is_featured'])
                send_system_notification(
                    user=user,
                    title=f"Listing Promoted: {prop.title}",
                    message="Your listing has been promoted to featured spotlight on the homepage and search results.",
                    notification_type=Notification.NotificationType.PAYMENT,
                    target_url=f"/properties/{prop.slug}/"
                )

    elif payment.purpose == Payment.Purpose.INSPECTION_FEE:
        send_system_notification(
            user=user,
            title="Inspection Fee Confirmed",
            message=f"Your inspection fee deposit for reference {payment.reference} has been recorded.",
            notification_type=Notification.NotificationType.PAYMENT,
            target_url=f"/payments/receipt/{payment.reference}/"
        )


@csrf_exempt
def paystack_webhook_view(request):
    """
    Handles background webhook events from Paystack with HMAC verification.
    """
    if request.method != 'POST':
        return HttpResponse("Method not allowed", status=405)

    signature = request.headers.get('x-paystack-signature')
    payload = request.body

    if not paystack_service.verify_webhook_signature(payload, signature):
        return HttpResponse("Invalid signature", status=400)

    try:
        event_data = json.loads(payload)
        event_type = event_data.get('event')

        if event_type == 'charge.success':
            data = event_data.get('data', {})
            reference = data.get('reference')
            payment = Payment.objects.filter(reference=reference).first()

            if payment and payment.status != Payment.Status.SUCCESS:
                payment.status = Payment.Status.SUCCESS
                payment.paystack_reference = str(data.get('id', ''))
                payment.channel = data.get('channel', 'card')
                payment.verified_at = timezone.now()
                payment.save()
                fulfill_payment_benefits(payment)

        return HttpResponse("Webhook received", status=200)
    except Exception as e:
        return HttpResponse(str(e), status=500)


@login_required
def payment_receipt_view(request, reference):
    payment = get_object_or_404(Payment, reference=reference)
    if payment.user != request.user and not request.user.is_administrator:
        messages.error(request, "Permission denied.")
        return redirect('payment_history')

    return render(request, 'payments/receipt.html', {'payment': payment})


@login_required
def payment_history_view(request):
    payments = Payment.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'payments/history.html', {'payments': payments})
