"""
Global context processors for Hometrace application.
"""
from django.conf import settings


def global_context(request):
    """
    Exposes platform-level context variables across all Django templates.
    """
    context = {
        'APP_NAME': 'Hometrace',
        'APP_TAGLINE': 'Find Your Next Home, Without the Stress',
        'PAYSTACK_PUBLIC_KEY': getattr(settings, 'PAYSTACK_PUBLIC_KEY', ''),
        'CURRENCY_SYMBOL': '₦',
        'unread_notifications_count': 0,
        'unread_messages_count': 0,
        'user_favorites_count': 0,
        'user_favorite_property_ids': [],
    }

    if request.user.is_authenticated:
        try:
            from notifications.models import Notification
            context['unread_notifications_count'] = Notification.objects.filter(
                user=request.user, is_read=False
            ).count()
        except Exception:
            pass

        try:
            from messaging.models import Message
            context['unread_messages_count'] = Message.objects.filter(
                conversation__in=request.user.conversations_as_buyer.all() | request.user.conversations_as_agent.all(),
                is_read=False
            ).exclude(sender=request.user).count()
        except Exception:
            pass

        try:
            from favorites.models import Favorite
            favs = Favorite.objects.filter(user=request.user)
            context['user_favorites_count'] = favs.count()
            context['user_favorite_property_ids'] = list(favs.values_list('property_id', flat=True))
        except Exception:
            pass

    return context
