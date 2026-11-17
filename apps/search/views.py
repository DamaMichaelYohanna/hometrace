from django.shortcuts import render
from django.core.paginator import Paginator
from django.db.models import Q
from properties.models import Property, PropertyCategory, Amenity
from properties.forms import NIGERIAN_STATES


def search_view(request):
    """
    Advanced multi-faceted search engine for Hometrace properties.
    """
    queryset = Property.objects.filter(
        approval_status=Property.ApprovalStatus.APPROVED,
        availability_status=Property.AvailabilityStatus.AVAILABLE
    ).select_related('category', 'agent').prefetch_related('images', 'amenities')

    # Query string for keyword search
    q = request.GET.get('q', '').strip()
    if q:
        queryset = queryset.filter(
            Q(title__icontains=q) |
            Q(description__icontains=q) |
            Q(city__icontains=q) |
            Q(neighbourhood__icontains=q) |
            Q(state__icontains=q) |
            Q(street_address__icontains=q)
        )

    # Location filters
    state = request.GET.get('state', '').strip()
    if state:
        queryset = queryset.filter(state__iexact=state)

    city = request.GET.get('city', '').strip()
    if city:
        queryset = queryset.filter(city__icontains=city)

    neighbourhood = request.GET.get('neighbourhood', '').strip()
    if neighbourhood:
        queryset = queryset.filter(neighbourhood__icontains=neighbourhood)

    # Purpose filter
    purpose = request.GET.get('purpose', '').strip()
    if purpose in ['for_sale', 'for_rent']:
        queryset = queryset.filter(listing_purpose=purpose)

    # Category filter
    category_id = request.GET.get('category', '').strip()
    if category_id:
        queryset = queryset.filter(category_id=category_id)

    # Property Type filter
    property_type = request.GET.get('property_type', '').strip()
    if property_type:
        queryset = queryset.filter(property_type=property_type)

    # Price range filters
    min_price = request.GET.get('min_price', '').strip()
    if min_price and min_price.isdigit():
        queryset = queryset.filter(price__gte=int(min_price))

    max_price = request.GET.get('max_price', '').strip()
    if max_price and max_price.isdigit():
        queryset = queryset.filter(price__lte=int(max_price))

    # Bedrooms filter
    bedrooms = request.GET.get('bedrooms', '').strip()
    if bedrooms:
        if bedrooms == '5+':
            queryset = queryset.filter(bedrooms__gte=5)
        elif bedrooms.isdigit():
            queryset = queryset.filter(bedrooms=int(bedrooms))

    # Bathrooms filter
    bathrooms = request.GET.get('bathrooms', '').strip()
    if bathrooms and bathrooms.isdigit():
        queryset = queryset.filter(bathrooms__gte=int(bathrooms))

    # Furnished status
    furnished = request.GET.get('furnished_status', '').strip()
    if furnished in ['unfurnished', 'semi_furnished', 'fully_furnished']:
        queryset = queryset.filter(furnished_status=furnished)

    # Amenities filter (multiple checkboxes)
    selected_amenities = request.GET.getlist('amenities')
    if selected_amenities:
        for amenity_id in selected_amenities:
            if amenity_id.isdigit():
                queryset = queryset.filter(amenities__id=int(amenity_id))

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

    # Context helpers
    categories = PropertyCategory.objects.filter(is_active=True)
    all_amenities = Amenity.objects.all()

    # Build clean query parameters for pagination links without losing filters
    params = request.GET.copy()
    if 'page' in params:
        del params['page']
    pagination_query = params.urlencode()

    context = {
        'properties': page_obj,
        'page_obj': page_obj,
        'total_count': paginator.count,
        'categories': categories,
        'all_amenities': all_amenities,
        'nigerian_states': NIGERIAN_STATES,
        'q': q,
        'current_state': state,
        'current_city': city,
        'current_neighbourhood': neighbourhood,
        'current_purpose': purpose,
        'current_category': category_id,
        'current_property_type': property_type,
        'min_price': min_price,
        'max_price': max_price,
        'current_bedrooms': bedrooms,
        'current_bathrooms': bathrooms,
        'current_furnished': furnished,
        'selected_amenities': [int(x) for x in selected_amenities if x.isdigit()],
        'current_sort': sort_by,
        'pagination_query': pagination_query,
    }
    return render(request, 'search/results.html', context)
