from locust import HttpUser, task, between
import random

class AutomationUser(HttpUser):
    wait_time = between(1, 3)
    
    def on_start(self):
        """Setup before starting tests"""
        self.platforms = ['instagram', 'facebook', 'linkedin']
        self.actions = ['follow', 'unfollow']
        self.quantities = [50, 100, 150, 200]
        
    @task(3)
    def start_automation(self):
        """Test starting automation tasks"""
        platform = random.choice(self.platforms)
        action = random.choice(self.actions)
        quantity = random.choice(self.quantities)
        
        self.client.post("/api/automation/start", json={
            "platform": platform,
            "action": action,
            "target_url": f"https://{platform}.com/test_user_{random.randint(1000, 9999)}",
            "quantity": quantity
        })
    
    @task(2)
    def check_progress(self):
        """Test progress endpoint"""
        self.client.get(f"/api/automation/progress/{random.randint(1, 100)}")
    
    @task(1)
    def view_logs(self):
        """Test logs endpoint"""
        self.client.get("/api/automation/logs") 