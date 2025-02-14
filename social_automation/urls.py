from django.urls import path
from . import views

app_name = 'social_automation'

urlpatterns = [
    # Test page and API endpoints
    path('test/', views.test_page, name='test_page'),
    path('api/test-database/', views.test_database_connection, name='test_database'),
    path('api/test-redis/', views.test_redis_connection, name='test_redis'),
    path('api/test-selenium/', views.test_selenium_setup, name='test_selenium'),
    path('api/test-instagram/', views.test_instagram_connection, name='test_instagram'),
    path('api/test-instagram-login/', views.test_instagram_login, name='test_instagram_login'),
    
    # Platform selection and automation interface
    path('', views.platform_selection, name='platform_selection'),
    
    # Platform-specific automation interfaces
    path('instagram/', views.automation_interface, {'platform': 'instagram'}, name='automation_instagram'),
    path('twitter/', views.automation_interface, {'platform': 'twitter'}, name='automation_twitter'),
    path('linkedin/', views.automation_interface, {'platform': 'linkedin'}, name='automation_linkedin'),
    path('facebook/', views.automation_interface, {'platform': 'facebook'}, name='automation_facebook'),
    path('youtube/', views.automation_interface, {'platform': 'youtube'}, name='automation_youtube'),
    path('pinterest/', views.automation_interface, {'platform': 'pinterest'}, name='automation_pinterest'),
    path('substack/', views.automation_interface, {'platform': 'substack'}, name='automation_substack'),
    
    # Automation endpoints
    path('<str:platform>/automate/', views.create_automation, name='create_automation'),
    
    # URL management
    path('<str:platform>/urls/', views.get_saved_urls, name='get_saved_urls'),
    path('<str:platform>/urls/save/', views.save_url, name='save_url'),
    path('<str:platform>/urls/<int:url_id>/delete/', views.delete_url, name='delete_url'),
    
    # Task management
    path('tasks/', views.task_list, name='task_list'),
    path('tasks/<int:task_id>/cancel/', views.cancel_task, name='cancel_task'),
    path('tasks/<int:task_id>/retry/', views.retry_task, name='retry_task'),
    path('tasks/<int:task_id>/progress/', views.get_task_progress, name='task_progress'),
    
    # Schedule management
    path('schedules/', views.schedule_list, name='schedule_list'),
    path('schedules/create/', views.create_schedule, name='create_schedule'),
    path('schedules/<int:schedule_id>/delete/', views.delete_schedule, name='delete_schedule'),
    path('schedules/<int:schedule_id>/toggle/', views.toggle_schedule, name='toggle_schedule'),
    
    # Analytics
    path('analytics/', views.analytics_dashboard, name='analytics_dashboard'),
    
    # Authentication
    path('signup/', views.signup, name='signup'),
    path('profile/', views.profile, name='profile'),
] 