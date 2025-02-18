from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from .base import BaseScraper
import undetected_chromedriver as uc
import logging
import time
import random
import os

class InstagramScraper(BaseScraper):
    def __init__(self, headless=False):
        self.logger = logging.getLogger(__name__)
        self.setup_driver(headless)
        
    def setup_driver(self, headless=False):
        """Initialize undetected-chromedriver with anti-detection measures"""
        options = uc.ChromeOptions()
        if headless:
            options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--disable-notifications')
        
        # Use custom user agent
        options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        self.driver = uc.Chrome(options=options)
        self.driver.maximize_window()
        
    async def login(self, username, password):
        """Login to Instagram with enhanced error handling"""
        try:
            self.driver.get("https://www.instagram.com/accounts/login/")
            self.human_delay()
            
            # Wait for and enter username
            username_input = WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.NAME, "username"))
            )
            await self.safe_send_keys(username_input, username)
            
            # Enter password
            password_input = self.driver.find_element(By.NAME, "password")
            await self.safe_send_keys(password_input, password)
            
            # Click login button
            login_button = self.driver.find_element(
                By.XPATH, '//*[@id="loginForm"]/div/div[3]'
            )
            await self.safe_click(login_button)
            
            # Check for login errors
            try:
                error_message = WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.ID, "slfErrorAlert"))
                )
                self.logger.error(f"Login failed: {error_message.text}")
                return False
            except:
                pass
                
            # Handle "Save Your Login Info?" popup
            await self.handle_save_info_popup()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Login failed: {str(e)}")
            return False
            
    async def handle_save_info_popup(self):
        """Handle the save info popup with multiple path attempts"""
        paths = [
            '//*[@id="mount_0_0_hO"]/div/div/div[2]/div/div/div[1]/div[1]/div[1]/section/main/div/div/div/div/div',
            '#mount_0_0_hO > div > div > div.x9f619.x1n2onr6.x1ja2u2z > div > div > div',
            '/html/body/div[2]/div/div/div[2]/div/div/div[1]/div[1]/div[1]/section/main/div/div/div/div/div'
        ]
        
        for path in paths:
            try:
                not_now_button = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, path))
                )
                await self.safe_click(not_now_button)
                return True
            except Exception:
                continue
                
        return False
            
    async def navigate_to_profile(self, profile_url):
        """Navigate to target profile with enhanced error handling"""
        try:
            self.driver.get(profile_url)
            self.human_delay()
            
            # Verify profile loaded
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((
                    By.XPATH, 
                    '//header//section'
                ))
            )
            
            return True
            
        except Exception as e:
            self.logger.error(f"Profile navigation failed: {str(e)}")
            return False
            
    async def open_followers_list(self):
        """Open followers modal with multiple xpath attempts"""
        followers_xpaths = [
            '//*[@id="mount_0_0_f+"]/div/div/div[2]/div/div/div[1]/div[2]/div/div[1]/section/main/div/header/section[3]/ul/li[2]/div/a',
            '//*[@id="mount_0_0_1V"]/div/div/div[2]/div/div/div[1]/div[2]/div/div[1]/section/main/div/header/section[3]/ul/li[2]/div/a',
            '/html/body/div[2]/div/div/div[2]/div/div/div[1]/div[2]/div/div[1]/section/main/div/header/section[3]/ul/li[2]/div/a',
            '//a[contains(@href,"/followers/")]',
            '//a[contains(text(), " followers")]'
        ]
        
        for xpath in followers_xpaths:
            try:
                followers_link = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, xpath))
                )
                await self.safe_click(followers_link)
                
                # Verify modal opened
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((
                        By.CSS_SELECTOR, 
                        'div[role="dialog"]'
                    ))
                )
                return True
                
            except Exception:
                continue
                
        return False
            
    async def scroll_followers_list(self):
        """Scroll followers list with rate limiting"""
        try:
            scroll_box = self.driver.find_element(
                By.CSS_SELECTOR, 
                'div[role="dialog"] ul'
            )
            last_height, new_height = 0, 1
            
            while last_height != new_height:
                last_height = new_height
                self.human_delay()
                
                new_height = self.driver.execute_script(
                    "arguments[0].scrollTo(0, arguments[0].scrollHeight); "
                    "return arguments[0].scrollHeight;",
                    scroll_box
                )
                
            return True
            
        except Exception as e:
            self.logger.error(f"Scrolling failed: {str(e)}")
            return False
            
    async def process_followers(self, action, quantity, websocket):
        """Process followers with batched following and rate limiting"""
        processed = 0
        batch_size = 25  # Instagram's rate limit friendly batch size
        
        try:
            while processed < quantity:
                # Find follow buttons
                buttons = self.driver.find_elements(
                    By.XPATH,
                    '//button[text()="Follow"]'
                )
                
                # Process in batches
                current_batch = buttons[processed:min(processed + batch_size, quantity)]
                
                for button in current_batch:
                    if await self.safe_click(button):
                        processed += 1
                        
                        # Update progress
                        progress = (processed / quantity) * 100
                        await websocket.send_json({
                            'type': 'progress',
                            'progress': progress,
                            'message': f"Followed {processed}/{quantity} users"
                        })
                        
                        self.human_delay()
                
                # Batch complete, add longer delay
                if processed % batch_size == 0:
                    time.sleep(random.uniform(8, 12))  # Random delay between batches
                    
                # Scroll if needed
                if processed < quantity:
                    await self.scroll_followers_list()
                    
            return True
            
        except Exception as e:
            self.logger.error(f"Processing followers failed: {str(e)}")
            return False
            
    def human_delay(self):
        """Randomized delay to mimic human behavior"""
        time.sleep(random.uniform(1.5, 3.0) + random.uniform(0, 0.5))
        
    async def safe_click(self, element):
        """Safe click with retry logic"""
        try:
            self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
            WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable(element)
            )
            element.click()
            return True
        except Exception as e:
            self.logger.error(f"Click failed: {str(e)}")
            return False
            
    async def safe_send_keys(self, element, text):
        """Safe text input with human-like typing"""
        try:
            for char in text:
                element.send_keys(char)
                time.sleep(random.uniform(0.1, 0.3))
            return True
        except Exception as e:
            self.logger.error(f"Send keys failed: {str(e)}")
            return False 