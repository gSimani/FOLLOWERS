from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Count
from .models import Platform, SocialProfile, Schedule, FollowTask, Analytics, AutomationTask, TargetURL
from .forms import CustomUserCreationForm, SocialProfileForm, ScheduleForm, FollowTaskForm
from .tasks import schedule_automation_task
from django.views.decorators.http import require_http_methods
import psycopg2
import redis
from selenium import webdriver
from django.conf import settings
import requests

def signup(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Account created successfully!')
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})

@login_required
def dashboard(request):
    platforms = Platform.objects.annotate(
        profile_count=Count('socialprofile', filter={'socialprofile__user': request.user})
    )
    active_schedules = Schedule.objects.filter(user=request.user, is_active=True).count()
    total_tasks = FollowTask.objects.filter(user=request.user).count()
    completed_tasks = FollowTask.objects.filter(user=request.user, status='completed').count()

    context = {
        'platforms': platforms,
        'active_schedules': active_schedules,
        'total_tasks': total_tasks,
        'completed_tasks': completed_tasks,
    }
    return render(request, 'social_automation/dashboard.html', context)

@login_required
def platform_detail(request, platform_id):
    platform = get_object_or_404(Platform, id=platform_id)
    social_profiles = SocialProfile.objects.filter(user=request.user, platform=platform)
    
    if request.method == 'POST':
        form = SocialProfileForm(request.POST)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = request.user
            profile.platform = platform
            profile.save()
            messages.success(request, f'Profile added for {platform.name}!')
            return redirect('platform_detail', platform_id=platform_id)
    else:
        form = SocialProfileForm()
    
    context = {
        'platform': platform,
        'social_profiles': social_profiles,
        'form': form,
    }
    return render(request, 'social_automation/platform_detail.html', context)

@login_required
def schedule_list(request):
    schedules = Schedule.objects.filter(user=request.user)
    
    if request.method == 'POST':
        form = ScheduleForm(request.user, request.POST)
        if form.is_valid():
            schedule = form.save(commit=False)
            schedule.user = request.user
            schedule.save()
            messages.success(request, 'Schedule created successfully!')
            return redirect('schedule_list')
    else:
        form = ScheduleForm(request.user)
    
    context = {
        'schedules': schedules,
        'form': form,
    }
    return render(request, 'social_automation/schedule_list.html', context)

