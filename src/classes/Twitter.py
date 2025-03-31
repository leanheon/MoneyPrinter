import re
import g4f
import sys
import time
from datetime import datetime
from termcolor import colored
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.common import exceptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.firefox import GeckoDriverManager

from src.config import get_config
from src.status import get_verbose
from src.cache import add_post, get_accounts
from src.openai_generator import OpenAIGenerator

class Twitter:
    """
    Class for the Bot, that grows a Twitter account.
    """
    def __init__(self, account_uuid: str, account_nickname: str, fp_profile_path: str, topic: str) -> None:
        """
        Initializes the Twitter Bot.

        Args:
            account_uuid (str): The account UUID
            account_nickname (str): The account nickname
            fp_profile_path (str): The path to the Firefox profile
            topic (str): The topic to post about
        """
        self.account_uuid = account_uuid
        self.account_nickname = account_nickname
        self.fp_profile_path = fp_profile_path
        self.topic = topic

        # Get account config from cache
        cached_accounts = get_accounts("twitter")
        self.account_config = None
        
        for account in cached_accounts:
            if account["id"] == self.account_uuid:
                self.account_config = account
                break
                
        if not self.account_config:
            raise Exception("Account configuration not found")
            
        # Initialize OpenAI generator
        self.openai_generator = OpenAIGenerator()

        # Initialize the Firefox profile
        self.options = Options()
        
        # Set headless state of browser
        if self.get_headless():
            self.options.add_argument("--headless")

        # Set the profile path
        self.options.add_argument("--profile")
        self.options.add_argument(fp_profile_path)

        # Set the service
        self.service = Service(GeckoDriverManager().install())

        # Initialize the browser
        self.browser = webdriver.Firefox(service=self.service, options=self.options)

    def generate_post(self):
        """
        Generate a post for X (Twitter)
        
        Returns:
            str: Generated post content
        """
        system_message = f"You are a social media expert who creates engaging content for {self.account_config.get('niche', 'general')} on X (formerly Twitter)."
        
        prompt = f"""
        Create an engaging, concise post for X (formerly Twitter) about {self.topic}.
        
        The post should:
        - Be under 280 characters (X's character limit)
        - Be conversational and engaging
        - Include 2-3 relevant hashtags
        - Encourage interaction (likes, reposts, replies)
        - Be suitable for the X platform audience
        
        Just provide the post text with no additional explanation or formatting.
        """
        
        post_content = self.openai_generator.generate_content(prompt, system_message, max_tokens=200)
        
        if self.get_verbose():
            print(f" => Generated X post: {post_content}")
            
        return post_content.strip() if post_content else f"Check out this interesting content about {self.topic}! #x #content"

    def post(self, text: str = None) -> None:
        """
        Starts the Twitter Bot.

        Args:
            text (str, optional): The text to post
        """
        # Generate post content if not provided
        post_content = text if text else self.generate_post()
        
        if self.get_verbose():
            print(colored(f" => Posting to X: ", "blue"), post_content[:30] + "...")

        try:
            bot = self.browser
            bot.get("https://twitter.com")

            time.sleep(2)

            try:
                # Find the "Post" button (new X interface)
                bot.find_element(By.XPATH, "//a[@data-testid='SideNav_NewTweet_Button']").click()
            except exceptions.NoSuchElementException:
                # Try alternative selector for the post button
                time.sleep(3)
                bot.find_element(By.XPATH, "//div[@role='button' and @aria-label='Post']").click()

            time.sleep(2)

            # Find the text input area and enter the post content
            body = post_content if text is None else text
            
            try:
                # Try to find the text input by data-testid
                bot.find_element(By.XPATH, "//div[@role='textbox']").send_keys(body)
            except exceptions.NoSuchElementException:
                # Try alternative selector for the text input
                bot.find_element(By.XPATH, "//div[@data-testid='tweetTextarea_0']").send_keys(body)

            time.sleep(1)

            # Find and click the post button
            try:
                # Try to find the post button by text content
                bot.find_element(By.XPATH, "//div[@data-testid='tweetButton']").click()
            except exceptions.NoSuchElementException:
                # Try alternative selector for the post button
                bot.find_element(By.XPATH, "//span[text()='Post']").click()

            if self.get_verbose():
                print(colored(f" => Pressed [ENTER] Button on X...", "blue"))

            time.sleep(4)  # Wait for post to be published

            # Add the post to the cache
            add_post({
                "content": post_content,
                "date": datetime.now().strftime("%m/%d/%Y, %H:%M:%S"),
                "platform": "twitter",
                "account_id": self.account_uuid
            })

            if self.get_verbose():
                print(colored("Posted to X successfully!", "green"))
                
            return True

        except Exception as e:
            if self.get_verbose():
                print(colored(f"Failed to post to X: {str(e)}", "red"))
            return False

    def post_with_image(self, text: str = None, image_path: str = None) -> None:
        """
        Posts content with an image to X (Twitter).

        Args:
            text (str, optional): The text to post
            image_path (str, optional): Path to the image to upload
            
        Returns:
            bool: True if successful, False otherwise
        """
        # Generate content if not provided
        post_content = text if text else self.generate_post()
        
        # Generate image if not provided
        if not image_path:
            # Generate image prompt
            system_message = "You are a creative prompt engineer for visual content."
            
            prompt = f"""
            Create a detailed image prompt for DALL-E based on this topic:
            
            {self.topic}
            
            The prompt should:
            - Be visually descriptive and detailed
            - Include style guidance (photorealistic, illustration, etc.)
            - Mention lighting, perspective, and mood
            - NOT include any text overlays or words to appear in the image
            
            Just provide the prompt text with no additional explanation or formatting.
            """
            
            image_prompt = self.openai_generator.generate_content(prompt, system_message, max_tokens=200)
            
            if not image_prompt:
                image_prompt = f"A high-quality image about {self.topic}"
                
            # Generate image
            image_path = self.openai_generator.generate_image(image_prompt)
            
        if not image_path:
            if self.get_verbose():
                print("No image available. Posting text only.")
            return self.post(post_content)
            
        if self.get_verbose():
            print(colored(f" => Posting to X with image: ", "blue"), post_content[:30] + "...")

        try:
            bot = self.browser
            bot.get("https://twitter.com")

            time.sleep(2)

            try:
                # Find the "Post" button (new X interface)
                bot.find_element(By.XPATH, "//a[@data-testid='SideNav_NewTweet_Button']").click()
            except exceptions.NoSuchElementException:
                # Try alternative selector for the post button
                time.sleep(3)
                bot.find_element(By.XPATH, "//div[@role='button' and @aria-label='Post']").click()

            time.sleep(2)

            # Find the text input area and enter the post content
            try:
                # Try to find the text input by data-testid
                bot.find_element(By.XPATH, "//div[@role='textbox']").send_keys(post_content)
            except exceptions.NoSuchElementException:
                # Try alternative selector for the text input
                bot.find_element(By.XPATH, "//div[@data-testid='tweetTextarea_0']").send_keys(post_content)

            time.sleep(1)

            # Find and click the image upload button
            try:
                # Try to find the image upload button by data-testid
                file_input = bot.find_element(By.XPATH, "//input[@data-testid='fileInput']")
                file_input.send_keys(image_path)
            except exceptions.NoSuchElementException:
                # Try alternative selector for the image upload button
                file_input = bot.find_element(By.XPATH, "//input[@type='file']")
                file_input.send_keys(image_path)

            time.sleep(3)  # Wait for image to upload

            # Find and click the post button
            try:
                # Try to find the post button by text content
                bot.find_element(By.XPATH, "//div[@data-testid='tweetButton']").click()
            except exceptions.NoSuchElementException:
                # Try alternative selector for the post button
                bot.find_element(By.XPATH, "//span[text()='Post']").click()

            if self.get_verbose():
                print(colored(f" => Pressed [ENTER] Button on X...", "blue"))

            time.sleep(4)  # Wait for post to be published

            # Add the post to the cache
            add_post({
                "content": post_content,
                "date": datetime.now().strftime("%m/%d/%Y, %H:%M:%S"),
                "platform": "twitter",
                "account_id": self.account_uuid,
                "has_media": True
            })

            if self.get_verbose():
                print(colored("Posted to X with image successfully!", "green"))
                
            return True

        except Exception as e:
            if self.get_verbose():
                print(colored(f"Failed to post to X with image: {str(e)}", "red"))
            return False

    def get_posts(self) -> list:
        """
        Gets the posts from the cache.
        
        Returns:
            list: The posts from the cache
        """
        from src.cache import get_posts
        return get_posts(self.account_uuid, "twitter")
        
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
