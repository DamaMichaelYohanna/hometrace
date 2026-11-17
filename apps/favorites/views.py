from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages
from properties.models import Property
from .models import Favorite


@login_required
def favorites_list_view(request):
    """
    Displays all properties saved by the logged-in buyer/renter.
    """
    favorites = Favorite.objects.filter(user=request.user).select_related(
        'property', 'property__category', 'property__agent'
    ).prefetch_related('property__images')

    return render(request, 'favorites/list.html', {'favorites': favorites})


@login_required
def toggle_favorite_view(request, property_id):
    """
    Toggles bookmark status. Works seamlessly with both AJAX (JSON) and standard form redirects.
    """
    prop = get_object_or_404(Property, id=property_id)
    favorite = Favorite.objects.filter(user=request.user, property=prop).first()

    if favorite:
        favorite.delete()
        saved = False
        msg = f"'{prop.title}' removed from your saved properties."
    else:
        Favorite.objects.create(user=request.user, property=prop)
        saved = True
        msg = f"'{prop.title}' added to your saved properties."

    total_favs = Favorite.objects.filter(user=request.user).count()

    # Check if AJAX request
    if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.GET.get('format') == 'json':
        return JsonResponse({
            'saved': saved,
            'message': msg,
            'total_favorites': total_favs,
            'property_id': str(property_id),
        })

    messages.success(request, msg)
    next_url = request.META.get('HTTP_REFERER') or 'favorites_list'
    return redirect(next_url)
