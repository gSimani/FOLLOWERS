from django.db import models
from django.contrib.auth.models import User

class SocialProfile(models.Model):
    PLATFORM_CHOICES = [
        ('instagram', 'Instagram'),
        ('twitter', 'Twitter'),
        ('tiktok', 'TikTok'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    platform = models.CharField(max_length=20, choices=PLATFORM_CHOICES)
    username = models.CharField(max_length=255)
    password = models.CharField(max_length=255)  # In production, use proper encryption
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['platform', 'username']
    
    def __str__(self):
        return f"{self.username} on {self.platform}"

class AutomationTask(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    ACTION_CHOICES = [
        ('follow', 'Follow'),
        ('unfollow', 'Unfollow'),
        ('like', 'Like'),
        ('comment', 'Comment'),
    ]
    
    profile = models.ForeignKey(SocialProfile, on_delete=models.CASCADE)
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    target_url = models.URLField()
    quantity = models.IntegerField(default=100)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    progress = models.IntegerField(default=0)
    error_message = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.action} task for {self.profile}"

class TargetUser(models.Model):
    task = models.ForeignKey(AutomationTask, on_delete=models.CASCADE)
    username = models.CharField(max_length=255)
    action_taken = models.BooleanField(default=False)
    action_date = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        unique_together = ['task', 'username']
    
    def __str__(self):
        return self.username 