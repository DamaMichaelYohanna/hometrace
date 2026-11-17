from django import forms
from .models import Property, PropertyImage, PropertyCategory, Amenity, PropertyReport

# List of all 36 Nigerian States + FCT for dropdown selection
NIGERIAN_STATES = [
    ('', 'Select Nigerian State'),
    ('Abuja FCT', 'Abuja FCT'),
    ('Abia', 'Abia'),
    ('Adamawa', 'Adamawa'),
    ('Akwa Ibom', 'Akwa Ibom'),
    ('Anambra', 'Anambra'),
    ('Bauchi', 'Bauchi'),
    ('Bayelsa', 'Bayelsa'),
    ('Benue', 'Benue'),
    ('Borno', 'Borno'),
    ('Cross River', 'Cross River'),
    ('Delta', 'Delta'),
    ('Ebonyi', 'Ebonyi'),
    ('Edo', 'Edo'),
    ('Ekiti', 'Ekiti'),
    ('Enugu', 'Enugu'),
    ('Gombe', 'Gombe'),
    ('Imo', 'Imo'),
    ('Jigawa', 'Jigawa'),
    ('Kaduna', 'Kaduna'),
    ('Kano', 'Kano'),
    ('Katsina', 'Katsina'),
    ('Kebbi', 'Kebbi'),
    ('Kogi', 'Kogi'),
    ('Kwara', 'Kwara'),
    ('Lagos', 'Lagos'),
    ('Nasarawa', 'Nasarawa'),
    ('Niger', 'Niger'),
    ('Ogun', 'Ogun'),
    ('Ondo', 'Ondo'),
    ('Osun', 'Osun'),
    ('Oyo', 'Oyo'),
    ('Plateau', 'Plateau'),
    ('Rivers', 'Rivers'),
    ('Sokoto', 'Sokoto'),
    ('Taraba', 'Taraba'),
    ('Yobe', 'Yobe'),
    ('Zamfara', 'Zamfara'),
]


class PropertyForm(forms.ModelForm):
    state = forms.ChoiceField(choices=NIGERIAN_STATES, widget=forms.Select(attrs={'class': 'form-input'}))
    amenities = forms.ModelMultipleChoiceField(
        queryset=Amenity.objects.all(),
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'checkbox-item'}),
        required=False
    )

    class Meta:
        model = Property
        fields = [
            'title', 'category', 'listing_purpose', 'property_type',
            'state', 'lga', 'city', 'neighbourhood', 'street_address',
            'price', 'rental_frequency', 'is_negotiable',
            'bedrooms', 'bathrooms', 'toilets', 'parking_spaces',
            'property_size', 'furnished_status', 'property_condition',
            'amenities', 'description', 'featured_image'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'e.g. Luxury 4-Bedroom Fully Detached Duplex with BQ', 'class': 'form-input'}),
            'category': forms.Select(attrs={'class': 'form-input'}),
            'listing_purpose': forms.Select(attrs={'class': 'form-input', 'id': 'purpose-selector'}),
            'property_type': forms.Select(attrs={'class': 'form-input'}),
            'lga': forms.TextInput(attrs={'placeholder': 'e.g. Keffi', 'class': 'form-input'}),
            'city': forms.TextInput(attrs={'placeholder': 'e.g. Keffi', 'class': 'form-input'}),
            'neighbourhood': forms.TextInput(attrs={'placeholder': 'e.g. Angwan Lambu / GRA / FMC Road', 'class': 'form-input'}),
            'street_address': forms.TextInput(attrs={'placeholder': 'e.g. Near NSUK Main Gate, University Road', 'class': 'form-input'}),
            'price': forms.NumberInput(attrs={'placeholder': 'Amount in Nigerian Naira (₦)', 'class': 'form-input'}),
            'rental_frequency': forms.Select(attrs={'class': 'form-input', 'id': 'frequency-selector'}),
            'is_negotiable': forms.CheckboxInput(attrs={'class': 'checkbox-input'}),
            'bedrooms': forms.NumberInput(attrs={'class': 'form-input', 'min': 0}),
            'bathrooms': forms.NumberInput(attrs={'class': 'form-input', 'min': 0}),
            'toilets': forms.NumberInput(attrs={'class': 'form-input', 'min': 0}),
            'parking_spaces': forms.NumberInput(attrs={'class': 'form-input', 'min': 0}),
            'property_size': forms.NumberInput(attrs={'placeholder': 'Area in sqm', 'class': 'form-input', 'step': '0.1'}),
            'furnished_status': forms.Select(attrs={'class': 'form-input'}),
            'property_condition': forms.Select(attrs={'class': 'form-input'}),
            'description': forms.Textarea(attrs={'rows': 6, 'placeholder': 'Provide detailed property description, title documents (C of O, Governor\'s Consent), unique selling points...', 'class': 'form-input'}),
            'featured_image': forms.FileInput(attrs={'class': 'file-input', 'accept': 'image/*'}),
        }


class MultipleFileInput(forms.FileInput):
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput(attrs={'class': 'file-input', 'accept': 'image/*'}))
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = [single_file_clean(data, initial)]
        return result


class PropertyImageUploadForm(forms.Form):
    images = MultipleFileField(
        required=False,
        help_text="You can select multiple photos at once."
    )


class PropertyReportForm(forms.ModelForm):
    class Meta:
        model = PropertyReport
        fields = ['reason', 'reporter_name', 'reporter_email', 'description']
        widgets = {
            'reason': forms.Select(attrs={'class': 'form-input'}),
            'reporter_name': forms.TextInput(attrs={'placeholder': 'Your Full Name', 'class': 'form-input'}),
            'reporter_email': forms.EmailInput(attrs={'placeholder': 'Your Email Address', 'class': 'form-input'}),
            'description': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Describe your concern or the nature of misleading information...', 'class': 'form-input'}),
        }
