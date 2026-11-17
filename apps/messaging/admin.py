from django.contrib import admin
from .models import Conversation, Message, Enquiry


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ('id', 'buyer', 'agent', 'property', 'updated_at')
    search_fields = ('buyer__email', 'agent__email', 'property__title')


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'conversation', 'sender', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at')
    search_fields = ('sender__email', 'body')


@admin.register(Enquiry)
class EnquiryAdmin(admin.ModelAdmin):
    list_display = ('subject', 'buyer', 'agent', 'property', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('buyer__email', 'agent__email', 'property__title', 'message')
