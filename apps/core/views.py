from django.shortcuts import render, redirect
from django.contrib import messages
from properties.models import Property, PropertyCategory
from properties.forms import NIGERIAN_STATES


def home_view(request):
    """
    Homepage featuring hero search, categories, featured properties, and marketplace highlights.
    """
    categories = PropertyCategory.objects.filter(is_active=True)[:8]

    # Featured properties for homepage spotlight
    featured_properties = Property.objects.filter(
        approval_status=Property.ApprovalStatus.APPROVED,
        availability_status=Property.AvailabilityStatus.AVAILABLE,
        is_featured=True
    ).select_related('category', 'agent').prefetch_related('images')[:6]

    # If fewer than 6 featured, backfill with recent approved listings
    if featured_properties.count() < 4:
        featured_properties = Property.objects.filter(
            approval_status=Property.ApprovalStatus.APPROVED,
            availability_status=Property.AvailabilityStatus.AVAILABLE
        ).select_related('category', 'agent').prefetch_related('images').order_by('-created_at')[:6]

    # Latest listings
    latest_properties = Property.objects.filter(
        approval_status=Property.ApprovalStatus.APPROVED,
        availability_status=Property.AvailabilityStatus.AVAILABLE
    ).select_related('category', 'agent').prefetch_related('images').order_by('-created_at')[:8]

    # Key focal locations in Keffi, Nasarawa State
    hotspots = [
        {
            'city': 'Angwan Lambu',
            'state': 'Nasarawa',
            'image': '/static/images/keffi/keffi_student_hostel.jpg',
            'count': Property.objects.filter(approval_status=Property.ApprovalStatus.APPROVED, neighbourhood__icontains='Angwan Lambu').count()
        },
        {
            'city': 'GRA Keffi',
            'state': 'Nasarawa',
            'image': '/static/images/keffi/keffi_modern_bungalow.webp',
            'count': Property.objects.filter(approval_status=Property.ApprovalStatus.APPROVED, neighbourhood__icontains='GRA').count()
        },
        {
            'city': 'FMC Corridor',
            'state': 'Nasarawa',
            'image': '/static/images/keffi/keffi_bungalow_compound.webp',
            'count': Property.objects.filter(approval_status=Property.ApprovalStatus.APPROVED, neighbourhood__icontains='FMC').count()
        },
        {
            'city': 'Abuja-Keffi Expressway',
            'state': 'Nasarawa',
            'image': '/static/images/keffi/keffi_duplex_interior.jpg',
            'count': Property.objects.filter(approval_status=Property.ApprovalStatus.APPROVED, neighbourhood__icontains='Expressway').count()
        },
    ]

    context = {
        'categories': categories,
        'featured_properties': featured_properties,
        'latest_properties': latest_properties,
        'hotspots': hotspots,
        'nigerian_states': NIGERIAN_STATES,
    }
    return render(request, 'core/index.html', context)


def about_view(request):
    return render(request, 'core/about.html')


def contact_view(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        messages.success(request, f"Thank you, {name}! Your message has been received. Our team will get back to you shortly.")
        return redirect('contact')
    return render(request, 'core/contact.html')


def privacy_view(request):
    return render(request, 'core/privacy.html')


def terms_view(request):
    return render(request, 'core/terms.html')


def offline_view(request):
    """
    PWA fallback page served when network is unavailable.
    """
    return render(request, 'offline.html')


# Custom Error Handlers
def handler403(request, exception=None):
    return render(request, '403.html', status=403)


def handler404(request, exception=None):
    return render(request, '404.html', status=404)


def handler500(request):
    return render(request, '500.html', status=500)
