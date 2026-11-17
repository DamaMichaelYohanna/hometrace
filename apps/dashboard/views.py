from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Sum, Q
from django.utils import timezone
from accounts.models import User, AgentProfile
from accounts.decorators import agent_required, buyer_required, admin_required
from properties.models import Property, PropertyCategory, Amenity, PropertyReport
from messaging.models import Conversation, Enquiry
from favorites.models import Favorite
from payments.models import Payment
from notifications.models import send_system_notification, Notification


@login_required
def dashboard_dispatch_view(request):
    """
    Intelligent role-based redirector.
    """
    if request.user.is_administrator:
        return redirect('admin_overview')
    elif request.user.is_agent:
        return redirect('agent_overview')
    else:
        return redirect('buyer_overview')


# ==========================================
# AGENT DASHBOARD VIEWS
# ==========================================

@login_required
@agent_required
def agent_overview_view(request):
    user = request.user
    user_properties = Property.objects.filter(agent=user)

    total_properties = user_properties.count()
    published_count = user_properties.filter(approval_status=Property.ApprovalStatus.APPROVED, availability_status=Property.AvailabilityStatus.AVAILABLE).count()
    pending_count = user_properties.filter(approval_status=Property.ApprovalStatus.PENDING).count()
    rejected_count = user_properties.filter(approval_status=Property.ApprovalStatus.REJECTED).count()
    rented_count = user_properties.filter(availability_status=Property.AvailabilityStatus.RENTED).count()
    sold_count = user_properties.filter(availability_status=Property.AvailabilityStatus.SOLD).count()

    enquiries = Enquiry.objects.filter(agent=user).select_related('buyer', 'property').order_by('-created_at')
    total_enquiries = enquiries.count()
    pending_enquiries = enquiries.filter(status='pending').count()

    recent_properties = user_properties.select_related('category').prefetch_related('images').order_by('-created_at')[:8]
    recent_enquiries = enquiries[:5]

    context = {
        'total_properties': total_properties,
        'published_count': published_count,
        'pending_count': pending_count,
        'rejected_count': rejected_count,
        'rented_count': rented_count,
        'sold_count': sold_count,
        'total_enquiries': total_enquiries,
        'pending_enquiries': pending_enquiries,
        'recent_properties': recent_properties,
        'recent_enquiries': recent_enquiries,
        'agent_profile': getattr(user, 'agent_profile', None),
    }
    return render(request, 'dashboard/agent/overview.html', context)


@login_required
@agent_required
def agent_properties_view(request):
    user = request.user
    status_filter = request.GET.get('status', 'all')
    properties = Property.objects.filter(agent=user).select_related('category').prefetch_related('images').order_by('-created_at')

    if status_filter == 'published':
        properties = properties.filter(approval_status=Property.ApprovalStatus.APPROVED, availability_status=Property.AvailabilityStatus.AVAILABLE)
    elif status_filter == 'pending':
        properties = properties.filter(approval_status=Property.ApprovalStatus.PENDING)
    elif status_filter == 'rejected':
        properties = properties.filter(approval_status=Property.ApprovalStatus.REJECTED)
    elif status_filter == 'rented':
        properties = properties.filter(availability_status=Property.AvailabilityStatus.RENTED)
    elif status_filter == 'sold':
        properties = properties.filter(availability_status=Property.AvailabilityStatus.SOLD)

    context = {
        'properties': properties,
        'current_status': status_filter,
    }
    return render(request, 'dashboard/agent/properties.html', context)


@login_required
@agent_required
def agent_enquiries_view(request):
    enquiries = Enquiry.objects.filter(agent=request.user).select_related('buyer', 'property').order_by('-created_at')
    return render(request, 'dashboard/agent/enquiries.html', {'enquiries': enquiries})


# ==========================================
# BUYER / RENTER DASHBOARD VIEWS
# ==========================================

@login_required
@buyer_required
def buyer_overview_view(request):
    user = request.user
    saved_properties = Favorite.objects.filter(user=user).select_related('property', 'property__category', 'property__agent').prefetch_related('property__images')[:6]
    total_saved = Favorite.objects.filter(user=user).count()

    conversations = Conversation.objects.filter(buyer=user).select_related('agent', 'property').order_by('-updated_at')[:6]
    for c in conversations:
        c.user_unread_count = c.unread_count_for_user(user)

    payments = Payment.objects.filter(user=user).order_by('-created_at')[:5]

    context = {
        'saved_properties': saved_properties,
        'total_saved': total_saved,
        'conversations': conversations,
        'payments': payments,
    }
    return render(request, 'dashboard/buyer/overview.html', context)


