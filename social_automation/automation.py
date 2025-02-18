from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import undetected_chromedriver as uc
import time
import random
import logging

class AutomationController:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.setup_driver()
        
    def setup_driver(self):
        options = uc.ChromeOptions()
        options.add_argument('--incognito')
        options.add_argument('--start-maximized')
        
        # Anti-detection measures
        options.add_argument('--disable-blink-features=AutomationControlled')
        
        self.driver = uc.Chrome(options=options)
        
    def human_delay(self):
        """Randomized delay to mimic human behavior"""
        base_delay = random.uniform(1.5, 3.0)
        micro_delay = random.uniform(0, 0.5)
        time.sleep(base_delay + micro_delay)
        
    async def update_progress(self, websocket, progress, action):
        """Send progress updates to frontend"""
        await websocket.send_json({
            'progress': progress,
            'action': action,
            'timestamp': time.time()
        })
        
    async def execute_automation(self, platform, action, target_url, quantity):
        """Main automation execution loop"""
        try:
            processed = 0
            total = int(quantity)
            
            # Navigate to target profile
            self.driver.get(target_url)
            self.human_delay()
            
            # Open followers/following list
            followers_button = self.driver.find_element_by_xpath("//a[contains(@href, '/followers')]")
            followers_button.click()
            self.human_delay()
            
            while processed < total:
                # Find action buttons (follow/unfollow)
                buttons = self.driver.find_elements_by_xpath(
                    f"//button[text()='{action.title()}']"
                )
                
                for button in buttons:
                    if processed >= total:
                        break
                        
                    try:
                        button.click()
                        processed += 1
                        
                        # Update progress
                        progress = (processed / total) * 100
                        await self.update_progress(
                            websocket,
                            progress,
                            f"Processing user {processed}/{total}"
                        )
                        
                        self.human_delay()
                        
                    except Exception as e:
                        self.logger.error(f"Action failed: {str(e)}")
                        continue
                
                # Scroll to load more
                self.driver.execute_script(
                    "arguments[0].scrollIntoView();", 
                    buttons[-1]
                )
                self.human_delay()
                
            return True
            
        except Exception as e:
            self.logger.error(f"Automation failed: {str(e)}")
            return False
            
        finally:
            self.driver.quit() 