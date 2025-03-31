import os
import json
import time
import requests
import tweepy
import facebook
import logging
from datetime import datetime, timedelta
from urllib.parse import urlparse
import random
import hashlib
import re

class SNSPoster:
    """
    Class for posting content to various social networking services.
    """
    def __init__(self, config_path=None):
        """
        Initialize the SNSPoster.
        
        Args:
            config_path (str): Path to configuration file
        """
        self.config = self._load_config(config_path)
        self.data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".sns_data")
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Set up logging
        self.logger = self._setup_logging()
        
        # Initialize history
        self.history_file = os.path.join(self.data_dir, "posting_history.json")
        self.history = self._load_history()
        
        # Initialize API clients
        self.api_clients = {}
        self._initialize_api_clients()
    
    def _setup_logging(self):
        """
        Set up logging for the SNSPoster.
        
        Returns:
            logging.Logger: Configured logger
        """
        logger = logging.getLogger("SNSPoster")
        logger.setLevel(logging.INFO)
        
        # Create file handler
        log_file = os.path.join(self.data_dir, "sns_poster.log")
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.INFO)
        
        # Create console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Create formatter
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # Add handlers to logger
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
        return logger
    
    def _load_config(self, config_path):
        """
        Load configuration from file or use defaults.
        
        Args:
            config_path (str): Path to configuration file
            
        Returns:
            dict: Configuration dictionary
        """
        default_config = {
            "platforms": {
                "twitter": {
                    "enabled": True,
                    "api_key": "",
                    "api_secret": "",
                    "access_token": "",
                    "token_secret": "",
                    "max_length": 280,
                    "include_link": True,
                    "include_hashtags": True,
                    "max_hashtags": 3
                },
                "facebook": {
                    "enabled": False,
                    "page_id": "",
                    "access_token": "",
                    "include_image": True,
                    "include_link": True
                },
                "linkedin": {
                    "enabled": False,
                    "access_token": "",
                    "include_image": True,
                    "include_link": True
                },
                "instagram": {
                    "enabled": False,
                    "username": "",
                    "password": "",
                    "require_image": True
                }
            },
            "posting": {
                "max_posts_per_day": 10,
                "min_interval_minutes": 30,
                "best_times": ["8:00", "12:00", "17:00", "20:00"],
                "include_source_attribution": True,
                "add_utm_parameters": True
            },
            "content": {
                "title_formats": [
                    "Breaking: {title}",
                    "Just in: {title}",
                    "{title}",
                    "News: {title}"
                ],
                "hashtag_sources": ["categories", "trending", "custom"],
                "custom_hashtags": ["news", "update", "trending"],
                "max_title_length": 100,
                "include_summary": True,
                "max_summary_length": 100
            },
            "image_handling": {
                "download_images": True,
                "image_download_path": "./images",
                "default_image": "",
                "resize_images": True,
                "max_image_width": 1200,
                "max_image_height": 1200
            },
            "error_handling": {
                "max_retries": 3,
                "retry_delay": 5,
                "log_errors": True,
                "notify_on_error": False,
                "notification_email": ""
            }
        }
        
        if config_path and os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    user_config = json.load(f)
                    # Merge user config with defaults
                    for key, value in user_config.items():
                        if key in default_config and isinstance(value, dict):
                            default_config[key].update(value)
                        else:
                            default_config[key] = value
            except Exception as e:
                self.logger.error(f"Error loading config file: {e}")
                
        return default_config
    
    def _load_history(self):
        """
        Load posting history from file.
        
        Returns:
            dict: History dictionary
        """
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                self.logger.error(f"Error loading history: {e}")
                
        return {"posts": [], "last_updated": datetime.now().isoformat()}
    
    def _save_history(self):
        """
        Save posting history to file.
        """
        try:
            with open(self.history_file, 'w') as f:
                json.dump(self.history, f, indent=2)
        except Exception as e:
            self.logger.error(f"Error saving history: {e}")
    
    def _initialize_api_clients(self):
        """
        Initialize API clients for each platform.
        """
        # Initialize Twitter API client
        if self.config["platforms"]["twitter"]["enabled"]:
            twitter_config = self.config["platforms"]["twitter"]
            if twitter_config["api_key"] and twitter_config["api_secret"] and twitter_config["access_token"] and twitter_config["token_secret"]:
                try:
                    auth = tweepy.OAuth1UserHandler(
                        twitter_config["api_key"],
                        twitter_config["api_secret"],
                        twitter_config["access_token"],
                        twitter_config["token_secret"]
                    )
                    self.api_clients["twitter"] = tweepy.API(auth)
                    self.logger.info("Twitter API client initialized")
                except Exception as e:
                    self.logger.error(f"Error initializing Twitter API client: {e}")
            else:
                self.logger.warning("Twitter is enabled but credentials are missing")
        
        # Initialize Facebook API client
        if self.config["platforms"]["facebook"]["enabled"]:
            facebook_config = self.config["platforms"]["facebook"]
            if facebook_config["access_token"]:
                try:
                    self.api_clients["facebook"] = facebook.GraphAPI(facebook_config["access_token"])
                    self.logger.info("Facebook API client initialized")
                except Exception as e:
                    self.logger.error(f"Error initializing Facebook API client: {e}")
            else:
                self.logger.warning("Facebook is enabled but access token is missing")
        
        # LinkedIn and Instagram would require additional libraries or approaches
        # This is a placeholder for those implementations
        if self.config["platforms"]["linkedin"]["enabled"]:
            self.logger.info("LinkedIn API client initialization would go here")
            
        if self.config["platforms"]["instagram"]["enabled"]:
            self.logger.info("Instagram API client initialization would go here")
    
    def _format_post_text(self, article, platform):
        """
        Format article data into post text for a specific platform.
        
        Args:
            article (dict): Article data
            platform (str): Platform name
            
        Returns:
            str: Formatted post text
        """
        platform_config = self.config["platforms"].get(platform, {})
        content_config = self.config["content"]
        
        # Select a random title format
        title_format = random.choice(content_config["title_formats"])
        formatted_title = title_format.format(title=article["title"])
        
        # Truncate title if needed
        if len(formatted_title) > content_config["max_title_length"]:
            formatted_title = formatted_title[:content_config["max_title_length"] - 3] + "..."
        
        # Start building the post
        post_text = formatted_title
        
        # Add summary if configured
        if content_config["include_summary"] and "summary" in article:
            summary = article["summary"]
            if len(summary) > content_config["max_summary_length"]:
                summary = summary[:content_config["max_summary_length"] - 3] + "..."
            post_text += f"\n\n{summary}"
        
        # Add source attribution if configured
        if self.config["posting"]["include_source_attribution"] and "source" in article:
            post_text += f"\n\nSource: {article['source']}"
        
        # Add link if configured
        if platform_config.get("include_link", True) and "url" in article:
            url = article["url"]
            
            # Add UTM parameters if configured
            if self.config["posting"]["add_utm_parameters"]:
                utm_params = f"utm_source={platform}&utm_medium=social&utm_campaign=news_bot"
                if "?" in url:
                    url += f"&{utm_params}"
                else:
                    url += f"?{utm_params}"
                    
            post_text += f"\n\n{url}"
        
        # Add hashtags if configured
        if platform_config.get("include_hashtags", False):
            hashtags = self._generate_hashtags(article)
            if hashtags:
                hashtag_text = " ".join(hashtags[:platform_config.get("max_hashtags", 3)])
                post_text += f"\n\n{hashtag_text}"
        
        # Truncate to platform limits
        max_length = platform_config.get("max_length", 5000)
        if len(post_text) > max_length:
            # Try to preserve the URL by truncating the text before it
            url_index = post_text.find("http")
            if url_index > 0 and url_index < max_length - 30:  # Ensure there's room for the URL
                truncated_text = post_text[:url_index].strip()
                if len(truncated_text) > max_length - 30 - 3:
                    truncated_text = truncated_text[:max_length - 30 - 3] + "..."
                post_text = truncated_text + "\n\n" + post_text[url_index:]
            else:
                post_text = post_text[:max_length - 3] + "..."
        
        return post_text
    
    def _generate_hashtags(self, article):
        """
        Generate hashtags for an article.
        
        Args:
            article (dict): Article data
            
        Returns:
            list: List of hashtags
        """
        hashtags = []
        hashtag_sources = self.config["content"]["hashtag_sources"]
        
        # Add from categories
        if "categories" in hashtag_sources and "categories" in article:
            for category in article["categories"]:
                # Clean and format category
                clean_category = re.sub(r'[^\w]', '', category)
                if clean_category:
                    hashtags.append(f"#{clean_category}")
        
        # Add from keywords if available
        if "keywords" in article:
            for keyword in article["keywords"][:3]:  # Limit to top 3 keywords
                # Clean and format keyword
                clean_keyword = re.sub(r'[^\w]', '', keyword)
                if clean_keyword:
                    hashtags.append(f"#{clean_keyword}")
        
        # Add custom hashtags
        if "custom" in hashtag_sources:
            custom_hashtags = self.config["content"]["custom_hashtags"]
            for tag in custom_hashtags:
                hashtags.append(f"#{tag}")
        
        # Remove duplicates and return
        return list(set(hashtags))
    
    def _can_post_now(self, platform):
        """
        Check if we can post to a platform now based on daily limits and intervals.
        
        Args:
            platform (str): Platform name
            
        Returns:
            bool: True if posting is allowed, False otherwise
        """
        now = datetime.now()
        today = now.strftime("%Y-%m-%d")
        
        # Count posts today for this platform
        posts_today = 0
        for post in self.history["posts"]:
            post_date = datetime.fromisoformat(post["timestamp"]).strftime("%Y-%m-%d")
            if post_date == today and post["platform"] == platform:
                posts_today += 1
        
        # Check daily limit
        if posts_today >= self.config["posting"]["max_posts_per_day"]:
            self.logger.info(f"Daily posting limit reached for {platform}")
            return False
        
        # Check interval
        if self.history["posts"]:
            last_post = None
            for post in reversed(self.history["posts"]):
                if post["platform"] == platform:
                    last_post = post
                    break
                    
            if last_post:
                last_post_time = datetime.fromisoformat(last_post["timestamp"])
                minutes_since_last = (now - last_post_time).total_seconds() / 60
                
                if minutes_since_last < self.config["posting"]["min_interval_minutes"]:
                    self.logger.info(f"Minimum interval not reached for {platform}, {minutes_since_last:.1f} minutes since last post")
                    return False
        
        return True
    
    def _is_good_posting_time(self):
        """
        Check if current time is a good time to post based on configuration.
        
        Returns:
            bool: True if it's a good time to post, False otherwise
        """
        now = datetime.now()
        current_time = now.strftime("%H:%M")
        
        # Check if current time is close to any of the best times
        best_times = self.config["posting"]["best_times"]
        for best_time in best_times:
            best_hour, best_minute = map(int, best_time.split(":"))
            current_hour, current_minute = map(int, current_time.split(":"))
            
            # Calculate difference in minutes
            best_total_minutes = best_hour * 60 + best_minute
            current_total_minutes = current_hour * 60 + current_minute
            diff_minutes = abs(best_total_minutes - current_total_minutes)
            
            # If within 30 minutes of a best time, it's a good time to post
            if diff_minutes <= 30:
                return True
        
        # If no best times are configured, always return True
        return not best_times
    
    def _download_image(self, image_url):
        """
        Download an image from a URL.
        
        Args:
            image_url (str): URL of the image
            
        Returns:
            str: Path to downloaded image or None if download failed
        """
        if not self.config["image_handling"]["download_images"]:
            return None
            
        try:
            # Create download directory if it doesn't exist
            download_path = self.config["image_handling"]["image_download_path"]
            os.makedirs(download_path, exist_ok=True)
            
            # Generate filename from URL
            filename = hashlib.md5(image_url.encode()).hexdigest() + ".jpg"
            filepath = os.path.join(download_path, filename)
            
            # Check if file already exists
            if os.path.exists(filepath):
                self.logger.info(f"Image already downloaded: {filepath}")
                return filepath
            
            # Download the image
            response = requests.get(image_url, timeout=10)
            if response.status_code == 200:
                with open(filepath, 'wb') as f:
                    f.write(response.content)
                self.logger.info(f"Image downloaded: {filepath}")
                return filepath
            else:
                self.logger.error(f"Failed to download image: {image_url}, status code: {response.status_code}")
                return None
                
        except Exception as e:
            self.logger.error(f"Error downloading image {image_url}: {str(e)}")
            return None
    
    def _post_to_twitter(self, post_text, image_path=None, retry_count=0):
        """
        Post to Twitter.
        
        Args:
            post_text (str): Text to post
            image_path (str): Optional path to image file
            retry_count (int): Current retry count
            
        Returns:
            dict: Result dictionary
        """
        twitter_config = self.config["platforms"]["twitter"]
        max_retries = self.config["error_handling"]["max_retries"]
        
        if not twitter_config.get("api_key") or not twitter_config.get("api_secret") or not twitter_config.get("access_token") or not twitter_config.get("token_secret"):
            return {"success": False, "error": "Twitter API credentials not configured"}
        
        if "twitter" not in self.api_clients:
            return {"success": False, "error": "Twitter API client not initialized"}
        
        try:
            twitter_api = self.api_clients["twitter"]
            
            # Post with or without media
            if image_path and os.path.exists(image_path):
                self.logger.info(f"Posting to Twitter with image: {image_path}")
                media = twitter_api.media_upload(image_path)
                result = twitter_api.update_status(status=post_text, media_ids=[media.media_id])
            else:
                self.logger.info("Posting to Twitter without image")
                result = twitter_api.update_status(status=post_text)
            
            # Return success result
            return {
                "success": True,
                "post_id": str(result.id),
                "url": f"https://twitter.com/user/status/{result.id}"
            }
            
        except Exception as e:
            error_msg = str(e)
            self.logger.error(f"Error posting to Twitter: {error_msg}")
            
            # Retry if not exceeded max retries
            if retry_count < max_retries:
                retry_delay = self.config["error_handling"]["retry_delay"]
                self.logger.info(f"Retrying Twitter post in {retry_delay} seconds (attempt {retry_count + 1}/{max_retries})")
                time.sleep(retry_delay)
                return self._post_to_twitter(post_text, image_path, retry_count + 1)
            
            return {"success": False, "error": error_msg}
    
    def _post_to_facebook(self, post_text, image_path=None, retry_count=0):
        """
        Post to Facebook.
        
        Args:
            post_text (str): Text to post
            image_path (str): Optional path to image file
            retry_count (int): Current retry count
            
        Returns:
            dict: Result dictionary
        """
        facebook_config = self.config["platforms"]["facebook"]
        max_retries = self.config["error_handling"]["max_retries"]
        
        if not facebook_config.get("page_id") or not facebook_config.get("access_token"):
            return {"success": False, "error": "Facebook API credentials not configured"}
        
        if "facebook" not in self.api_clients:
            return {"success": False, "error": "Facebook API client not initialized"}
        
        try:
            facebook_api = self.api_clients["facebook"]
            page_id = facebook_config["page_id"]
            
            # Post with or without media
            if image_path and os.path.exists(image_path):
                self.logger.info(f"Posting to Facebook with image: {image_path}")
                with open(image_path, 'rb') as image_file:
                    result = facebook_api.put_photo(
                        image=image_file,
                        message=post_text,
                        album_path=f"{page_id}/photos"
                    )
            else:
                self.logger.info("Posting to Facebook without image")
                result = facebook_api.put_object(
                    parent_object=page_id,
                    connection_name="feed",
                    message=post_text
                )
            
            # Return success result
            post_id = result.get("id", "unknown")
            return {
                "success": True,
                "post_id": post_id,
                "url": f"https://facebook.com/{post_id}"
            }
            
        except Exception as e:
            error_msg = str(e)
            self.logger.error(f"Error posting to Facebook: {error_msg}")
            
            # Retry if not exceeded max retries
            if retry_count < max_retries:
                retry_delay = self.config["error_handling"]["retry_delay"]
                self.logger.info(f"Retrying Facebook post in {retry_delay} seconds (attempt {retry_count + 1}/{max_retries})")
                time.sleep(retry_delay)
                return self._post_to_facebook(post_text, image_path, retry_count + 1)
            
            return {"success": False, "error": error_msg}
    
    def _post_to_linkedin(self, post_text, image_path=None, retry_count=0):
        """
        Post to LinkedIn.
        
        Args:
            post_text (str): Text to post
            image_path (str): Optional path to image file
            retry_count (int): Current retry count
            
        Returns:
            dict: Result dictionary
        """
        linkedin_config = self.config["platforms"]["linkedin"]
        max_retries = self.config["error_handling"]["max_retries"]
        
        if not linkedin_config.get("access_token"):
            return {"success": False, "error": "LinkedIn API credentials not configured"}
        
        try:
            # This is a placeholder for actual LinkedIn API implementation
            # In a real implementation, you would use the LinkedIn API to post
            self.logger.info(f"Posting to LinkedIn: {post_text[:50]}...")
            if image_path:
                self.logger.info(f"With image: {image_path}")
                
            # Simulate successful posting
            post_id = f"linkedin_{int(time.time())}"
            return {
                "success": True,
                "post_id": post_id,
                "url": f"https://linkedin.com/post/{post_id}"
            }
            
        except Exception as e:
            error_msg = str(e)
            self.logger.error(f"Error posting to LinkedIn: {error_msg}")
            
            # Retry if not exceeded max retries
            if retry_count < max_retries:
                retry_delay = self.config["error_handling"]["retry_delay"]
                self.logger.info(f"Retrying LinkedIn post in {retry_delay} seconds (attempt {retry_count + 1}/{max_retries})")
                time.sleep(retry_delay)
                return self._post_to_linkedin(post_text, image_path, retry_count + 1)
            
            return {"success": False, "error": error_msg}
    
    def _post_to_instagram(self, post_text, image_path, retry_count=0):
        """
        Post to Instagram.
        
        Args:
            post_text (str): Text to post
            image_path (str): Path to image file (required for Instagram)
            retry_count (int): Current retry count
            
        Returns:
            dict: Result dictionary
        """
        instagram_config = self.config["platforms"]["instagram"]
        max_retries = self.config["error_handling"]["max_retries"]
        
        if not instagram_config.get("username") or not instagram_config.get("password"):
            return {"success": False, "error": "Instagram credentials not configured"}
        
        if not image_path or not os.path.exists(image_path):
            return {"success": False, "error": "Image path is required for Instagram"}
        
        try:
            # This is a placeholder for actual Instagram API implementation
            # In a real implementation, you would use the Instagram API to post
            self.logger.info(f"Posting to Instagram: {post_text[:50]}...")
            self.logger.info(f"With image: {image_path}")
                
            # Simulate successful posting
            post_id = f"instagram_{int(time.time())}"
            return {
                "success": True,
                "post_id": post_id,
                "url": f"https://instagram.com/p/{post_id}"
            }
            
        except Exception as e:
            error_msg = str(e)
            self.logger.error(f"Error posting to Instagram: {error_msg}")
            
            # Retry if not exceeded max retries
            if retry_count < max_retries:
                retry_delay = self.config["error_handling"]["retry_delay"]
                self.logger.info(f"Retrying Instagram post in {retry_delay} seconds (attempt {retry_count + 1}/{max_retries})")
                time.sleep(retry_delay)
                return self._post_to_instagram(post_text, image_path, retry_count + 1)
            
            return {"success": False, "error": error_msg}
    
    def post_article(self, article, platforms=None):
        """
        Post an article to specified platforms.
        
        Args:
            article (dict): Article data
            platforms (list): List of platforms to post to (defaults to all enabled)
            
        Returns:
            dict: Results dictionary
        """
        if not platforms:
            platforms = [p for p, config in self.config["platforms"].items() if config.get("enabled", False)]
        
        results = {}
        
        # Download image if available
        image_path = None
        if "image_url" in article and article["image_url"]:
            image_path = self._download_image(article["image_url"])
        elif "images" in article and article["images"]:
            # Use the first image
            image_path = self._download_image(article["images"][0]["url"])
        
        # If no image was downloaded but we have a default image, use that
        if not image_path and self.config["image_handling"]["default_image"]:
            default_image = self.config["image_handling"]["default_image"]
            if os.path.exists(default_image):
                image_path = default_image
        
        for platform in platforms:
            # Check if platform is enabled
            if not self.config["platforms"].get(platform, {}).get("enabled", False):
                results[platform] = {"success": False, "error": f"Platform {platform} is not enabled"}
                continue
                
            # Check if we can post now
            if not self._can_post_now(platform):
                results[platform] = {"success": False, "error": f"Posting limit reached for {platform}"}
                continue
                
            # Check if it's a good time to post
            if not self._is_good_posting_time():
                results[platform] = {"success": False, "error": "Not an optimal posting time"}
                continue
            
            # Format post text for this platform
            post_text = self._format_post_text(article, platform)
            
            # Post to the platform
            if platform == "twitter":
                result = self._post_to_twitter(post_text, image_path)
            elif platform == "facebook":
                result = self._post_to_facebook(post_text, image_path)
            elif platform == "linkedin":
                result = self._post_to_linkedin(post_text, image_path)
            elif platform == "instagram":
                # Instagram requires an image
                if not image_path:
                    result = {"success": False, "error": "Image is required for Instagram"}
                else:
                    result = self._post_to_instagram(post_text, image_path)
            else:
                result = {"success": False, "error": f"Unsupported platform: {platform}"}
            
            results[platform] = result
            
            # Record in history if successful
            if result.get("success", False):
                self.history["posts"].append({
                    "article_id": article.get("id", hashlib.md5(article["url"].encode()).hexdigest()),
                    "platform": platform,
                    "post_id": result.get("post_id", ""),
                    "url": result.get("url", ""),
                    "timestamp": datetime.now().isoformat()
                })
                self._save_history()
        
        return results
    
    def post_multiple_articles(self, articles, platforms=None):
        """
        Post multiple articles to social media.
        
        Args:
            articles (list): List of article dictionaries
            platforms (list): List of platforms to post to
            
        Returns:
            list: List of result dictionaries
        """
        results = []
        
        for article in articles:
            # Post the article
            post_results = self.post_article(article, platforms)
            
            # Check if posting was successful on any platform
            success = any(result.get("success", False) for result in post_results.values())
            
            results.append({
                "article": {
                    "id": article.get("id", hashlib.md5(article["url"].encode()).hexdigest()),
                    "title": article["title"],
                    "url": article["url"]
                },
                "results": post_results,
                "success": success
            })
        
        return results
    
    def schedule_posts(self, articles, platforms=None):
        """
        Schedule posts throughout the day.
        
        Args:
            articles (list): List of article dictionaries
            platforms (list): List of platforms to post to
            
        Returns:
            dict: Schedule dictionary
        """
        if not platforms:
            platforms = [p for p, config in self.config["platforms"].items() if config.get("enabled", False)]
            
        # Get best posting times
        best_times = self.config["posting"]["best_times"]
        if not best_times:
            # Default to evenly spaced times during the day
            posts_per_day = min(len(articles), self.config["posting"]["max_posts_per_day"])
            hours_between = 24 / posts_per_day
            best_times = [f"{int(i * hours_between):02d}:00" for i in range(posts_per_day)]
        
        # Filter out already posted articles
        filtered_articles = []
        for article in articles:
            article_id = article.get("id", hashlib.md5(article["url"].encode()).hexdigest())
            already_posted = False
            for post in self.history["posts"]:
                if post["article_id"] == article_id:
                    already_posted = True
                    break
                    
            if not already_posted:
                filtered_articles.append(article)
        
        # Create schedule
        schedule = []
        now = datetime.now()
        today = now.strftime("%Y-%m-%d")
        
        for i in range(min(len(filtered_articles), self.config["posting"]["max_posts_per_day"], len(best_times))):
            time_str = best_times[i % len(best_times)]
            hour, minute = map(int, time_str.split(":"))
            
            scheduled_time = datetime(now.year, now.month, now.day, hour, minute)
            
            # If time is in the past, schedule for tomorrow
            if scheduled_time < now:
                scheduled_time = scheduled_time.replace(day=scheduled_time.day + 1)
            
            schedule.append({
                "article": {
                    "id": filtered_articles[i].get("id", hashlib.md5(filtered_articles[i]["url"].encode()).hexdigest()),
                    "title": filtered_articles[i]["title"],
                    "url": filtered_articles[i]["url"]
                },
                "scheduled_time": scheduled_time.isoformat(),
                "platforms": platforms
            })
        
        return {
            "date": today,
            "posts": schedule
        }
    
    def get_posting_stats(self, days=7):
        """
        Get posting statistics.
        
        Args:
            days (int): Number of days to include in stats
            
        Returns:
            dict: Statistics dictionary
        """
        now = datetime.now()
        cutoff_date = (now - timedelta(days=days)).isoformat()
        
        # Filter recent posts
        recent_posts = [post for post in self.history["posts"] if post["timestamp"] >= cutoff_date]
        
        # Count by platform
        platform_counts = {}
        for post in recent_posts:
            platform = post["platform"]
            if platform in platform_counts:
                platform_counts[platform] += 1
            else:
                platform_counts[platform] = 1
        
        # Count by day
        day_counts = {}
        for post in recent_posts:
            day = datetime.fromisoformat(post["timestamp"]).strftime("%Y-%m-%d")
            if day in day_counts:
                day_counts[day] += 1
            else:
                day_counts[day] = 1
        
        # Get most recent posts
        most_recent = sorted(recent_posts, key=lambda x: x["timestamp"], reverse=True)[:5]
        recent_posts_data = []
        
        for post in most_recent:
            recent_posts_data.append({
                "platform": post["platform"],
                "timestamp": post["timestamp"],
                "url": post["url"],
                "article_id": post["article_id"]
            })
        
        return {
            "total_posts": len(recent_posts),
            "platform_counts": platform_counts,
            "day_counts": day_counts,
            "recent_posts": recent_posts_data
        }
    
    def run_scheduled_posting(self, schedule):
        """
        Run scheduled posting based on a schedule.
        
        Args:
            schedule (dict): Schedule dictionary
            
        Returns:
            dict: Results dictionary
        """
        results = {
            "scheduled": len(schedule["posts"]),
            "posted": 0,
            "failed": 0,
            "skipped": 0,
            "posts": []
        }
        
        now = datetime.now()
        
        for post in schedule["posts"]:
            scheduled_time = datetime.fromisoformat(post["scheduled_time"])
            
            # If post is due (scheduled time is in the past)
            if scheduled_time <= now:
                self.logger.info(f"Posting scheduled article: {post['article']['title']}")
                
                # Find the full article data
                # In a real implementation, you would need to retrieve the article data
                # This is a placeholder
                article_data = {
                    "id": post["article"]["id"],
                    "title": post["article"]["title"],
                    "url": post["article"]["url"],
                    "summary": "This is a placeholder summary for the scheduled article."
                }
                
                # Post the article
                post_results = self.post_article(article_data, post["platforms"])
                
                # Check if posting was successful on any platform
                success = any(result.get("success", False) for result in post_results.values())
                
                if success:
                    results["posted"] += 1
                else:
                    results["failed"] += 1
                
                results["posts"].append({
                    "article": post["article"],
                    "scheduled_time": post["scheduled_time"],
                    "results": post_results,
                    "success": success
                })
            else:
                # Post is not due yet
                results["skipped"] += 1
        
        return results