# ==========================================
# ADMINISTRATOR DASHBOARD VIEWS
# ==========================================

@login_required
@admin_required
def admin_overview_view(request):
    # User KPIs
    total_users = User.objects.count()
    total_agents = User.objects.filter(role=User.Role.AGENT).count()
    total_buyers = User.objects.filter(role=User.Role.BUYER).count()

    # Property KPIs
    all_properties = Property.objects.all()
    total_properties = all_properties.count()
    published_count = all_properties.filter(approval_status=Property.ApprovalStatus.APPROVED, availability_status=Property.AvailabilityStatus.AVAILABLE).count()
    pending_count = all_properties.filter(approval_status=Property.ApprovalStatus.PENDING).count()
    rejected_count = all_properties.filter(approval_status=Property.ApprovalStatus.REJECTED).count()
    sold_count = all_properties.filter(availability_status=Property.AvailabilityStatus.SOLD).count()
    rented_count = all_properties.filter(availability_status=Property.AvailabilityStatus.RENTED).count()

    # Financial KPIs
    payments = Payment.objects.all()
    total_payments_count = payments.count()
    successful_payments = payments.filter(status=Payment.Status.SUCCESS)
    total_revenue = successful_payments.aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')

    # Chart distribution data
    category_distribution = PropertyCategory.objects.annotate(count=Count('properties')).values('name', 'count')
    location_distribution = Property.objects.values('state').annotate(count=Count('id')).order_by('-count')[:6]

    # Moderation queues
    pending_properties = all_properties.filter(approval_status=Property.ApprovalStatus.PENDING).select_related('agent', 'category').order_by('-created_at')[:5]
    recent_reports = PropertyReport.objects.filter(status='pending').select_related('property', 'reporter')[:5]
    recent_users = User.objects.order_by('-date_joined')[:6]

    context = {
        'total_users': total_users,
        'total_agents': total_agents,
        'total_buyers': total_buyers,
        'total_properties': total_properties,
        'published_count': published_count,
        'pending_count': pending_count,
        'rejected_count': rejected_count,
        'sold_count': sold_count,
        'rented_count': rented_count,
        'total_payments_count': total_payments_count,
        'total_revenue': total_revenue,
        'category_distribution': list(category_distribution),
        'location_distribution': list(location_distribution),
        'pending_properties': pending_properties,
        'recent_reports': recent_reports,
        'recent_users': recent_users,
    }
    return render(request, 'dashboard/admin/overview.html', context)


@login_required
@admin_required
def admin_users_view(request):
    role_filter = request.GET.get('role')
    users = User.objects.all().order_by('-date_joined')

    if role_filter in ['agent', 'buyer', 'admin']:
        users = users.filter(role=role_filter)

    search = request.GET.get('search', '').strip()
    if search:
        users = users.filter(Q(email__icontains=search) | Q(full_name__icontains=search) | Q(phone_number__icontains=search))

    context = {
        'users': users,
        'role_filter': role_filter or 'all',
        'search': search,
    }
    return render(request, 'dashboard/admin/users.html', context)


@login_required
@admin_required
def admin_user_toggle_status_view(request, user_id):
    target_user = get_object_or_404(User, id=user_id)
    if target_user == request.user:
        messages.error(request, "You cannot suspend your own administrative account.")
        return redirect('admin_users')

    target_user.is_active = not target_user.is_active
    target_user.save(update_fields=['is_active'])
    status_label = "activated" if target_user.is_active else "suspended"
    messages.success(request, f"User {target_user.full_name} has been {status_label}.")
    return redirect('admin_users')


@login_required
@admin_required
def admin_properties_view(request):
    status_filter = request.GET.get('status')
    properties = Property.objects.select_related('agent', 'category').prefetch_related('images').order_by('-created_at')

    if status_filter:
        properties = properties.filter(approval_status=status_filter)

    return render(request, 'dashboard/admin/properties.html', {
        'properties': properties,
        'status_filter': status_filter or 'all',
    })