@login_required
def task_list(request):
    tasks = FollowTask.objects.filter(user=request.user).order_by('-created_at')
    
    if request.method == 'POST':
        form = FollowTaskForm(request.user, request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.user = request.user
            task.save()
            messages.success(request, 'Task created successfully!')
            return redirect('task_list')
    else:
        form = FollowTaskForm(request.user)
    
    context = {
        'tasks': tasks,
        'form': form,
    }
    return render(request, 'social_automation/task_list.html', context)

@login_required
def analytics_dashboard(request):
    today = timezone.now().date()
    analytics = Analytics.objects.filter(
        user=request.user,
        date=today
    ).select_related('platform', 'social_profile')
    
    context = {
        'analytics': analytics,
    }
    return render(request, 'social_automation/analytics_dashboard.html', context)

@login_required
def delete_profile(request, profile_id):
    profile = get_object_or_404(SocialProfile, id=profile_id, user=request.user)
    platform_id = profile.platform.id
    profile.delete()
    messages.success(request, 'Profile deleted successfully!')
    return redirect('platform_detail', platform_id=platform_id)

@login_required
def delete_schedule(request, schedule_id):
    schedule = get_object_or_404(Schedule, id=schedule_id, user=request.user)
    schedule.delete()
    messages.success(request, 'Schedule deleted successfully!')
    return redirect('schedule_list')

@login_required
def toggle_schedule(request, schedule_id):
    schedule = get_object_or_404(Schedule, id=schedule_id, user=request.user)
    schedule.is_active = not schedule.is_active
    schedule.save()
    return JsonResponse({'status': 'success', 'is_active': schedule.is_active})

PLATFORM_CONFIGS = {
    'instagram': {
        'name': 'Instagram',
        'icon': 'fab fa-instagram',
        'icon_class': 'bg-gradient-to-r from-purple-500 to-pink-500'
    },
    'facebook': {
        'name': 'Facebook',
        'icon': 'fab fa-facebook-f',
        'icon_class': 'bg-blue-600'
    },
    'twitter': {
        'name': 'Twitter',
        'icon': 'fab fa-twitter',
        'icon_class': 'bg-blue-400'
    },
    'linkedin': {
        'name': 'LinkedIn',
        'icon': 'fab fa-linkedin-in',
        'icon_class': 'bg-blue-700'
    },
    'youtube': {
        'name': 'YouTube',
        'icon': 'fab fa-youtube',
        'icon_class': 'bg-red-600'
    },
    'pinterest': {
        'name': 'Pinterest',
        'icon': 'fab fa-pinterest-p',
        'icon_class': 'bg-red-700'
    },
    'substack': {
        'name': 'Substack',
        'icon': 'fas fa-newspaper',
        'icon_class': 'bg-orange-500'
    }
}

@login_required
def platform_selection(request):
    """Display the platform selection interface."""
    return render(request, 'social_automation/platform_selection.html')

@login_required
def automation_interface(request, platform):
    """Display the automation interface for a specific platform."""
    if platform not in PLATFORM_CONFIGS:
        return JsonResponse({'error': 'Invalid platform'}, status=400)
    
    context = {
        'platform_name': PLATFORM_CONFIGS[platform]['name'],
        'platform_icon': PLATFORM_CONFIGS[platform]['icon'],
        'platform_icon_class': PLATFORM_CONFIGS[platform]['icon_class'],
        'saved_urls': TargetURL.objects.filter(user=request.user, platform=platform)
    }
    return render(request, 'social_automation/automation_interface.html', context)

@login_required
@require_http_methods(['POST'])
def create_automation(request, platform):
    """Create a new automation task."""
    try:
        data = request.POST
        action = data.get('action')
        target_url = data.get('profile_url')
        target_type = data.get('target')
        quantity = int(data.get('quantity', 50))
        
        if not all([action, target_url, target_type]):
            return JsonResponse({
                'error': 'Missing required fields'
            }, status=400)
            
        # Create or get target URL
        target_url_obj, _ = TargetURL.objects.get_or_create(
            user=request.user,
            platform=platform,
            url=target_url
        )
        
        # Create automation task
        task = AutomationTask.objects.create(
            user=request.user,
            platform=platform,
            action=action,
            target_url=target_url_obj,
            target_type=target_type,
            quantity=quantity
        )
        
        # Schedule the task
        schedule_automation_task(task.id)
        
        return JsonResponse({
            'message': 'Automation task created successfully',
            'task_id': task.id
        })
        
    except Exception as e:
        return JsonResponse({
            'error': str(e)
        }, status=500)

@login_required
@require_http_methods(['GET'])
def get_saved_urls(request, platform):
    """Get saved URLs for a platform."""
    urls = TargetURL.objects.filter(
        user=request.user,
        platform=platform
    ).values('id', 'url', 'created_at')
    
    return JsonResponse({
        'urls': list(urls)
    })

@login_required
@require_http_methods(['POST'])
def save_url(request, platform):
    """Save a new target URL."""
    url = request.POST.get('url')
    if not url:
        return JsonResponse({
            'error': 'URL is required'
        }, status=400)
        
    url_obj, created = TargetURL.objects.get_or_create(
        user=request.user,
        platform=platform,
        url=url
    )
    
    return JsonResponse({
        'message': 'URL saved successfully',
        'url_id': url_obj.id,
        'created': created
    })

@login_required
@require_http_methods(['DELETE'])
def delete_url(request, platform, url_id):
    """Delete a saved URL."""
    try:
        url = TargetURL.objects.get(
            id=url_id,
            user=request.user,
            platform=platform
        )
        url.delete()
        return JsonResponse({
            'message': 'URL deleted successfully'
        })
    except TargetURL.DoesNotExist:
        return JsonResponse({
            'error': 'URL not found'
        }, status=404)

@login_required
@require_http_methods(['GET'])
def get_task_progress(request, task_id):
    """Get detailed progress for a specific task."""
    try:
        task = AutomationTask.objects.get(id=task_id, user=request.user)
        
        # Get the latest progress logs
        progress_logs = task.progress_logs.all()[:50]  # Get last 50 logs
        
        response_data = {
            'task_id': task.id,
            'status': task.status,
            'total_processed': task.total_processed,
            'total_succeeded': task.total_succeeded,
            'total_failed': task.total_failed,
            'progress_percentage': task.progress_percentage,
            'started_at': task.started_at.isoformat() if task.started_at else None,
            'completed_at': task.completed_at.isoformat() if task.completed_at else None,
            'error_message': task.error_message,
            'progress_logs': [
                {
                    'action': log.action,
                    'target_username': log.target_username,
                    'status': log.status,
                    'error_message': log.error_message,
                    'created_at': log.created_at.isoformat()
                }
                for log in progress_logs
            ]
        }
        
        return JsonResponse(response_data)
        
    except AutomationTask.DoesNotExist:
        return JsonResponse({
            'error': 'Task not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'error': str(e)
        }, status=500)

def test_page(request):
    """Simple test page to verify server is working"""
    return render(request, 'social_automation/test.html', {
        'title': 'Instagram Automation Test'
    })

def test_database_connection(request):
    """Test database connection"""
    try:
        conn = psycopg2.connect(
            dbname=settings.DATABASES['default']['NAME'],
            user=settings.DATABASES['default']['USER'],
            password=settings.DATABASES['default']['PASSWORD'],
            host=settings.DATABASES['default']['HOST'],
            port=settings.DATABASES['default']['PORT']
        )
        conn.close()
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

def test_redis_connection(request):
    """Test Redis connection"""
    try:
        r = redis.from_url(settings.CELERY_BROKER_URL)
        r.ping()
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

def test_selenium_setup(request):
    """Test Selenium setup"""
    try:
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        driver = webdriver.Chrome(options=options)
        driver.quit()
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

def test_instagram_connection(request):
    """Test Instagram accessibility"""
    try:
        response = requests.get('https://www.instagram.com', timeout=5)
        return JsonResponse({
            'success': response.status_code == 200,
            'status_code': response.status_code
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@require_http_methods(['POST'])
def test_instagram_login(request):
    """Test Instagram login"""
    try:
        from .scrapers.instagram import InstagramScraper
        scraper = InstagramScraper()
        success = scraper.login()
        scraper.cleanup()
        return JsonResponse({'success': success})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})
