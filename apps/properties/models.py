import uuid
import builtins
from django.db import models
from django.conf import settings
from django.utils.text import slugify
from django.utils import timezone


class PropertyCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    icon_name = models.CharField(max_length=50, default="home", help_text="Icon identifier e.g. home, building, warehouse, map")
    description = models.TextField(blank=True, default="")
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Property Category'
        verbose_name_plural = 'Property Categories'
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Amenity(models.Model):
    CATEGORY_CHOICES = (
        ('security', 'Security & Safety'),
        ('utility', 'Power & Utilities'),
        ('comfort', 'Comfort & Living'),
        ('luxury', 'Luxury & Recreation'),
    )
    name = models.CharField(max_length=100, unique=True)
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES, default='utility')
    icon_class = models.CharField(max_length=50, default="check-circle", blank=True)

    class Meta:
        verbose_name = 'Amenity'
        verbose_name_plural = 'Amenities'
        ordering = ['name']

    def __str__(self):
        return self.name


class Property(models.Model):
    class Purpose(models.TextChoices):
        FOR_SALE = 'for_sale', 'For Sale'
        FOR_RENT = 'for_rent', 'For Rent'

    class PropertyType(models.TextChoices):
        RESIDENTIAL = 'residential', 'Residential'
        COMMERCIAL = 'commercial', 'Commercial'
        LAND = 'land', 'Land / Plot'
        INDUSTRIAL = 'industrial', 'Industrial'

    class FurnishedStatus(models.TextChoices):
        UNFURNISHED = 'unfurnished', 'Unfurnished'
        SEMI_FURNISHED = 'semi_furnished', 'Semi-Furnished'
        FULLY_FURNISHED = 'fully_furnished', 'Fully Furnished'

    class PropertyCondition(models.TextChoices):
        BRAND_NEW = 'brand_new', 'Brand New'
        RENOVATED = 'renovated', 'Renovated'
        FAIRLY_USED = 'fairly_used', 'Fairly Used'

    class AvailabilityStatus(models.TextChoices):
        AVAILABLE = 'available', 'Available'
        UNDER_OFFER = 'under_offer', 'Under Offer'
        RENTED = 'rented', 'Rented'
        SOLD = 'sold', 'Sold'

    class ApprovalStatus(models.TextChoices):
        DRAFT = 'draft', 'Draft'
        PENDING = 'pending', 'Pending Approval'
        APPROVED = 'approved', 'Approved'
        REJECTED = 'rejected', 'Rejected'
        ARCHIVED = 'archived', 'Archived'

    class RentalFrequency(models.TextChoices):
        MONTHLY = 'monthly', 'Per Month'
        YEARLY = 'yearly', 'Per Annum (Yearly)'
        DAILY = 'daily', 'Short Let (Per Day)'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    agent = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='properties')
    category = models.ForeignKey(PropertyCategory, on_delete=models.PROTECT, related_name='properties')

    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=280, unique=True, blank=True)
    description = models.TextField()

    listing_purpose = models.CharField(max_length=20, choices=Purpose.choices, default=Purpose.FOR_RENT)
    property_type = models.CharField(max_length=20, choices=PropertyType.choices, default=PropertyType.RESIDENTIAL)

    # Location specifics in Nigeria
    state = models.CharField(max_length=100, db_index=True)
    lga = models.CharField(max_length=100, blank=True, default="")
    city = models.CharField(max_length=100, db_index=True)
    neighbourhood = models.CharField(max_length=150, db_index=True)
    street_address = models.CharField(max_length=255, blank=True, default="")
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    # Pricing
    price = models.DecimalField(max_digits=14, decimal_places=2, db_index=True)
    currency = models.CharField(max_length=10, default="NGN")
    rental_frequency = models.CharField(max_length=20, choices=RentalFrequency.choices, blank=True, null=True)
    is_negotiable = models.BooleanField(default=False)

    # Specifications
    bedrooms = models.PositiveIntegerField(default=1)
    bathrooms = models.PositiveIntegerField(default=1)
    toilets = models.PositiveIntegerField(default=1)
    parking_spaces = models.PositiveIntegerField(default=1)
    property_size = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Size in square meters (sqm)")
    furnished_status = models.CharField(max_length=20, choices=FurnishedStatus.choices, default=FurnishedStatus.UNFURNISHED)
    property_condition = models.CharField(max_length=20, choices=PropertyCondition.choices, default=PropertyCondition.BRAND_NEW)

    # Amenities
    amenities = models.ManyToManyField(Amenity, blank=True, related_name='properties')

    # Media & Highlights
    featured_image = models.ImageField(upload_to='properties/', blank=True, null=True)
    is_featured = models.BooleanField(default=False, help_text="Show in homepage featured spotlight.")

    # Statuses & Workflow
    availability_status = models.CharField(max_length=20, choices=AvailabilityStatus.choices, default=AvailabilityStatus.AVAILABLE, db_index=True)
    approval_status = models.CharField(max_length=20, choices=ApprovalStatus.choices, default=ApprovalStatus.PENDING, db_index=True)
    rejection_reason = models.TextField(blank=True, default="")

    view_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'Property'
        verbose_name_plural = 'Properties'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['approval_status', 'availability_status']),
            models.Index(fields=['state', 'city', 'neighbourhood']),
            models.Index(fields=['listing_purpose', 'price']),
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(f"{self.title}-{self.city}-{self.state}")
            slug = base_slug
            counter = 1
            while Property.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug

        if self.approval_status == self.ApprovalStatus.APPROVED and not self.published_at:
            self.published_at = timezone.now()

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} - {self.neighbourhood}, {self.city} (₦{self.price:,.2f})"

    @property
    def formatted_price(self):
        return f"₦{self.price:,.0f}"

    @property
    def price_display(self):
        freq = f" / {self.get_rental_frequency_display()}" if self.rental_frequency and self.listing_purpose == self.Purpose.FOR_RENT else ""
        return f"{self.formatted_price}{freq}"

    @property
    def is_public(self):
        return self.approval_status == self.ApprovalStatus.APPROVED and self.availability_status == self.AvailabilityStatus.AVAILABLE

    @property
    def primary_image_url(self):
        if self.featured_image:
            name = str(self.featured_image.name if hasattr(self.featured_image, 'name') else self.featured_image)
            if name.startswith(('http://', 'https://', '//', '/static/')):
                return name
            try:
                return self.featured_image.url
            except Exception:
                return "/static/icons/property-placeholder.svg"

        first_img = self.images.filter(is_featured=True).first() or self.images.first()
        if first_img and first_img.image:
            name = str(first_img.image.name if hasattr(first_img.image, 'name') else first_img.image)
            if name.startswith(('http://', 'https://', '//', '/static/')):
                return name
            try:
                return first_img.image.url
            except Exception:
                return "/static/icons/property-placeholder.svg"
        return "/static/icons/property-placeholder.svg"