@login_required
@admin_required
def admin_pending_approvals_view(request):
    pending_properties = Property.objects.filter(
        approval_status=Property.ApprovalStatus.PENDING
    ).select_related('agent', 'category').prefetch_related('images').order_by('-created_at')

    return render(request, 'dashboard/admin/pending_approvals.html', {'properties': pending_properties})


@login_required
@admin_required
def admin_approve_property_view(request, property_id):
    prop = get_object_or_404(Property, id=property_id)
    prop.approval_status = Property.ApprovalStatus.APPROVED
    prop.published_at = timezone.now()
    prop.rejection_reason = ""
    prop.save(update_fields=['approval_status', 'published_at', 'rejection_reason'])

    send_system_notification(
        user=prop.agent,
        title=f"Property Approved: {prop.title}",
        message=f"Congratulations! Your property '{prop.title}' has been reviewed and approved. It is now visible to prospective buyers and renters on Hometrace.",
        notification_type=Notification.NotificationType.PROPERTY_STATUS,
        target_url=f"/properties/{prop.slug}/"
    )

    messages.success(request, f"Property '{prop.title}' has been approved and published.")
    return redirect('admin_pending_approvals')


@login_required
@admin_required
def admin_reject_property_view(request, property_id):
    prop = get_object_or_404(Property, id=property_id)
    reason = request.POST.get('reason', 'Listing information requires revision or fails compliance guidelines.').strip()

    prop.approval_status = Property.ApprovalStatus.REJECTED
    prop.rejection_reason = reason
    prop.save(update_fields=['approval_status', 'rejection_reason'])

    send_system_notification(
        user=prop.agent,
        title=f"Property Review Notice: {prop.title}",
        message=f"Your listing was not approved for the following reason: {reason}. You can edit and resubmit it from your dashboard.",
        notification_type=Notification.NotificationType.PROPERTY_STATUS,
        target_url=f"/properties/{prop.slug}/edit/"
    )

    messages.warning(request, f"Property '{prop.title}' was rejected.")
    return redirect('admin_pending_approvals')


@login_required
@admin_required
def admin_reports_view(request):
    reports = PropertyReport.objects.select_related('property', 'reporter').order_by('-created_at')
    return render(request, 'dashboard/admin/reports.html', {'reports': reports})


@login_required
@admin_required
def admin_report_action_view(request, report_id, action):
    report = get_object_or_404(PropertyReport, id=report_id)
    if action == 'dismiss':
        report.status = 'dismissed'
        report.save(update_fields=['status'])
        messages.info(request, "Report dismissed.")
    elif action == 'archive':
        report.status = 'action_taken'
        report.save(update_fields=['status'])
        report.property.approval_status = Property.ApprovalStatus.ARCHIVED
        report.property.save(update_fields=['approval_status'])
        messages.success(request, f"Property '{report.property.title}' archived and removed from public view.")

    return redirect('admin_reports')


@login_required
@admin_required
def admin_transactions_view(request):
    transactions = Payment.objects.select_related('user').order_by('-created_at')
    total_amount = transactions.filter(status=Payment.Status.SUCCESS).aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')

    return render(request, 'dashboard/admin/transactions.html', {
        'transactions': transactions,
        'total_amount': total_amount,
    })


@login_required
@admin_required
def admin_taxonomy_view(request):
    categories = PropertyCategory.objects.all()
    amenities = Amenity.objects.all()

    if request.method == 'POST':
        action_type = request.POST.get('action_type')
        if action_type == 'add_category':
            name = request.POST.get('name', '').strip()
            icon_name = request.POST.get('icon_name', 'home').strip()
            desc = request.POST.get('description', '').strip()
            if name:
                PropertyCategory.objects.create(name=name, icon_name=icon_name, description=desc)
                messages.success(request, f"Category '{name}' created.")
        elif action_type == 'add_amenity':
            name = request.POST.get('name', '').strip()
            category = request.POST.get('category', 'utility')
            if name:
                Amenity.objects.create(name=name, category=category)
                messages.success(request, f"Amenity '{name}' added.")
        return redirect('admin_taxonomy')

    return render(request, 'dashboard/admin/taxonomy.html', {
        'categories': categories,
        'amenities': amenities,
    })
