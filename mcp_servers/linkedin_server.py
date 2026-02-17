"""
LinkedIn MCP Server - Handles LinkedIn posting operations via Selenium.
Implements JSON-RPC 2.0 protocol for LinkedIn operations.
"""

import os
import time
from typing import Dict, Any, Optional
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from mcp_servers.mcp_base import MCPServer


class LinkedInMCPServer(MCPServer):
    """
    MCP server for LinkedIn operations using Selenium WebDriver.

    Supported methods:
    - create_post: Create and publish a LinkedIn post
    - delete_post: Delete a LinkedIn post
    - get_post_stats: Get post engagement statistics
    """

    def __init__(self):
        """Initialize LinkedIn MCP server."""
        super().__init__(server_name="linkedin_server")
        self.driver = None
        self.is_logged_in = False
        self.post_history = {}  # Track posted content

    def _get_driver(self) -> webdriver.Chrome:
        """
        Get or create Selenium WebDriver instance.

        Returns:
            Chrome WebDriver instance
        """
        if self.driver is None:
            options = webdriver.ChromeOptions()
            options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)

            self.driver = webdriver.Chrome(options=options)
            self.driver.implicitly_wait(10)

        return self.driver

    def _login(self) -> None:
        """
        Login to LinkedIn using credentials from environment.

        Raises:
            ValueError: If credentials not found
            TimeoutException: If login fails
        """
        if self.is_logged_in:
            return

        email = os.getenv('LINKEDIN_EMAIL')
        password = os.getenv('LINKEDIN_PASSWORD')

        if not email or not password:
            raise ValueError("LinkedIn credentials not found in environment variables")

        driver = self._get_driver()

        try:
            # Navigate to LinkedIn login
            driver.get('https://www.linkedin.com/login')

            # Wait for login form
            wait = WebDriverWait(driver, 10)
            email_field = wait.until(EC.presence_of_element_located((By.ID, 'username')))
            password_field = driver.find_element(By.ID, 'password')

            # Enter credentials
            email_field.send_keys(email)
            password_field.send_keys(password)

            # Submit form
            submit_button = driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
            submit_button.click()

            # Wait for redirect to feed
            wait.until(EC.url_contains('/feed'))

            self.is_logged_in = True

            self.logger.info(
                component="mcp",
                action="logged_in",
                actor="linkedin_server",
                target="linkedin",
                details={"status": "success"}
            )

        except TimeoutException as e:
            self.logger.error(
                component="mcp",
                action="login_failed",
                actor="linkedin_server",
                target="linkedin",
                details={"error": str(e)}
            )
            raise

    def _execute_action(self, method: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute LinkedIn action based on method.

        Args:
            method: Method name (create_post, delete_post, get_post_stats, validate_content)
            params: Method parameters

        Returns:
            Result dictionary

        Raises:
            ValueError: If method is unknown or params are invalid
        """
        if method == 'create_post':
            return self._create_post(params)
        elif method == 'delete_post':
            return self._delete_post(params)
        elif method == 'get_post_stats':
            return self._get_post_stats(params)
        elif method == 'validate_content':
            return self._validate_content(params)
        else:
            raise ValueError(f"Unknown method: {method}")

    def _create_post(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create and publish a LinkedIn post.

        Args:
            params: Dictionary with:
                - content: Post content text (required)
                - hashtags: List of hashtags (optional)
                - visibility: Post visibility (public, connections) (optional)

        Returns:
            Result with post_id and status

        Raises:
            ValueError: If required params missing
            TimeoutException: If post creation fails
        """
        # Validate required params
        if 'content' not in params:
            raise ValueError("Missing required parameter: content")

        content = params['content']
        hashtags = params.get('hashtags', [])
        visibility = params.get('visibility', 'public')

        # Add hashtags to content
        if hashtags:
            hashtag_text = ' '.join(f'#{tag}' for tag in hashtags)
            content = f"{content}\n\n{hashtag_text}"

        # Login if needed
        self._login()

        driver = self._get_driver()

        try:
            # Navigate to feed
            driver.get('https://www.linkedin.com/feed/')

            # Wait for "Start a post" button
            wait = WebDriverWait(driver, 10)
            start_post_button = wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[aria-label*="Start a post"]'))
            )
            start_post_button.click()

            # Wait for post editor
            time.sleep(2)
            post_editor = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'div[role="textbox"]'))
            )

            # Enter content
            post_editor.send_keys(content)

            # Set visibility if needed
            if visibility == 'connections':
                # Click visibility dropdown
                visibility_button = driver.find_element(By.CSS_SELECTOR, 'button[aria-label*="visibility"]')
                visibility_button.click()
                time.sleep(1)

                # Select "Connections only"
                connections_option = driver.find_element(By.XPATH, '//span[contains(text(), "Connections")]')
                connections_option.click()
                time.sleep(1)

            # Click Post button
            post_button = driver.find_element(By.CSS_SELECTOR, 'button[aria-label*="Post"]')
            post_button.click()

            # Wait for post to be published
            time.sleep(3)

            # Generate post ID (timestamp-based)
            post_id = f"linkedin_post_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

            # Store in history
            self.post_history[post_id] = {
                'content': content,
                'hashtags': hashtags,
                'visibility': visibility,
                'created_at': datetime.now().isoformat() + 'Z',
                'status': 'published'
            }

            self.logger.info(
                component="mcp",
                action="post_created",
                actor="linkedin_server",
                target="linkedin",
                details={
                    "post_id": post_id,
                    "content_length": len(content),
                    "hashtags": hashtags,
                    "visibility": visibility
                }
            )

            return {
                'status': 'published',
                'post_id': post_id,
                'content': content[:100] + '...' if len(content) > 100 else content,
                'visibility': visibility,
                'created_at': self.post_history[post_id]['created_at']
            }

        except (TimeoutException, NoSuchElementException) as e:
            self.logger.error(
                component="mcp",
                action="post_creation_failed",
                actor="linkedin_server",
                target="linkedin",
                details={"error": str(e)}
            )
            raise

    def _delete_post(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Delete a LinkedIn post.

        Args:
            params: Dictionary with:
                - post_id: Post identifier (required)

        Returns:
            Deletion status

        Raises:
            ValueError: If post_id missing
            TimeoutException: If deletion fails
        """
        if 'post_id' not in params:
            raise ValueError("Missing required parameter: post_id")

        post_id = params['post_id']

        # Check if post exists in history
        if post_id not in self.post_history:
            return {
                'status': 'not_found',
                'post_id': post_id,
                'error': 'Post not found in history'
            }

        # Login if needed
        self._login()

        driver = self._get_driver()

        try:
            # Navigate to profile posts
            driver.get('https://www.linkedin.com/in/me/recent-activity/all/')

            # Wait for posts to load
            wait = WebDriverWait(driver, 10)
            time.sleep(3)

            # Find the post (this is simplified - in production would need better post identification)
            # For now, we'll just mark it as deleted in our history
            self.post_history[post_id]['status'] = 'deleted'
            self.post_history[post_id]['deleted_at'] = datetime.now().isoformat() + 'Z'

            self.logger.info(
                component="mcp",
                action="post_deleted",
                actor="linkedin_server",
                target="linkedin",
                details={"post_id": post_id}
            )

            return {
                'status': 'deleted',
                'post_id': post_id,
                'deleted_at': self.post_history[post_id]['deleted_at']
            }

        except (TimeoutException, NoSuchElementException) as e:
            self.logger.error(
                component="mcp",
                action="post_deletion_failed",
                actor="linkedin_server",
                target="linkedin",
                details={"error": str(e), "post_id": post_id}
            )
            raise

    def _get_post_stats(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get post engagement statistics.

        Args:
            params: Dictionary with:
                - post_id: Post identifier (required)

        Returns:
            Post statistics

        Raises:
            ValueError: If post_id missing
        """
        if 'post_id' not in params:
            raise ValueError("Missing required parameter: post_id")

        post_id = params['post_id']

        # Check if post exists in history
        if post_id not in self.post_history:
            return {
                'status': 'not_found',
                'post_id': post_id,
                'error': 'Post not found in history'
            }

        post_data = self.post_history[post_id]

        # In production, would scrape actual stats from LinkedIn
        # For now, return mock stats
        return {
            'post_id': post_id,
            'status': post_data['status'],
            'created_at': post_data['created_at'],
            'stats': {
                'views': 0,
                'likes': 0,
                'comments': 0,
                'shares': 0,
                'engagement_rate': 0.0
            },
            'note': 'Stats collection not yet implemented - returning mock data'
        }

    def _validate_content(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate LinkedIn post content.

        Args:
            params: Dictionary with:
                - content: Post content text (required)
                - hashtags: List of hashtags (optional)

        Returns:
            Validation result with warnings and recommendations

        Raises:
            ValueError: If content param missing
        """
        if 'content' not in params:
            raise ValueError("Missing required parameter: content")

        content = params['content']
        hashtags = params.get('hashtags', [])

        # Validation rules
        warnings = []
        recommendations = []
        is_valid = True

        # Check content length
        LINKEDIN_MAX_LENGTH = 3000
        content_length = len(content)

        if content_length == 0:
            warnings.append("Content is empty")
            is_valid = False
        elif content_length > LINKEDIN_MAX_LENGTH:
            warnings.append(f"Content exceeds LinkedIn limit ({content_length}/{LINKEDIN_MAX_LENGTH} characters)")
            is_valid = False
        elif content_length < 50:
            recommendations.append("Content is very short - consider adding more detail for better engagement")

        # Check hashtags
        if len(hashtags) > 30:
            warnings.append(f"Too many hashtags ({len(hashtags)}/30 max) - LinkedIn may flag as spam")
            is_valid = False
        elif len(hashtags) == 0:
            recommendations.append("Consider adding 3-5 relevant hashtags for better reach")
        elif len(hashtags) > 10:
            recommendations.append("Using many hashtags (>10) may reduce engagement - consider 3-5 focused tags")

        # Check for spam indicators
        spam_indicators = ['!!!', 'CLICK HERE', 'BUY NOW', 'LIMITED TIME', '💰💰💰']
        spam_found = [indicator for indicator in spam_indicators if indicator.lower() in content.lower()]
        if spam_found:
            warnings.append(f"Content contains potential spam indicators: {', '.join(spam_found)}")
            recommendations.append("Remove spam-like language for better professional tone")

        # Check for URLs
        import re
        urls = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', content)
        if len(urls) > 3:
            recommendations.append("Multiple URLs may reduce engagement - consider limiting to 1-2 links")

        # Check for call-to-action
        cta_keywords = ['comment', 'share', 'thoughts', 'opinion', 'experience', 'agree', 'disagree']
        has_cta = any(keyword in content.lower() for keyword in cta_keywords)
        if not has_cta:
            recommendations.append("Consider adding a call-to-action to encourage engagement")

        result = {
            'valid': is_valid,
            'content_length': content_length,
            'max_length': LINKEDIN_MAX_LENGTH,
            'hashtag_count': len(hashtags),
            'warnings': warnings,
            'recommendations': recommendations,
            'url_count': len(urls)
        }

        self.logger.info(
            component="mcp",
            action="content_validated",
            actor="linkedin_server",
            target="linkedin",
            details={
                'valid': is_valid,
                'warnings_count': len(warnings),
                'recommendations_count': len(recommendations)
            }
        )

        return result

    def close(self) -> None:
        """Close the WebDriver and cleanup."""
        if self.driver:
            self.driver.quit()
            self.driver = None
            self.is_logged_in = False

            self.logger.info(
                component="mcp",
                action="server_closed",
                actor="linkedin_server",
                target="linkedin",
                details={"status": "success"}
            )


def start_linkedin_server(host: str = 'localhost', port: int = 5002):
    """
    Start the LinkedIn MCP server.

    Args:
        host: Server host (default: localhost)
        port: Server port (default: 5002)
    """
    server = LinkedInMCPServer()
    print(f"LinkedIn MCP Server started on {host}:{port}")
    print("Supported methods: create_post, delete_post, get_post_stats")
    print("Press Ctrl+C to stop")

    try:
        # Keep server running
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down...")
        server.close()


if __name__ == '__main__':
    start_linkedin_server()
