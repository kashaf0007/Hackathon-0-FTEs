"""
LinkedIn watcher - Monitors LinkedIn for connection requests and messages.
Uses Selenium for web automation.
"""

import os
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from AI_Employee_Vault.Watchers.watcher_base import WatcherBase


class LinkedInWatcher(WatcherBase):
    """
    LinkedIn watcher using Selenium for web automation.

    Monitors LinkedIn for:
    - Connection requests
    - New messages
    - Post mentions/comments (optional)
    """

    def __init__(self, poll_interval: int = 600):
        """
        Initialize LinkedIn watcher.

        Args:
            poll_interval: Polling interval in seconds (default: 600 = 10 minutes)
        """
        super().__init__(source='linkedin', poll_interval=poll_interval)

        self.email = os.getenv('LINKEDIN_EMAIL')
        self.password = os.getenv('LINKEDIN_PASSWORD')
        self.driver = None
        self.is_logged_in = False

        if not self.email or not self.password:
            raise ValueError(
                "LinkedIn credentials not found in environment variables.\n"
                "Please set LINKEDIN_EMAIL and LINKEDIN_PASSWORD in .env file."
            )

    def _init_driver(self) -> None:
        """Initialize Selenium WebDriver."""
        if self.driver:
            return

        options = webdriver.ChromeOptions()
        options.add_argument('--headless')  # Run in background
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)

        try:
            self.driver = webdriver.Chrome(options=options)
            self.driver.implicitly_wait(10)
        except Exception as e:
            self.logger.error(
                component="watcher",
                action="driver_init_failed",
                actor="linkedin_watcher",
                target="selenium",
                details={"error": str(e)}
            )
            raise

    def _login(self) -> bool:
        """
        Login to LinkedIn.

        Returns:
            True if login successful, False otherwise
        """
        if self.is_logged_in:
            return True

        try:
            self._init_driver()

            # Navigate to LinkedIn login
            self.driver.get('https://www.linkedin.com/login')
            time.sleep(2)

            # Enter credentials
            email_field = self.driver.find_element(By.ID, 'username')
            password_field = self.driver.find_element(By.ID, 'password')

            email_field.send_keys(self.email)
            password_field.send_keys(self.password)

            # Click login button
            login_button = self.driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
            login_button.click()

            # Wait for redirect to feed
            time.sleep(5)

            # Check if login successful
            if 'feed' in self.driver.current_url or 'mynetwork' in self.driver.current_url:
                self.is_logged_in = True
                self.logger.info(
                    component="watcher",
                    action="login_success",
                    actor="linkedin_watcher",
                    target="linkedin",
                    details={"status": "authenticated"}
                )
                return True
            else:
                self.logger.error(
                    component="watcher",
                    action="login_failed",
                    actor="linkedin_watcher",
                    target="linkedin",
                    details={"url": self.driver.current_url}
                )
                return False

        except Exception as e:
            self.logger.error(
                component="watcher",
                action="login_error",
                actor="linkedin_watcher",
                target="linkedin",
                details={"error": str(e)}
            )
            return False

    def _fetch_connection_requests(self) -> List[Dict[str, Any]]:
        """
        Fetch pending connection requests.

        Returns:
            List of connection request events
        """
        events = []

        try:
            # Navigate to My Network page
            self.driver.get('https://www.linkedin.com/mynetwork/invitation-manager/')
            time.sleep(3)

            # Find connection request cards
            try:
                request_cards = self.driver.find_elements(
                    By.CSS_SELECTOR,
                    'li.invitation-card'
                )

                for card in request_cards[:5]:  # Limit to 5 most recent
                    try:
                        # Extract name
                        name_elem = card.find_element(By.CSS_SELECTOR, '.invitation-card__name')
                        name = name_elem.text

                        # Extract headline/company
                        headline_elem = card.find_element(By.CSS_SELECTOR, '.invitation-card__occupation')
                        headline = headline_elem.text

                        # Extract profile URL if available
                        profile_url = ''
                        try:
                            profile_link = card.find_element(By.CSS_SELECTOR, 'a[href*="/in/"]')
                            profile_url = profile_link.get_attribute('href')
                        except NoSuchElementException:
                            pass

                        # Build event
                        raw_event = {
                            'type': 'connection_request',
                            'timestamp': datetime.now().isoformat() + 'Z',
                            'priority': 'low',
                            'subject': 'Connection Request',
                            'body': f"I'd like to add you to my professional network on LinkedIn.",
                            'from': name,
                            'to': 'me',
                            'attachments': [],
                            'metadata': {
                                'labels': ['connection_request'],
                                'is_reply': False,
                                'contact_history': 'new',
                                'raw_data': {
                                    'profile_url': profile_url,
                                    'headline': headline
                                }
                            }
                        }

                        events.append(raw_event)

                    except Exception as e:
                        continue

            except NoSuchElementException:
                # No connection requests found
                pass

        except Exception as e:
            self.logger.error(
                component="watcher",
                action="fetch_connections_failed",
                actor="linkedin_watcher",
                target="linkedin",
                details={"error": str(e)}
            )

        return events

    def _fetch_messages(self) -> List[Dict[str, Any]]:
        """
        Fetch new LinkedIn messages.

        Returns:
            List of message events
        """
        events = []

        try:
            # Navigate to messaging
            self.driver.get('https://www.linkedin.com/messaging/')
            time.sleep(3)

            # Find unread message conversations
            try:
                unread_convos = self.driver.find_elements(
                    By.CSS_SELECTOR,
                    'li.msg-conversation-listitem--unread'
                )

                for convo in unread_convos[:5]:  # Limit to 5 most recent
                    try:
                        # Extract sender name
                        name_elem = convo.find_element(By.CSS_SELECTOR, '.msg-conversation-card__participant-names')
                        name = name_elem.text

                        # Extract message preview
                        preview_elem = convo.find_element(By.CSS_SELECTOR, '.msg-conversation-card__message-snippet')
                        preview = preview_elem.text

                        # Build event
                        raw_event = {
                            'type': 'new_message',
                            'timestamp': datetime.now().isoformat() + 'Z',
                            'priority': 'medium',
                            'subject': 'LinkedIn Message',
                            'body': preview,
                            'from': name,
                            'to': 'me',
                            'attachments': [],
                            'metadata': {
                                'labels': ['message'],
                                'is_reply': False,
                                'contact_history': 'known',
                                'raw_data': {}
                            }
                        }

                        events.append(raw_event)

                    except Exception:
                        continue

            except NoSuchElementException:
                # No unread messages
                pass

        except Exception as e:
            self.logger.error(
                component="watcher",
                action="fetch_messages_failed",
                actor="linkedin_watcher",
                target="linkedin",
                details={"error": str(e)}
            )

        return events

    def fetch_new_events(self) -> List[Dict[str, Any]]:
        """
        Fetch new events from LinkedIn.

        Returns:
            List of raw event dictionaries
        """
        # Login if not already logged in
        if not self._login():
            return []

        events = []

        # Fetch connection requests
        events.extend(self._fetch_connection_requests())

        # Fetch messages
        events.extend(self._fetch_messages())

        return events

    def cleanup(self) -> None:
        """Cleanup resources (close browser)."""
        if self.driver:
            try:
                self.driver.quit()
            except Exception:
                pass
            self.driver = None
            self.is_logged_in = False


def main():
    """Run LinkedIn watcher in standalone mode."""
    import argparse

    parser = argparse.ArgumentParser(description='LinkedIn Watcher')
    parser.add_argument('--test-login', action='store_true', help='Test login only')
    parser.add_argument('--test', action='store_true', help='Run one poll cycle and exit')
    parser.add_argument('--interval', type=int, default=600, help='Poll interval in seconds')

    args = parser.parse_args()

    watcher = LinkedInWatcher(poll_interval=args.interval)

    try:
        if args.test_login:
            print("Testing LinkedIn login...")
            if watcher._login():
                print("✓ Login successful")
            else:
                print("✗ Login failed")
            return

        if args.test:
            print("Running test poll...")
            count = watcher.poll_once()
            print(f"✓ Found {count} new events")
            return

        print(f"Starting LinkedIn watcher (polling every {args.interval} seconds)...")
        print("Press Ctrl+C to stop")
        watcher.run()

    finally:
        watcher.cleanup()


if __name__ == '__main__':
    main()
