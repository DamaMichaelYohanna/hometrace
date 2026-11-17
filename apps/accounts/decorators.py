from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.core.exceptions import PermissionDenied


def agent_required(view_func):
    """
    Decorator for views that checks that the user is an active Property Agent.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.info(request, "Please log in as an agent to continue.")
            return redirect('login')
        if not (request.user.is_agent or request.user.is_administrator):
            messages.error(request, "Access restricted. You must have an Agent account to access this section.")
            return redirect('dashboard_dispatch')
        return view_func(request, *args, **kwargs)
    return _wrapped_view


def buyer_required(view_func):
    """
    Decorator for views that checks that the user is a Buyer or Renter.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.info(request, "Please log in to continue.")
            return redirect('login')
        if not (request.user.is_buyer or request.user.is_administrator):
            messages.error(request, "Access restricted to prospective buyers and renters.")
            return redirect('dashboard_dispatch')
        return view_func(request, *args, **kwargs)
    return _wrapped_view


def admin_required(view_func):
    """
    Decorator for views that checks that the user is a platform administrator.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.info(request, "Administrator credentials required.")
            return redirect('login')
        if not request.user.is_administrator:
            raise PermissionDenied("You do not have administrative clearance to access this portal.")
        return view_func(request, *args, **kwargs)
    return _wrapped_view
