from django.contrib import admin
from .models import PropertyCategory, Amenity, Property, PropertyImage, PropertyReport


class PropertyImageInline(admin.TabularInline):
    model = PropertyImage
    extra = 1
    fields = ('image', 'caption', 'is_featured', 'display_order')


@admin.register(PropertyCategory)
class PropertyCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'icon_name', 'is_active')
    prepopulated_fields = {'slug': ('name',)}
    list_filter = ('is_active',)
    search_fields = ('name',)


@admin.register(Amenity)
class AmenityAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'icon_class')
    list_filter = ('category',)
    search_fields = ('name',)


@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = (
        'title', 'agent', 'category', 'listing_purpose',
        'state', 'city', 'price', 'availability_status', 'approval_status', 'created_at'
    )
    list_filter = ('approval_status', 'availability_status', 'listing_purpose', 'state', 'category')
    search_fields = ('title', 'description', 'city', 'neighbourhood', 'agent__email', 'agent__full_name')
    prepopulated_fields = {'slug': ('title',)}
    inlines = [PropertyImageInline]
    actions = ['approve_selected_properties', 'reject_selected_properties']

    @admin.action(description="Approve selected properties for public display")
    def approve_selected_properties(self, request, queryset):
        queryset.update(approval_status=Property.ApprovalStatus.APPROVED)
        self.message_user(request, f"{queryset.count()} properties have been approved.")

    @admin.action(description="Reject selected properties")
    def reject_selected_properties(self, request, queryset):
        queryset.update(approval_status=Property.ApprovalStatus.REJECTED)
        self.message_user(request, f"{queryset.count()} properties marked as rejected.")


@admin.register(PropertyImage)
class PropertyImageAdmin(admin.ModelAdmin):
    list_display = ('property', 'caption', 'is_featured', 'display_order', 'uploaded_at')
    list_filter = ('is_featured',)


@admin.register(PropertyReport)
class PropertyReportAdmin(admin.ModelAdmin):
    list_display = ('property', 'reporter_name', 'reason', 'status', 'created_at')
    list_filter = ('reason', 'status')
    search_fields = ('property__title', 'reporter_email', 'reporter_name', 'description')