class PropertyImage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='properties/')
    caption = models.CharField(max_length=200, blank=True, default="")
    is_featured = models.BooleanField(default=False)
    display_order = models.PositiveIntegerField(default=0)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Property Photograph'
        verbose_name_plural = 'Property Photographs'
        ordering = ['display_order', '-is_featured', 'uploaded_at']

    @builtins.property
    def image_url(self):
        if self.image:
            name = str(self.image.name if hasattr(self.image, 'name') else self.image)
            if name.startswith(('http://', 'https://', '//', '/static/')):
                return name
            try:
                return self.image.url
            except Exception:
                return "/static/icons/property-placeholder.svg"
        return "/static/icons/property-placeholder.svg"

    def __str__(self):
        return f"Photo for {self.property.title}"


class PropertyReport(models.Model):
    REASON_CHOICES = (
        ('fraud', 'Suspected Fraud or Scam Listing'),
        ('incorrect_price', 'Incorrect or Manipulated Price'),
        ('duplicate', 'Duplicate Listing'),
        ('unavailable', 'Property is No Longer Available'),
        ('offensive', 'Inappropriate or Offensive Content'),
    )
    STATUS_CHOICES = (
        ('pending', 'Pending Investigation'),
        ('reviewed', 'Reviewed'),
        ('dismissed', 'Dismissed'),
        ('action_taken', 'Action Taken (Listing Removed/Archived)'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='reports')
    reporter = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    reporter_name = models.CharField(max_length=150, blank=True, default="")
    reporter_email = models.EmailField(blank=True, default="")
    reason = models.CharField(max_length=30, choices=REASON_CHOICES)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Property Report'
        verbose_name_plural = 'Property Reports'
        ordering = ['-created_at']

    def __str__(self):
        return f"Report on {self.property.title} ({self.get_reason_display()})"
