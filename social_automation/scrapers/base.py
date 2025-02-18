import time
import random
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from fake_useragent import UserAgent
import undetected_chromedriver as uc
from django.conf import settings

class BaseScraper:
    def __init__(self, headless=True):
        self.headless = headless
        self.driver = None
        self.wait = None
        self.setup_driver()

    def setup_driver(self):
        options = webdriver.ChromeOptions()
        ua = UserAgent()
        options.add_argument(f'user-agent={ua.random}')
        
        if self.headless:
            options.add_argument('--headless')
        
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920,1080')
        options.add_argument('--disable-notifications')
        options.add_experimental_option('excludeSwitches', ['enable-automation'])
        options.add_experimental_option('useAutomationExtension', False)

        # Use undetected-chromedriver for better anti-bot evasion
        self.driver = uc.Chrome(options=options)
        self.wait = WebDriverWait(self.driver, 10)

    def random_sleep(self, min_seconds=2, max_seconds=5):
        time.sleep(random.uniform(min_seconds, max_seconds))

    def safe_click(self, element):
        """Click with random delay and error handling"""
        try:
            self.random_sleep(1, 3)
            element.click()
            return True
        except Exception as e:
            print(f"Click failed: {str(e)}")
            return False

    def safe_send_keys(self, element, text, clear=True):
        """Type with random delays between keystrokes"""
        try:
            if clear:
                element.clear()
            for char in text:
                element.send_keys(char)
                time.sleep(random.uniform(0.1, 0.3))
            return True
        except Exception as e:
            print(f"Send keys failed: {str(e)}")
            return False

    def scroll_to_element(self, element):
        """Scroll element into view with JS"""
        self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
        self.random_sleep(1, 2)

    def infinite_scroll(self, scroll_pause=2):
        """Scroll to bottom of page until no more content loads"""
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        
        while True:
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            self.random_sleep(scroll_pause, scroll_pause + 2)
            
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

    def close(self):
        """Close browser and cleanup"""
        if self.driver:
            self.driver.quit()
            self.driver = None
            self.wait = None 