# Example usage
if __name__ == "__main__":
    # Create a SNS poster
    poster = SNSPoster()
    
    # Post an article
    article = {
        "title": "Example News Article",
        "url": "https://example.com/news/article",
        "summary": "This is an example news article for testing the SNS poster.",
        "image_url": "https://example.com/news/article/image.jpg",
        "categories": ["technology", "news"],
        "keywords": ["example", "test", "news"]
    }
    
    results = poster.post_article(article, platforms=["twitter"])
    print(f"Posting results: {results}")
    
    # Get posting stats
    stats = poster.get_posting_stats(days=7)
    print(f"Posting stats: {stats}")
    
    # Schedule posts
    articles = [
        {
            "title": "Example News Article 1",
            "url": "https://example.com/news/article1",
            "summary": "This is example news article 1."
        },
        {
            "title": "Example News Article 2",
            "url": "https://example.com/news/article2",
            "summary": "This is example news article 2."
        },
        {
            "title": "Example News Article 3",
            "url": "https://example.com/news/article3",
            "summary": "This is example news article 3."
        }
    ]
    
    schedule = poster.schedule_posts(articles, platforms=["twitter"])
    print(f"Schedule: {schedule}")
    
    # Run scheduled posting
    results = poster.run_scheduled_posting(schedule)
    print(f"Scheduled posting results: {results}")
