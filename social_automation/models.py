from django.db import models
from django.contrib.auth.models import User

class Platform(models.Model):
    name = models.CharField(max_length=50, unique=True)
    icon = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class SocialProfile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    platform = models.ForeignKey(Platform, on_delete=models.CASCADE)
    profile_url = models.URLField()
    username = models.CharField(max_length=100)
    access_token = models.CharField(max_length=255, blank=True, null=True)
    access_token_secret = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'platform', 'username')

    def __str__(self):
        return f"{self.user.username} - {self.platform.name} - {self.username}"

class FollowTask(models.Model):
    ACTION_CHOICES = [
        ('follow', 'Follow'),
        ('unfollow', 'Unfollow'),
    ]
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    platform = models.ForeignKey(Platform, on_delete=models.CASCADE)
    social_profile = models.ForeignKey(SocialProfile, on_delete=models.CASCADE)
    action = models.CharField(max_length=10, choices=ACTION_CHOICES)
    target_username = models.CharField(max_length=100)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    error_message = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.action} - {self.target_username}"

class Schedule(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    platform = models.ForeignKey(Platform, on_delete=models.CASCADE)
    social_profile = models.ForeignKey(SocialProfile, on_delete=models.CASCADE)
    action = models.CharField(max_length=10, choices=FollowTask.ACTION_CHOICES)
    target_count = models.IntegerField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.platform.name} - {self.action}"

class Analytics(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    platform = models.ForeignKey(Platform, on_delete=models.CASCADE)
    social_profile = models.ForeignKey(SocialProfile, on_delete=models.CASCADE)
    date = models.DateField()
    followers_count = models.IntegerField()
    following_count = models.IntegerField()
    engagement_rate = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'platform', 'social_profile', 'date')

    def __str__(self):
        return f"{self.user.username} - {self.platform.name} - {self.date}"

class AutomationTask(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('scheduled', 'Scheduled'),
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    platform = models.CharField(max_length=50)
    action = models.CharField(max_length=20)
    target_url = models.ForeignKey(TargetURL, on_delete=models.CASCADE)
    target_type = models.CharField(max_length=20)  # 'followers' or 'following'
    quantity = models.IntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    error_message = models.TextField(blank=True, null=True)
    calendar_event_id = models.CharField(max_length=100, blank=True, null=True)
    total_processed = models.IntegerField(default=0)
    total_succeeded = models.IntegerField(default=0)
    total_failed = models.IntegerField(default=0)
    progress_percentage = models.FloatField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.platform} - {self.action} - {self.status}"

    def update_progress(self, processed=0, succeeded=0, failed=0):
        """Update task progress"""
        self.total_processed += processed
        self.total_succeeded += succeeded
        self.total_failed += failed
        if self.quantity > 0:
            self.progress_percentage = (self.total_processed / self.quantity) * 100
        self.save()

class TaskProgress(models.Model):
    task = models.ForeignKey(AutomationTask, on_delete=models.CASCADE, related_name='progress_logs')
    action = models.CharField(max_length=20)  # 'follow' or 'unfollow'
    target_username = models.CharField(max_length=100)
    status = models.CharField(max_length=20)  # 'success' or 'failed'
    error_message = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.task.platform} - {self.action} - {self.target_username} - {self.status}"
