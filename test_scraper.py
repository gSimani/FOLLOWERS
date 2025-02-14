from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class InstagramTest:
    def __init__(self):
        self.driver = None
        self.wait = None
        self.username = os.getenv('INSTAGRAM_USERNAME')
        self.password = os.getenv('INSTAGRAM_PASSWORD')

    def setup_driver(self):
        """Initialize the Chrome driver"""
        options = webdriver.ChromeOptions()
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option('excludeSwitches', ['enable-automation'])
        options.add_experimental_option('useAutomationExtension', False)
        
        self.driver = webdriver.Chrome(options=options)
        self.wait = WebDriverWait(self.driver, 10)
        
        # Execute stealth script
        self.driver.execute_script(
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
        )

    def login(self):
        """Test Instagram login"""
        try:
            print("Attempting to log in to Instagram...")
            self.driver.get('https://www.instagram.com/')
            time.sleep(3)  # Wait for page to load

            # Check for "Continue as" button
            try:
                continue_button = self.wait.until(
                    EC.presence_of_element_located((
                        By.XPATH,
                        "//div[contains(@class, 'x9f619') and contains(@class, 'xjbqb8w')]//div[contains(@class, 'x1plvlek')]"
                    ))
                )
                print("Found 'Continue as' button, clicking...")
                continue_button.click()
                return True
            except Exception as e:
                print("No 'Continue as' button found, proceeding with manual login...")

            # Enter username
            username_input = self.wait.until(
                EC.presence_of_element_located((
                    By.XPATH,
                    '//*[@id="loginForm"]/div[1]/div[1]/div/label/input'
                ))
            )
            username_input.send_keys(self.username)
            print("Username entered...")

            # Enter password
            password_input = self.wait.until(
                EC.presence_of_element_located((
                    By.XPATH,
                    '//*[@id="loginForm"]/div[1]/div[2]/div/label/input'
                ))
            )
            password_input.send_keys(self.password)
            print("Password entered...")

            # Click login button
            login_button = self.wait.until(
                EC.element_to_be_clickable((
                    By.XPATH,
                    "//button[@type='submit']"
                ))
            )
            login_button.click()
            print("Login button clicked...")

            # Wait for login to complete
            time.sleep(5)

            # Handle "Save Login Info" dialog if it appears
            try:
                not_now_button = self.wait.until(
                    EC.element_to_be_clickable((
                        By.XPATH,
                        "//button[contains(text(), 'Not Now')]"
                    ))
                )
                not_now_button.click()
                print("Handled 'Save Login Info' dialog...")
            except Exception:
                print("No 'Save Login Info' dialog found...")

            return True

        except Exception as e:
            print(f"Login failed: {str(e)}")
            return False

    def test_get_followers(self, target_account):
        """Test getting followers from a target account"""
        try:
            print(f"Navigating to {target_account}'s profile...")
            self.driver.get(f'https://www.instagram.com/{target_account}/')
            time.sleep(3)

            # Click followers count
            followers_element = self.wait.until(
                EC.element_to_be_clickable((
                    By.XPATH,
                    '//*[@id="mount_0_0_sr"]/div/div/div[2]/div/div/div[1]/div[2]/div/div[1]/section/main/div/header/section[3]/ul/li[2]/div/a/span/span'
                ))
            )
            followers_element.click()
            print("Clicked followers count...")
            time.sleep(3)

            # Scroll through followers
            scroll_div = self.wait.until(
                EC.presence_of_element_located((
                    By.XPATH,
                    '/html/body/div[6]/div[2]/div/div/div[1]/div/div[2]/div/div/div/div/div[2]/div/div/div[3]'
                ))
            )
            
            # Scroll a few times
            for _ in range(3):
                self.driver.execute_script(
                    "arguments[0].scrollTop = arguments[0].scrollHeight",
                    scroll_div
                )
                time.sleep(2)
                print("Scrolled followers list...")

            print("Successfully tested followers retrieval")
            return True

        except Exception as e:
            print(f"Error getting followers: {str(e)}")
            return False

    def cleanup(self):
        """Clean up resources"""
        if self.driver:
            self.driver.quit()

def main():
    tester = InstagramTest()
    try:
        print("Setting up Chrome driver...")
        tester.setup_driver()
        
        if tester.login():
            print("Login successful!")
            
            # Test getting followers from a public account
            target_account = 'akim.realestate'  # Using the example account
            if tester.test_get_followers(target_account):
                print("Followers test successful!")
            else:
                print("Followers test failed!")
        else:
            print("Login failed!")
            
    except Exception as e:
        print(f"Test failed: {str(e)}")
    finally:
        print("Cleaning up...")
        tester.cleanup()

if __name__ == "__main__":
    main() 