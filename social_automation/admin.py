from django.contrib import admin
from .models import Platform, SocialProfile, Schedule, FollowTask, Analytics

@admin.register(Platform)
class PlatformAdmin(admin.ModelAdmin):
    list_display = ('name', 'icon', 'created_at', 'updated_at')
    search_fields = ('name',)

@admin.register(SocialProfile)
class SocialProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'platform', 'username', 'created_at', 'updated_at')
    list_filter = ('platform', 'created_at')
    search_fields = ('user__username', 'username', 'platform__name')
    raw_id_fields = ('user',)

@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = ('user', 'platform', 'action', 'target_count', 'start_time', 'end_time', 'is_active')
    list_filter = ('platform', 'action', 'is_active', 'created_at')
    search_fields = ('user__username', 'platform__name')
    raw_id_fields = ('user', 'social_profile')

@admin.register(FollowTask)
class FollowTaskAdmin(admin.ModelAdmin):
    list_display = ('user', 'platform', 'action', 'target_username', 'status', 'created_at')
    list_filter = ('platform', 'action', 'status', 'created_at')
    search_fields = ('user__username', 'target_username', 'platform__name')
    raw_id_fields = ('user', 'social_profile')
    readonly_fields = ('error_message',)

@admin.register(Analytics)
class AnalyticsAdmin(admin.ModelAdmin):
    list_display = ('user', 'platform', 'date', 'followers_count', 'following_count', 'engagement_rate')
    list_filter = ('platform', 'date')
    search_fields = ('user__username', 'platform__name')
    raw_id_fields = ('user', 'social_profile')
    date_hierarchy = 'date'
