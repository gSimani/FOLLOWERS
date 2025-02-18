import os
import subprocess
import sys

def run_command(command, error_message="Command failed"):
    try:
        subprocess.run(command, shell=True, check=True)
        return True
    except subprocess.CalledProcessError:
        print(f"Error: {error_message}")
        return False

def setup_vercel():
    print("Setting up Vercel...")
    commands = [
        "npm i -g vercel",
        f"vercel login --token {os.getenv('VERCEL_TOKEN', 'iePAKLzR7pnniYiHNUPwXIMt')}",
        "vercel link --yes"
    ]
    
    for cmd in commands:
        if not run_command(cmd):
            return False
    return True

def deploy_to_vercel():
    print("Deploying to Vercel...")
    if not run_command("vercel --prod"):
        return False
    return True

def push_to_github():
    print("Pushing to GitHub...")
    commands = [
        "git add .",
        'git commit -m "Update deployment"',
        "git push origin main"
    ]
    
    for cmd in commands:
        if not run_command(cmd):
            return False
    return True

def main():
    # Ensure we're in the right directory
    if not os.path.exists("manage.py"):
        print("Error: Please run this script from the project root directory")
        sys.exit(1)
        
    # Run database migrations
    if not run_command("python manage.py migrate"):
        sys.exit(1)
        
    # Run tests
    if not run_command("pytest"):
        print("Warning: Tests failed. Continue anyway? (y/n)")
        if input().lower() != 'y':
            sys.exit(1)
            
    # Setup and deploy to Vercel
    if not setup_vercel():
        sys.exit(1)
        
    if not deploy_to_vercel():
        sys.exit(1)
        
    # Push to GitHub
    if not push_to_github():
        sys.exit(1)
        
    print("\nDeployment complete!")
    print("Check your deployment at: https://followers-yidbiz.vercel.app")

if __name__ == "__main__":
    main() 