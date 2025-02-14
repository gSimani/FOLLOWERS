from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from .base import BaseScraper
import os

class FacebookScraper(BaseScraper):
    def __init__(self, email=None, password=None, headless=True):
        super().__init__(headless)
        self.email = email or os.getenv('FACEBOOK_EMAIL')
        self.password = password or os.getenv('FACEBOOK_PASSWORD')
        self.base_url = 'https://www.facebook.com'
        self.logged_in = False

    def login(self):
        """Login to Facebook"""
        if self.logged_in:
            return True

        try:
            self.driver.get(self.base_url)
            self.random_sleep(3, 5)

            # Handle cookie consent if present
            try:
                cookie_button = self.wait.until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Allow') or contains(text(), 'Accept')]"))
                )
                self.safe_click(cookie_button)
            except TimeoutException:
                pass

            # Enter email
            email_input = self.wait.until(
                EC.presence_of_element_located((By.ID, "email"))
            )
            self.safe_send_keys(email_input, self.email)

            # Enter password
            password_input = self.wait.until(
                EC.presence_of_element_located((By.ID, "pass"))
            )
            self.safe_send_keys(password_input, self.password)

            # Click login button
            login_button = self.wait.until(
                EC.element_to_be_clickable((By.NAME, "login"))
            )
            self.safe_click(login_button)
            self.random_sleep(5, 7)

            self.logged_in = True
            return True

        except Exception as e:
            print(f"Login failed: {str(e)}")
            return False

    def get_profile_info(self, username):
        """Get profile information for a user"""
        if not self.logged_in and not self.login():
            return None

        try:
            self.driver.get(f"{self.base_url}/{username}")
            self.random_sleep(3, 5)

            # Get follower count (if available)
            try:
                followers = self.driver.find_element(
                    By.XPATH,
                    "//a[contains(@href, 'followers')]/span"
                ).text
            except:
                followers = "N/A"

            # Get following count (if available)
            try:
                following = self.driver.find_element(
                    By.XPATH,
                    "//a[contains(@href, 'following')]/span"
                ).text
            except:
                following = "N/A"

            # Get bio
            try:
                bio = self.driver.find_element(
                    By.XPATH,
                    "//div[contains(@class, 'profileBio')]"
                ).text
            except:
                bio = ""

            return {
                'username': username,
                'followers': followers,
                'following': following,
                'bio': bio,
                'is_private': "This content isn't available" in self.driver.page_source
            }

        except Exception as e:
            print(f"Failed to get profile info: {str(e)}")
            return None

    def follow_user(self, username):
        """Follow a user"""
        if not self.logged_in and not self.login():
            return False

        try:
            self.driver.get(f"{self.base_url}/{username}")
            self.random_sleep(3, 5)

            follow_button = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//span[text()='Follow']"))
            )
            return self.safe_click(follow_button)

        except Exception as e:
            print(f"Failed to follow user: {str(e)}")
            return False

    def unfollow_user(self, username):
        """Unfollow a user"""
        if not self.logged_in and not self.login():
            return False

        try:
            self.driver.get(f"{self.base_url}/{username}")
            self.random_sleep(3, 5)

            # Click Following button
            following_button = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//span[text()='Following']"))
            )
            self.safe_click(following_button)
            self.random_sleep(1, 2)

            # Click Unfollow in the popup
            unfollow_button = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//span[text()='Unfollow']"))
            )
            return self.safe_click(unfollow_button)

        except Exception as e:
            print(f"Failed to unfollow user: {str(e)}")
            return False

    def get_followers(self, username, max_count=100):
        """Get a list of user's followers"""
        if not self.logged_in and not self.login():
            return []

        followers = []
        try:
            self.driver.get(f"{self.base_url}/{username}/followers")
            self.random_sleep(3, 5)

            while len(followers) < max_count:
                # Find follower elements
                follower_items = self.driver.find_elements(
                    By.XPATH,
                    "//div[@role='main']//a[contains(@href, '/user/')]"
                )

                for item in follower_items:
                    if len(followers) >= max_count:
                        break

                    try:
                        username = item.get_attribute("href").split("/")[-1]
                        if username not in followers:
                            followers.append(username)
                    except:
                        continue

                # Scroll to load more
                self.driver.execute_script(
                    "window.scrollTo(0, document.body.scrollHeight);"
                )
                self.random_sleep(2, 3)

                # Check if we've reached the end
                if len(follower_items) == len(followers):
                    break

        except Exception as e:
            print(f"Failed to get followers: {str(e)}")

        return followers

    def get_following(self, username, max_count=100):
        """Get a list of users that the user is following"""
        if not self.logged_in and not self.login():
            return []

        following = []
        try:
            self.driver.get(f"{self.base_url}/{username}/following")
            self.random_sleep(3, 5)

            while len(following) < max_count:
                # Find following elements
                following_items = self.driver.find_elements(
                    By.XPATH,
                    "//div[@role='main']//a[contains(@href, '/user/')]"
                )

                for item in following_items:
                    if len(following) >= max_count:
                        break

                    try:
                        username = item.get_attribute("href").split("/")[-1]
                        if username not in following:
                            following.append(username)
                    except:
                        continue

                # Scroll to load more
                self.driver.execute_script(
                    "window.scrollTo(0, document.body.scrollHeight);"
                )
                self.random_sleep(2, 3)

                # Check if we've reached the end
                if len(following_items) == len(following):
                    break

        except Exception as e:
            print(f"Failed to get following: {str(e)}")

        return following 