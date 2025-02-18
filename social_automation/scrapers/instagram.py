from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from .base import BaseScraper
import json
import os
import time
import logging

class InstagramScraper(BaseScraper):
    # XPath Constants
    FOLLOWERS_COUNT_XPATH = '//*[@id="mount_0_0_sr"]/div/div/div[2]/div/div/div[1]/div[2]/div/div[1]/section/main/div/header/section[3]/ul/li[2]/div/a/span/span'
    FOLLOWING_COUNT_XPATH = '//*[@id="mount_0_0_sr"]/div/div/div[2]/div/div/div[1]/div[2]/div/div[1]/section/main/div/header/section[3]/ul/li[3]/div/a/span/span'
    FOLLOWERS_SCROLL_XPATH = '/html/body/div[6]/div[2]/div/div/div[1]/div/div[2]/div/div/div/div/div[2]/div/div/div[3]'
    
    # Login XPaths
    CONTINUE_AS_XPATH = "//div[contains(@class, 'x9f619') and contains(@class, 'xjbqb8w')]//div[contains(@class, 'x1plvlek')]"
    USERNAME_INPUT_XPATH = '//*[@id="loginForm"]/div[1]/div[1]/div/label/input'
    PASSWORD_INPUT_XPATH = '//*[@id="loginForm"]/div[1]/div[2]/div/label/input'
    LOGIN_BUTTON_XPATH = "//button[@type='submit']"
    
    # Button XPath Pattern (can be formatted with index)
    FOLLOW_BUTTON_XPATH_PATTERN = '/html/body/div[6]/div[2]/div/div/div[1]/div/div[2]/div/div/div/div/div[2]/div/div/div[3]/div[1]/div/div[{index}]/div/div/div/div[3]/div/button/div/div'
    
    def __init__(self, username=None, password=None, headless=True):
        super().__init__(headless)
        self.username = username or os.getenv('INSTAGRAM_USERNAME')
        self.password = password or os.getenv('INSTAGRAM_PASSWORD')
        self.base_url = 'https://www.instagram.com'
        self.logged_in = False
        self.logger = logging.getLogger(__name__)

    def login(self):
        """Login to Instagram with handling for both direct login and 'Continue as' option"""
        if self.logged_in:
            return True

        try:
            self.driver.get(self.base_url)
            self.random_sleep(3, 5)

            # First, try to find the "Continue as" button
            try:
                continue_button = self.wait.until(
                    EC.presence_of_element_located((By.XPATH, self.CONTINUE_AS_XPATH))
                )
                self.logger.info("Found 'Continue as' button, attempting to use existing session")
                if self.safe_click(continue_button):
                    self.random_sleep(3, 5)
                    self.logged_in = True
                    return True
            except Exception as e:
                self.logger.info("No 'Continue as' button found, proceeding with manual login")

            # If "Continue as" wasn't available or failed, proceed with manual login
            try:
                # Enter username
                username_input = self.wait.until(
                    EC.presence_of_element_located((By.XPATH, self.USERNAME_INPUT_XPATH))
                )
                self.safe_send_keys(username_input, self.username)

                # Enter password
                password_input = self.wait.until(
                    EC.presence_of_element_located((By.XPATH, self.PASSWORD_INPUT_XPATH))
                )
                self.safe_send_keys(password_input, self.password)

                # Click login button
                login_button = self.wait.until(
                    EC.element_to_be_clickable((By.XPATH, self.LOGIN_BUTTON_XPATH))
                )
                if not self.safe_click(login_button):
                    raise Exception("Failed to click login button")

                self.random_sleep(5, 7)

                # Handle "Save Login Info" dialog if it appears
                try:
                    not_now_button = self.wait.until(
                        EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Not Now')]"))
                    )
                    self.safe_click(not_now_button)
                except TimeoutException:
                    self.logger.info("No 'Save Login Info' dialog found")

                # Handle "Turn on Notifications" dialog if it appears
                try:
                    not_now_button = self.wait.until(
                        EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Not Now')]"))
                    )
                    self.safe_click(not_now_button)
                except TimeoutException:
                    self.logger.info("No 'Turn on Notifications' dialog found")

                self.logged_in = True
                return True

            except Exception as e:
                self.logger.error(f"Manual login failed: {str(e)}")
                return False

        except Exception as e:
            self.logger.error(f"Login process failed: {str(e)}")
            return False

    def get_profile_info(self, username):
        """Get profile information for a user"""
        if not self.logged_in and not self.login():
            return None

        try:
            self.driver.get(f"{self.base_url}/{username}/")
            self.random_sleep(3, 5)

            # Get follower and following counts
            stats = self.driver.find_elements(By.CSS_SELECTOR, "header section ul li")
            followers = stats[1].text.split()[0]
            following = stats[2].text.split()[0]

            # Get bio and other profile info
            bio = self.driver.find_element(By.CSS_SELECTOR, "header section div:nth-child(3)").text

            return {
                'username': username,
                'followers': followers,
                'following': following,
                'bio': bio,
                'is_private': 'This Account is Private' in self.driver.page_source
            }

        except Exception as e:
            print(f"Failed to get profile info: {str(e)}")
            return None

    def get_followers_count(self):
        """Get the number of followers"""
        try:
            element = self.wait.until(
                EC.presence_of_element_located((By.XPATH, self.FOLLOWERS_COUNT_XPATH))
            )
            return int(element.text.replace(',', ''))
        except Exception as e:
            self.logger.error(f"Failed to get followers count: {str(e)}")
            return 0

    def get_following_count(self):
        """Get the number of following"""
        try:
            element = self.wait.until(
                EC.presence_of_element_located((By.XPATH, self.FOLLOWING_COUNT_XPATH))
            )
            return int(element.text.replace(',', ''))
        except Exception as e:
            self.logger.error(f"Failed to get following count: {str(e)}")
            return 0

    def scroll_user_list(self):
        """Scroll through the user list until no more content loads"""
        try:
            scroll_div = self.wait.until(
                EC.presence_of_element_located((By.XPATH, self.FOLLOWERS_SCROLL_XPATH))
            )
            
            last_height = self.driver.execute_script("return arguments[0].scrollHeight", scroll_div)
            while True:
                # Scroll to bottom
                self.driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", scroll_div)
                self.random_sleep(2, 3)  # Wait for content to load
                
                # Calculate new scroll height and compare with last scroll height
                new_height = self.driver.execute_script("return arguments[0].scrollHeight", scroll_div)
                if new_height == last_height:
                    break
                last_height = new_height
                
        except Exception as e:
            self.logger.error(f"Error scrolling user list: {str(e)}")

    def get_follow_buttons(self, action='follow'):
        """Get all follow/following buttons based on action type"""
        buttons = []
        index = 1
        
        while True:
            try:
                button_xpath = self.FOLLOW_BUTTON_XPATH_PATTERN.format(index=index)
                button = self.driver.find_element(By.XPATH, button_xpath)
                
                # Check if button matches our action type
                if action == 'follow' and button.text == 'Follow':
                    buttons.append(button)
                elif action == 'unfollow' and button.text == 'Following':
                    buttons.append(button)
                
                index += 1
                
                # Break if we've found enough buttons or reached the end
                if len(buttons) >= 50 or index > 100:  # Limit to prevent infinite loop
                    break
                    
            except Exception:
                break  # No more buttons found
                
        return buttons

    def get_followers(self, username, max_count=100):
        """Get a list of user's followers"""
        if not self.logged_in and not self.login():
            return []

        followers = []
        try:
            # Navigate to user's profile
            self.driver.get(f"{self.base_url}/{username}/")
            self.random_sleep(3, 5)
            
            # Click followers count to open modal
            followers_element = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, self.FOLLOWERS_COUNT_XPATH))
            )
            self.safe_click(followers_element)
            self.random_sleep(2, 3)
            
            # Scroll to load all users
            self.scroll_user_list()
            
            # Get all follow buttons
            buttons = self.get_follow_buttons(action='follow')
            
            # Extract usernames from parent elements
            for button in buttons[:max_count]:
                try:
                    # Get username from parent div
                    username_element = button.find_element(By.XPATH, "./ancestor::div[contains(@class, 'x1dm5mii')]//span[contains(@class, 'xt0psk2')]")
                    followers.append(username_element.text)
                except Exception as e:
                    self.logger.error(f"Error extracting username: {str(e)}")
                    continue
                    
            return followers[:max_count]
            
        except Exception as e:
            self.logger.error(f"Error getting followers: {str(e)}")
            return []

    def get_following(self, username, max_count=100):
        """Get a list of users that the user is following"""
        if not self.logged_in and not self.login():
            return []

        following = []
        try:
            # Navigate to user's profile
            self.driver.get(f"{self.base_url}/{username}/")
            self.random_sleep(3, 5)
            
            # Click following count to open modal
            following_element = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, self.FOLLOWING_COUNT_XPATH))
            )
            self.safe_click(following_element)
            self.random_sleep(2, 3)
            
            # Scroll to load all users
            self.scroll_user_list()
            
            # Get all following buttons
            buttons = self.get_follow_buttons(action='unfollow')
            
            # Extract usernames from parent elements
            for button in buttons[:max_count]:
                try:
                    # Get username from parent div
                    username_element = button.find_element(By.XPATH, "./ancestor::div[contains(@class, 'x1dm5mii')]//span[contains(@class, 'xt0psk2')]")
                    following.append(username_element.text)
                except Exception as e:
                    self.logger.error(f"Error extracting username: {str(e)}")
                    continue
                    
            return following[:max_count]
            
        except Exception as e:
            self.logger.error(f"Error getting following: {str(e)}")
            return []

    def follow_user(self, username):
        """Follow a user"""
        if not self.logged_in and not self.login():
            return False

        try:
            # Navigate to user's profile
            self.driver.get(f"{self.base_url}/{username}/")
            self.random_sleep(3, 5)

            # Find and click follow button
            follow_button = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//button[div/div[text()='Follow']]"))
            )
            return self.safe_click(follow_button)

        except Exception as e:
            self.logger.error(f"Failed to follow user {username}: {str(e)}")
            return False

    def unfollow_user(self, username):
        """Unfollow a user"""
        if not self.logged_in and not self.login():
            return False

        try:
            # Navigate to user's profile
            self.driver.get(f"{self.base_url}/{username}/")
            self.random_sleep(3, 5)

            # Find and click following button
            following_button = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//button[div/div[text()='Following']]"))
            )
            if not self.safe_click(following_button):
                return False

            self.random_sleep(1, 2)

            # Click unfollow in the popup
            unfollow_button = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//button[text()='Unfollow']"))
            )
            return self.safe_click(unfollow_button)

        except Exception as e:
            self.logger.error(f"Failed to unfollow user {username}: {str(e)}")
            return False 