from django.contrib import admin
from django.urls import path
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', TemplateView.as_view(template_name='platform_select.html'), name='home'),
    path('api/automation/start', views.start_automation, name='start_automation'),
    path('api/automation/progress/<str:task_id>/', views.get_progress, name='get_progress'),
    path('api/automation/logs/', views.get_logs, name='get_logs'),
]

# Serve static files in development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) 