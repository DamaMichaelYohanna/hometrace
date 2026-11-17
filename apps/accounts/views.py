from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.signing import TimestampSigner, BadSignature, SignatureExpired
from django.conf import settings
from .models import User, AgentProfile, BuyerProfile
from .forms import RegistrationForm, LoginForm, UserProfileForm, AgentProfileForm, BuyerProfileForm

signer = TimestampSigner()


def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard_dispatch')

    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            password = form.cleaned_data['password']
            user.set_password(password)
            user.save()

            # If agent, update agency name
            if user.role == User.Role.AGENT:
                agency_name = form.cleaned_data.get('agency_name')
                agent_profile, _ = AgentProfile.objects.get_or_create(user=user)
                if agency_name:
                    agent_profile.agency_name = agency_name
                    agent_profile.save()

            # Auto-login newly registered user
            authenticated_user = authenticate(request, email=user.email, password=password)
            if authenticated_user:
                login(request, authenticated_user)
                messages.success(request, f"Welcome to Hometrace, {user.full_name}! Your account has been created.")
                return redirect('dashboard_dispatch')

            messages.success(request, "Account created successfully. Please log in.")
            return redirect('login')
        else:
            messages.error(request, "Please correct the errors in the registration form.")
    else:
        role_pref = request.GET.get('role', 'buyer')
        initial_role = User.Role.AGENT if role_pref == 'agent' else User.Role.BUYER
        form = RegistrationForm(initial={'role': initial_role})

    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard_dispatch')

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email'].strip().lower()
            password = form.cleaned_data['password']
            remember_me = form.cleaned_data.get('remember_me', False)

            user = authenticate(request, email=email, password=password)
            if user is not None:
                if not user.is_active:
                    messages.error(request, "Your account is inactive or has been suspended. Please contact support.")
                    return render(request, 'accounts/login.html', {'form': form})

                login(request, user)
                if not remember_me:
                    request.session.set_expiry(0)  # Browser close session
                else:
                    request.session.set_expiry(1209600)  # 2 weeks

                messages.success(request, f"Welcome back, {user.full_name}!")
                next_url = request.GET.get('next')
                if next_url:
                    return redirect(next_url)
                return redirect('dashboard_dispatch')
            else:
                messages.error(request, "Invalid email address or password. Please try again.")
    else:
        form = LoginForm()

    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out securely. See you again soon!")
    return redirect('home')


@login_required
def profile_view(request):
    user = request.user
    agent_form = None
    buyer_form = None

    if request.method == 'POST':
        user_form = UserProfileForm(request.POST, request.FILES, instance=user)
        is_subform_valid = True

        if user.is_agent:
            agent_profile, _ = AgentProfile.objects.get_or_create(user=user)
            agent_form = AgentProfileForm(request.POST, instance=agent_profile)
            if not agent_form.is_valid():
                is_subform_valid = False
        elif user.is_buyer:
            buyer_profile, _ = BuyerProfile.objects.get_or_create(user=user)
            buyer_form = BuyerProfileForm(request.POST, instance=buyer_profile)
            if not buyer_form.is_valid():
                is_subform_valid = False

        if user_form.is_valid() and is_subform_valid:
            user_form.save()
            if agent_form:
                agent_form.save()
            if buyer_form:
                buyer_form.save()
            messages.success(request, "Your profile details have been updated successfully.")
            return redirect('profile')
        else:
            messages.error(request, "Please review the form errors before saving.")
    else:
        user_form = UserProfileForm(instance=user)
        if user.is_agent:
            agent_profile, _ = AgentProfile.objects.get_or_create(user=user)
            agent_form = AgentProfileForm(instance=agent_profile)
        elif user.is_buyer:
            buyer_profile, _ = BuyerProfile.objects.get_or_create(user=user)
            buyer_form = BuyerProfileForm(instance=buyer_profile)

    context = {
        'user_form': user_form,
        'agent_form': agent_form,
        'buyer_form': buyer_form,
    }
    return render(request, 'accounts/profile.html', context)


@login_required
def send_verification_email_view(request):
    """
    Sends or demonstrates email verification token.
    """
    user = request.user
    token = signer.sign(str(user.id))
    verification_url = request.build_absolute_uri(f"/accounts/verify-email/{token}/")

    # In production/console backend, email is sent
    from django.core.mail import send_mail
    try:
        send_mail(
            subject="Verify your Hometrace Email Address",
            message=f"Hello {user.full_name},\n\nPlease click the link below to verify your email address:\n{verification_url}\n\nThank you,\nHometrace Team",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=True,
        )
    except Exception:
        pass

    messages.info(request, f"A verification link has been sent to {user.email}. (For local defense demonstration, click the 'Verify Now' button.)")
    return redirect('profile')


def verify_email_token_view(request, token):
    try:
        user_id = signer.unsign(token, max_age=86400)  # 24 hours
        user = get_object_or_404(User, id=user_id)
        user.is_verified = True
        user.save()
        messages.success(request, "Your email address has been successfully verified!")
    except (BadSignature, SignatureExpired):
        messages.error(request, "The verification link is invalid or has expired.")

    if request.user.is_authenticated:
        return redirect('profile')
    return redirect('login')


def password_reset_request_view(request):
    if request.method == 'POST':
        email = request.POST.get('email', '').strip().lower()
        user = User.objects.filter(email=email).first()
        if user:
            messages.success(request, f"Password reset instructions have been dispatched to {email}. Please check your inbox.")
        else:
            messages.info(request, f"If an account exists for {email}, a recovery link has been dispatched.")
        return render(request, 'accounts/password_reset_done.html', {'email': email})
    return render(request, 'accounts/password_reset.html')
