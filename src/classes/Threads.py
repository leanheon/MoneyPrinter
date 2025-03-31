import os
import json
import time
import requests
from uuid import uuid4
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.common import exceptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from src.config import get_config
from src.constants import ROOT_DIR
from src.cache import get_accounts, add_post
from src.status import get_verbose
from src.openai_generator import OpenAIGenerator

class Threads:
    """
    Class for the Threads Bot, that posts content to Meta's Threads platform.
    """
    def __init__(self, account_uuid: str, account_nickname: str, topic: str = None) -> None:
        """
        Initializes the Threads Bot.

        Args:
            account_uuid (str): The account UUID
            account_nickname (str): The account nickname
            topic (str, optional): The topic to create content about
        """
        self.account_uuid = account_uuid
        self.account_nickname = account_nickname
        self.topic = topic
        
        # Get account config from cache
        cached_accounts = get_accounts("threads")
        self.account_config = None
        
        for account in cached_accounts:
            if account["id"] == self.account_uuid:
                self.account_config = account
                break
                
        if not self.account_config:
            raise Exception("Account configuration not found")
            
        # Initialize OpenAI generator
        self.openai_generator = OpenAIGenerator()
        
        # Initialize Firefox profile path
        self.fp_profile_path = self.account_config.get("fp_profile_path", "")
        
        # Initialize options
        self.options = Options()
        
        # Set headless state of browser
        if self.get_headless():
            self.options.add_argument("--headless")
            
        # Set the profile path
        self.options.add_argument("--profile")
        self.options.add_argument(self.fp_profile_path)
        
        # Set the service
        self.service = Service(GeckoDriverManager().install())
        
        # Initialize the browser
        self.browser = webdriver.Firefox(service=self.service, options=self.options)
        
    def generate_post(self):
        """
        Generate a post for Threads
        
        Returns:
            str: Generated post content
        """
        system_message = f"You are a social media expert who creates engaging content for {self.account_config.get('niche', 'general')} on Meta's Threads platform."
        
        prompt = f"""
        Create an engaging, concise post for Meta's Threads platform about {self.topic or self.account_config.get('niche', 'general')}.
        
        The post should:
        - Be under 500 characters (Threads limit)
        - Be conversational and engaging
        - Include a question or call to action to encourage replies
        - Include 2-3 relevant hashtags
        - Be suitable for the Threads platform audience
        
        Just provide the post text with no additional explanation or formatting.
        """
        
        post_content = self.openai_generator.generate_content(prompt, system_message, max_tokens=300)
        
        if self.get_verbose():
            print(f" => Generated Threads post: {post_content}")
            
        return post_content.strip() if post_content else f"Check out this interesting content about {self.topic or self.account_config.get('niche', 'general')}! #threads"
        
    def generate_image_post(self):
        """
        Generate a post with an image for Threads
        
        Returns:
            tuple: (post_content, image_path)
        """
        # Generate post content
        post_content = self.generate_post()
        
        # Generate image prompt
        system_message = "You are a creative prompt engineer for visual content."
        
        prompt = f"""
        Create a detailed image prompt for DALL-E based on this topic:
        
        {self.topic or self.account_config.get('niche', 'general')}
        
        The prompt should:
        - Be visually descriptive and detailed
        - Include style guidance (photorealistic, illustration, etc.)
        - Mention lighting, perspective, and mood
        - NOT include any text overlays or words to appear in the image
        
        Just provide the prompt text with no additional explanation or formatting.
        """
        
        image_prompt = self.openai_generator.generate_content(prompt, system_message, max_tokens=200)
        
        if not image_prompt:
            image_prompt = f"A high-quality image about {self.topic or self.account_config.get('niche', 'general')}"
            
        # Generate image
        image_path = self.openai_generator.generate_image(image_prompt)
        
        if self.get_verbose() and image_path:
            print(f" => Generated image for Threads post: {image_path}")
            
        return post_content, image_path
        
    def post(self, text: str = None) -> None:
        """
        Starts the Threads Bot.

        Args:
            text (str, optional): The text to post
        """
        if self.get_verbose():
            print(colored(f" => Posting to Threads: ", "blue"), post_content[:30] + "...")
            
        # Generate post content if not provided
        post_content = text if text else self.generate_post()
        
        try:
            # Navigate to Threads
            self.browser.get("https://threads.net")
            
            time.sleep(2)
            
            # Find and click the "New thread" button
            try:
                new_thread_button = self.browser.find_element(By.XPATH, "//button[contains(@aria-label, 'New thread')]")
                new_thread_button.click()
            except exceptions.NoSuchElementException:
                if self.get_verbose():
                    print("New thread button not found. Trying alternative method.")
                # Try alternative method - look for the compose icon
                new_thread_button = self.browser.find_element(By.XPATH, "//a[contains(@href, '/create')]")
                new_thread_button.click()
                
            time.sleep(2)
            
            # Find the text input area and enter the post content
            try:
                text_area = self.browser.find_element(By.XPATH, "//div[contains(@aria-label, 'Thread text')]")
                text_area.send_keys(post_content)
            except exceptions.NoSuchElementException:
                if self.get_verbose():
                    print("Text area not found. Trying alternative method.")
                # Try alternative method
                text_area = self.browser.find_element(By.XPATH, "//div[contains(@role, 'textbox')]")
                text_area.send_keys(post_content)
                
            time.sleep(1)
            
            # Find and click the post button
            post_button = self.browser.find_element(By.XPATH, "//button[contains(text(), 'Post') or contains(@aria-label, 'Post')]")
            post_button.click()
            
            time.sleep(4)  # Wait for post to be published
            
            if self.get_verbose():
                print("Posted to Threads successfully!")
                
            # Add the post to the cache
            add_post({
                "content": post_content,
                "date": datetime.now().strftime("%m/%d/%Y, %H:%M:%S"),
                "platform": "threads",
                "account_id": self.account_uuid
            })
            
            return True
            
        except Exception as e:
            if self.get_verbose():
                print(f"Error posting to Threads: {e}")
            return False
            
    def post_with_image(self, text: str = None, image_path: str = None) -> None:
        """
        Posts content with an image to Threads.

        Args:
            text (str, optional): The text to post
            image_path (str, optional): Path to the image to upload
            
        Returns:
            bool: True if successful, False otherwise
        """
        # Generate content and image if not provided
        if not text or not image_path:
            post_content, generated_image_path = self.generate_image_post()
            text = text or post_content
            image_path = image_path or generated_image_path
            
        if not image_path:
            if self.get_verbose():
                print("No image available. Posting text only.")
            return self.post(text)
            
        if self.get_verbose():
            print(colored(f" => Posting to Threads with image: ", "blue"), text[:30] + "...")
            
        try:
            # Navigate to Threads
            self.browser.get("https://threads.net")
            
            time.sleep(2)
            
            # Find and click the "New thread" button
            try:
                new_thread_button = self.browser.find_element(By.XPATH, "//button[contains(@aria-label, 'New thread')]")
                new_thread_button.click()
            except exceptions.NoSuchElementException:
                if self.get_verbose():
                    print("New thread button not found. Trying alternative method.")
                # Try alternative method - look for the compose icon
                new_thread_button = self.browser.find_element(By.XPATH, "//a[contains(@href, '/create')]")
                new_thread_button.click()
                
            time.sleep(2)
            
            # Find and click the image upload button
            try:
                image_button = self.browser.find_element(By.XPATH, "//input[@type='file' or @accept='image/*']")
                image_button.send_keys(image_path)
            except exceptions.NoSuchElementException:
                if self.get_verbose():
                    print("Image upload button not found. Trying alternative method.")
                # Try alternative method
                image_button = self.browser.find_element(By.XPATH, "//div[contains(@aria-label, 'Add photo')]")
                image_button.click()
                time.sleep(1)
                file_input = self.browser.find_element(By.XPATH, "//input[@type='file']")
                file_input.send_keys(image_path)
                
            time.sleep(3)  # Wait for image to upload
            
            # Find the text input area and enter the post content
            try:
                text_area = self.browser.find_element(By.XPATH, "//div[contains(@aria-label, 'Thread text')]")
                text_area.send_keys(text)
            except exceptions.NoSuchElementException:
                if self.get_verbose():
                    print("Text area not found. Trying alternative method.")
                # Try alternative method
                text_area = self.browser.find_element(By.XPATH, "//div[contains(@role, 'textbox')]")
                text_area.send_keys(text)
                
            time.sleep(1)
            
            # Find and click the post button
            post_button = self.browser.find_element(By.XPATH, "//button[contains(text(), 'Post') or contains(@aria-label, 'Post')]")
            post_button.click()
            
            time.sleep(4)  # Wait for post to be published
            
            if self.get_verbose():
                print("Posted to Threads with image successfully!")
                
            # Add the post to the cache
            add_post({
                "content": text,
                "date": datetime.now().strftime("%m/%d/%Y, %H:%M:%S"),
                "platform": "threads",
                "account_id": self.account_uuid,
                "has_media": True
            })
            
            return True
            
        except Exception as e:
            if self.get_verbose():
                print(f"Error posting to Threads with image: {e}")
            return False
            
    def get_posts(self) -> list:
        """
        Gets the posts from the cache.
        
        Returns:
            list: The posts from the cache
        """
        from src.cache import get_posts
        return get_posts(self.account_uuid, "threads")
        
    def get_headless(self) -> bool:
        """
        Returns whether headless mode is enabled
        
        Returns:
            bool: True if headless mode is enabled, False otherwise
        """
        return self.account_config.get("headless", True)
        
    def get_verbose(self) -> bool:
        """
        Returns whether verbose mode is enabled
        
        Returns:
            bool: True if verbose mode is enabled, False otherwise
        """
        return get_verbose()
        
    def __del__(self):
        """
        Closes the browser when the object is deleted
        """
        try:
            self.browser.quit()
        except:
            pass
