from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from accounts.decorators import agent_required
from accounts.models import User, AgentProfile
from .models import Property, PropertyCategory, Amenity, PropertyImage, PropertyReport
from .forms import PropertyForm, PropertyImageUploadForm, PropertyReportForm


def property_list_view(request):
    """
    Public listing page for approved properties.
    """
    queryset = Property.objects.filter(
        approval_status=Property.ApprovalStatus.APPROVED,
        availability_status=Property.AvailabilityStatus.AVAILABLE
    ).select_related('category', 'agent').prefetch_related('images')

    # Purpose filter
    purpose = request.GET.get('purpose')
    if purpose in ['for_sale', 'for_rent']:
        queryset = queryset.filter(listing_purpose=purpose)

    # Category filter
    category_slug = request.GET.get('category')
    if category_slug:
        queryset = queryset.filter(category__slug=category_slug)

    # State filter
    state = request.GET.get('state')
    if state:
        queryset = queryset.filter(state__iexact=state)

    # Sorting
    sort_by = request.GET.get('sort', '-created_at')
    valid_sorts = {
        'newest': '-created_at',
        'oldest': 'created_at',
        'price_low': 'price',
        'price_high': '-price',
    }
    order_field = valid_sorts.get(sort_by, '-created_at')
    queryset = queryset.order_by(order_field)

    paginator = Paginator(queryset, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    categories = PropertyCategory.objects.filter(is_active=True)

    context = {
        'properties': page_obj,
        'page_obj': page_obj,
        'total_count': paginator.count,
        'categories': categories,
        'current_purpose': purpose or '',
        'current_category': category_slug or '',
        'current_state': state or '',
        'current_sort': sort_by,
    }
    return render(request, 'properties/list.html', context)


def property_detail_view(request, slug):
    """
    Detailed property view with gallery, amenities, agent card, and similar properties.
    """
    prop = get_object_or_404(
        Property.objects.select_related('category', 'agent').prefetch_related('images', 'amenities'),
        slug=slug
    )

    # If property is not approved, only owner agent or admin can view
    if not prop.is_public:
        if not (request.user.is_authenticated and (request.user == prop.agent or request.user.is_administrator)):
            messages.warning(request, "This listing is currently pending moderation or is not available.")
            return redirect('property_list')

    # Increment view counter once per session
    session_key = f"viewed_prop_{prop.id}"
    if not request.session.get(session_key):
        prop.view_count += 1
        prop.save(update_fields=['view_count'])
        request.session[session_key] = True

    # Similar properties (same state or category, excluding current)
    similar_properties = Property.objects.filter(
        approval_status=Property.ApprovalStatus.APPROVED,
        availability_status=Property.AvailabilityStatus.AVAILABLE
    ).filter(
        Q(category=prop.category) | Q(state=prop.state)
    ).exclude(id=prop.id).select_related('category', 'agent').prefetch_related('images')[:4]

    agent_profile = getattr(prop.agent, 'agent_profile', None)
    agent_active_count = Property.objects.filter(
        agent=prop.agent,
        approval_status=Property.ApprovalStatus.APPROVED,
        availability_status=Property.AvailabilityStatus.AVAILABLE
    ).count()

    report_form = PropertyReportForm()

    context = {
        'property': prop,
        'similar_properties': similar_properties,
        'agent_profile': agent_profile,
        'agent_active_count': agent_active_count,
        'report_form': report_form,
    }
    return render(request, 'properties/detail.html', context)


@login_required
@agent_required
def property_create_view(request):
    """
    Allows agents to create a new listing with multi-image uploads.
    """
    if request.method == 'POST':
        form = PropertyForm(request.POST, request.FILES)
        image_form = PropertyImageUploadForm(request.POST, request.FILES)

        if form.is_valid() and image_form.is_valid():
            prop = form.save(commit=False)
            prop.agent = request.user
            prop.approval_status = Property.ApprovalStatus.PENDING
            prop.save()
            form.save_m2m()

            # Handle multiple images
            files = request.FILES.getlist('images')
            for index, file in enumerate(files):
                PropertyImage.objects.create(
                    property=prop,
                    image=file,
                    is_featured=(index == 0 and not prop.featured_image),
                    display_order=index
                )

            messages.success(
                request,
                f"'{prop.title}' has been submitted successfully and is now pending administrator review."
            )
            return redirect('agent_properties')
        else:
            messages.error(request, "Please check the highlighted errors in the form.")
    else:
        form = PropertyForm()
        image_form = PropertyImageUploadForm()

    return render(request, 'properties/create.html', {'form': form, 'image_form': image_form})


@login_required
def property_edit_view(request, slug):
    """
    Edit existing property listing. Owner agent or admin only.
    """
    prop = get_object_or_404(Property, slug=slug)

    # Permission check
    if not (request.user == prop.agent or request.user.is_administrator):
        messages.error(request, "You do not have permission to edit this property listing.")
        return redirect('property_list')

    if request.method == 'POST':
        form = PropertyForm(request.POST, request.FILES, instance=prop)
        image_form = PropertyImageUploadForm(request.POST, request.FILES)

        if form.is_valid() and image_form.is_valid():
            prop = form.save(commit=False)
            # Re-submit for approval if edited by agent
            if not request.user.is_administrator:
                prop.approval_status = Property.ApprovalStatus.PENDING
            prop.save()
            form.save_m2m()

            files = request.FILES.getlist('images')
            for index, file in enumerate(files):
                PropertyImage.objects.create(
                    property=prop,
                    image=file,
                    display_order=prop.images.count() + index
                )

            messages.success(request, f"Changes saved for '{prop.title}'.")
            if request.user.is_administrator:
                return redirect('admin_properties')
            return redirect('agent_properties')
    else:
        form = PropertyForm(instance=prop)
        image_form = PropertyImageUploadForm()

    context = {
        'form': form,
        'image_form': image_form,
        'property': prop,
    }
    return render(request, 'properties/edit.html', context)


@login_required
def property_delete_view(request, slug):
    """
    Delete or archive a property listing.
    """
    prop = get_object_or_404(Property, slug=slug)

    if not (request.user == prop.agent or request.user.is_administrator):
        messages.error(request, "Unauthorized operation.")
        return redirect('property_list')

    if request.method == 'POST':
        title = prop.title
        prop.delete()
        messages.success(request, f"Property listing '{title}' has been deleted.")
        if request.user.is_administrator:
            return redirect('admin_properties')
        return redirect('agent_properties')

    return render(request, 'properties/confirm_delete.html', {'property': prop})


@login_required
def property_status_toggle_view(request, slug, new_status):
    """
    Quick status toggle for agent dashboard: available, under_offer, rented, sold.
    """
    prop = get_object_or_404(Property, slug=slug)
    if not (request.user == prop.agent or request.user.is_administrator):
        messages.error(request, "Permission denied.")
        return redirect('agent_properties')

    valid_statuses = dict(Property.AvailabilityStatus.choices)
    if new_status in valid_statuses:
        prop.availability_status = new_status
        prop.save(update_fields=['availability_status'])
        messages.success(request, f"Status of '{prop.title}' updated to {valid_statuses[new_status]}.")

    return redirect('agent_properties')


def property_report_view(request, slug):
    """
    Handles report submission against suspected fraudulent or inaccurate listings.
    """
    prop = get_object_or_404(Property, slug=slug)
    if request.method == 'POST':
        form = PropertyReportForm(request.POST)
        if form.is_valid():
            report = form.save(commit=False)
            report.property = prop
            if request.user.is_authenticated:
                report.reporter = request.user
                if not report.reporter_name:
                    report.reporter_name = request.user.full_name
                if not report.reporter_email:
                    report.reporter_email = request.user.email
            report.save()
            messages.success(request, "Your report has been submitted to Hometrace administrators for moderation. Thank you for keeping the platform safe.")
        else:
            messages.error(request, "Please fill in all required fields to submit a report.")
    return redirect('property_detail', slug=slug)


def agent_public_profile_view(request, agent_id):
    """
    Public profile of an agent displaying verified credentials and all their active listings.
    """
    agent = get_object_or_404(User, id=agent_id, role=User.Role.AGENT)
    agent_profile = getattr(agent, 'agent_profile', None)

    active_listings = Property.objects.filter(
        agent=agent,
        approval_status=Property.ApprovalStatus.APPROVED,
        availability_status=Property.AvailabilityStatus.AVAILABLE
    ).select_related('category').prefetch_related('images').order_by('-created_at')

    context = {
        'agent': agent,
        'agent_profile': agent_profile,
        'listings': active_listings,
        'total_active': active_listings.count(),
    }
    return render(request, 'properties/agent_profile.html', context)
