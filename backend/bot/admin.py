from django.contrib import admin
from .models import User, AudioMessage, Conversation

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['id', 'line_user_id', 'display_name', 'created_at']
    search_fields = ['line_user_id', 'display_name']
    list_filter = ['created_at']

@admin.register(AudioMessage)
class AudioMessageAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'message_id', 'processed', 'created_at']
    list_filter = ['processed', 'created_at']
    search_fields = ['user__line_user_id', 'message_id']

@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'message', 'is_from_user', 'created_at']
    list_filter = ['is_from_user', 'created_at']
    search_fields = ['user__line_user_id', 'message']
