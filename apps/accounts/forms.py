from django import forms
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from .models import User, AgentProfile, BuyerProfile, validate_nigerian_phone


class RegistrationForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Create strong password (min 8 characters)',
            'class': 'form-input',
            'id': 'reg-password'
        }),
        validators=[validate_password],
        label='Password'
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Re-enter your password',
            'class': 'form-input',
            'id': 'reg-confirm-password'
        }),
        label='Confirm Password'
    )
    agency_name = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'e.g. Apex Realty & Properties Ltd',
            'class': 'form-input',
            'id': 'reg-agency-name'
        }),
        label='Agency / Business Name (For Agents)'
    )
    agree_terms = forms.BooleanField(
        required=True,
        error_messages={'required': 'You must agree to the Terms of Service and Privacy Policy to proceed.'},
        label='I agree to Hometrace Terms and Conditions'
    )

    class Meta:
        model = User
        fields = ['full_name', 'email', 'phone_number', 'role']
        widgets = {
            'full_name': forms.TextInput(attrs={'placeholder': 'e.g. Chukwuma Adeleke', 'class': 'form-input'}),
            'email': forms.EmailInput(attrs={'placeholder': 'you@example.com', 'class': 'form-input'}),
            'phone_number': forms.TextInput(attrs={'placeholder': 'e.g. 08031234567 or +2348031234567', 'class': 'form-input'}),
            'role': forms.Select(attrs={'class': 'form-input', 'id': 'role-selector'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['role'].choices = [
            (User.Role.BUYER, 'Buyer / Renter (Searching for property)'),
            (User.Role.AGENT, 'Property Agent (Listing properties)'),
        ]

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip().lower()
        if User.objects.filter(email=email).exists():
            raise ValidationError('An account with this email address already exists.')
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        role = cleaned_data.get('role')
        agency_name = cleaned_data.get('agency_name')

        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', 'Passwords do not match.')

        if role == User.Role.AGENT and not agency_name:
            self.add_error('agency_name', 'Please provide your agency or business name.')

        return cleaned_data


class LoginForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'placeholder': 'name@domain.com',
            'class': 'form-input',
            'autocomplete': 'email'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'placeholder': '••••••••',
            'class': 'form-input',
            'autocomplete': 'current-password',
            'id': 'login-password'
        })
    )
    remember_me = forms.BooleanField(required=False, initial=True)


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['full_name', 'phone_number', 'profile_image']
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-input'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-input'}),
            'profile_image': forms.FileInput(attrs={'class': 'file-input'}),
        }


class AgentProfileForm(forms.ModelForm):
    class Meta:
        model = AgentProfile
        fields = [
            'agency_name', 'license_number', 'biography',
            'office_address', 'state', 'city', 'whatsapp_number'
        ]
        widgets = {
            'agency_name': forms.TextInput(attrs={'class': 'form-input'}),
            'license_number': forms.TextInput(attrs={'class': 'form-input'}),
            'biography': forms.Textarea(attrs={'class': 'form-input', 'rows': 4}),
            'office_address': forms.TextInput(attrs={'class': 'form-input'}),
            'state': forms.TextInput(attrs={'class': 'form-input'}),
            'city': forms.TextInput(attrs={'class': 'form-input'}),
            'whatsapp_number': forms.TextInput(attrs={'class': 'form-input'}),
        }


class BuyerProfileForm(forms.ModelForm):
    class Meta:
        model = BuyerProfile
        fields = ['preferred_state', 'preferred_city', 'max_budget']
        widgets = {
            'preferred_state': forms.TextInput(attrs={'class': 'form-input'}),
            'preferred_city': forms.TextInput(attrs={'class': 'form-input'}),
            'max_budget': forms.NumberInput(attrs={'class': 'form-input'}),
        }
