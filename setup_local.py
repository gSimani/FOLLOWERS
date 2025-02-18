import os
import sys
import subprocess
import json

def check_python_version():
    print("Checking Python version...")
    if sys.version_info < (3, 11):
        print("Error: Python 3.11 or higher is required")
        sys.exit(1)
    print("✓ Python version OK")

def check_dependencies():
    print("Checking dependencies...")
    try:
        subprocess.run(["pip", "install", "-r", "requirements.txt"], check=True)
        print("✓ Dependencies installed")
    except subprocess.CalledProcessError:
        print("Error: Failed to install dependencies")
        sys.exit(1)

def setup_vercel_config():
    print("Setting up Vercel configuration...")
    config = {
        "projectId": "prj_FHlmV71F2v4iZt1N19mXe7lXgQBf",
        "orgId": "team_OIAQ7q0bQTblRPZrnKhU4BGF",
        "settings": {
            "framework": "other"
        }
    }
    
    with open(".vercel/project.json", "w") as f:
        json.dump(config, f, indent=2)
    print("✓ Vercel config created")

def setup_env_file():
    print("Setting up environment variables...")
    env_vars = {
        "VERCEL_TOKEN": "iePAKLzR7pnniYiHNUPwXIMt",
        "VERCEL_ORG_ID": "team_OIAQ7q0bQTblRPZrnKhU4BGF",
        "VERCEL_PROJECT_ID": "prj_FHlmV71F2v4iZt1N19mXe7lXgQBf",
        "DJANGO_SETTINGS_MODULE": "social_automation.settings",
        "DATABASE_URL": "postgresql://localhost/social_automation",
        "DEBUG": "True"
    }
    
    with open(".env", "w") as f:
        for key, value in env_vars.items():
            f.write(f"{key}={value}\n")
    print("✓ Environment variables set")

def main():
    print("Starting local setup...")
    check_python_version()
    check_dependencies()
    
    # Create necessary directories
    os.makedirs(".vercel", exist_ok=True)
    
    setup_vercel_config()
    setup_env_file()
    
    print("\nSetup complete! You can now run:")
    print("1. python manage.py migrate")
    print("2. python manage.py runserver")

if __name__ == "__main__":
    main() 