from django.contrib import admin
from .models import SocialProfile, AutomationTask, TargetUser

@admin.register(SocialProfile)
class SocialProfileAdmin(admin.ModelAdmin):
    list_display = ('username', 'platform', 'user', 'is_active', 'created_at')
    list_filter = ('platform', 'is_active')
    search_fields = ('username', 'user__username')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(AutomationTask)
class AutomationTaskAdmin(admin.ModelAdmin):
    list_display = ('profile', 'action', 'status', 'progress', 'created_at')
    list_filter = ('action', 'status')
    search_fields = ('profile__username', 'target_url')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(TargetUser)
class TargetUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'task', 'action_taken', 'action_date')
    list_filter = ('action_taken',)
    search_fields = ('username', 'task__profile__username')
    readonly_fields = ('action_date',) 