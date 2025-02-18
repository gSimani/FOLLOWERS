import os
import subprocess
import sys

def run_command(command):
    try:
        subprocess.run(command, shell=True, check=True)
        print(f"Successfully ran: {command}")
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {command}")
        print(f"Error: {str(e)}")
        sys.exit(1)

def setup_project():
    # Create project directory
    project_path = r"C:\Users\mdd22\OneDrive\Desktop\GUY and MIKE\FOLLOWERS"
    os.makedirs(project_path, exist_ok=True)
    os.chdir(project_path)
    
    # Install required packages
    run_command("pip install --user django django-allauth django-crispy-forms crispy-tailwind")
    
    # Create Django project
    run_command("python -m django startproject followers .")
    
    # Create social_automation app
    run_command("python -m django startapp social_automation")
    
    # Create necessary directories
    os.makedirs("templates/social_automation", exist_ok=True)
    os.makedirs("static", exist_ok=True)
    
    # Create base template
    with open("templates/base.html", "w") as f:
        f.write("""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}Social Media Automation{% endblock %}</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body>
    <div class="container mx-auto px-4 py-8">
        {% block content %}{% endblock %}
    </div>
</body>
</html>""")

    # Create test template
    with open("templates/social_automation/test.html", "w") as f:
        f.write("""{% extends 'base.html' %}

{% block content %}
<div class="max-w-7xl mx-auto py-12">
    <h1 class="text-4xl font-bold text-center mb-8">Welcome to Social Media Automation</h1>
    <p class="text-center text-xl">Your automation platform is ready!</p>
</div>
{% endblock %}""")

    # Update settings.py
    with open("followers/settings.py", "r") as f:
        settings = f.read()
    
    settings = settings.replace(
        "INSTALLED_APPS = [",
        """INSTALLED_APPS = [
    'social_automation',"""
    )
    
    settings = settings.replace(
        "'DIRS': []",
        "'DIRS': [BASE_DIR / 'templates']"
    )
    
    with open("followers/settings.py", "w") as f:
        f.write(settings)

    # Update urls.py
    with open("followers/urls.py", "w") as f:
        f.write("""from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('social_automation.urls')),
]""")

    # Create app urls.py
    with open("social_automation/urls.py", "w") as f:
        f.write("""from django.urls import path
from . import views

app_name = 'social_automation'

urlpatterns = [
    path('', views.home, name='home'),
]""")

    # Create views
    with open("social_automation/views.py", "w") as f:
        f.write("""from django.shortcuts import render

def home(request):
    return render(request, 'social_automation/test.html')""")

    # Run migrations
    run_command("python manage.py makemigrations")
    run_command("python manage.py migrate")
    
    # Start the development server
    print("\nSetup complete! Starting the development server...")
    print("You can access the site at: http://127.0.0.1:8000")
    run_command("python manage.py runserver")

if __name__ == "__main__":
    setup_project() 