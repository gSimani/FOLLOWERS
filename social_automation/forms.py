from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import SocialProfile, Schedule, FollowTask

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user

class SocialProfileForm(forms.ModelForm):
    class Meta:
        model = SocialProfile
        fields = ['platform', 'profile_url', 'username']
        widgets = {
            'profile_url': forms.URLInput(attrs={'class': 'form-input'}),
            'username': forms.TextInput(attrs={'class': 'form-input'}),
        }

class ScheduleForm(forms.ModelForm):
    class Meta:
        model = Schedule
        fields = ['platform', 'social_profile', 'action', 'target_count', 'start_time', 'end_time']
        widgets = {
            'start_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-input'}),
            'end_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-input'}),
            'target_count': forms.NumberInput(attrs={'class': 'form-input'}),
        }

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['social_profile'].queryset = SocialProfile.objects.filter(user=user)

class FollowTaskForm(forms.ModelForm):
    class Meta:
        model = FollowTask
        fields = ['platform', 'social_profile', 'action', 'target_username']
        widgets = {
            'target_username': forms.TextInput(attrs={'class': 'form-input'}),
        }

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['social_profile'].queryset = SocialProfile.objects.filter(user=user) 