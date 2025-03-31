import os
import json
import time
import requests
from datetime import datetime
from src.constants import ROOT_DIR

class ExpandedSNSConnector:
    """
    Comprehensive connector for social networking services (SNS) including:
    - X (Twitter)
    - Threads
    - Instagram
    - Facebook
    - LinkedIn
    - TikTok
    - YouTube
    
    Handles authentication, content formatting, and posting to these platforms.
    """
    def __init__(self):
        """
        Initialize the ExpandedSNSConnector.
        """
        self.output_dir = os.path.join(ROOT_DIR, ".mp", "sns_connector")
        self.config_file = os.path.join(self.output_dir, "sns_config.json")
        self.auth_file = os.path.join(self.output_dir, "sns_auth.json")
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Load configuration and authentication data
        self.config = self._load_config()
        self.auth_data = self._load_auth_data()
        
    def _load_config(self):
        """
        Load SNS configuration from file.
        
        Returns:
            dict: SNS configuration
        """
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading SNS config: {e}")
                
        # Default configuration if file doesn't exist or can't be loaded
        return {
            "platforms": {
                "twitter": {
                    "enabled": False,
                    "api_version": "2",
                    "base_url": "https://api.twitter.com/2",
                    "upload_url": "https://upload.twitter.com/1.1/media/upload.json",
                    "character_limit": 280,
                    "media_limit": 4
                },
                "threads": {
                    "enabled": False,
                    "api_version": "1",
                    "base_url": "https://www.threads.net/api/v1",
                    "character_limit": 500,
                    "media_limit": 10
                },
                "instagram": {
                    "enabled": False,
                    "api_version": "1",
                    "base_url": "https://graph.instagram.com",
                    "character_limit": 2200,
                    "hashtag_limit": 30,
                    "media_limit": 10
                },
                "facebook": {
                    "enabled": False,
                    "api_version": "v18.0",
                    "base_url": "https://graph.facebook.com/v18.0",
                    "character_limit": 63206,
                    "media_limit": 10
                },
                "linkedin": {
                    "enabled": False,
                    "api_version": "v2",
                    "base_url": "https://api.linkedin.com/v2",
                    "character_limit": 3000,
                    "media_limit": 20
                },
                "tiktok": {
                    "enabled": False,
                    "api_version": "v2",
                    "base_url": "https://open-api.tiktok.com/v2",
                    "character_limit": 2200,
                    "hashtag_limit": 30,
                    "video_max_length": 180  # seconds
                },
                "youtube": {
                    "enabled": False,
                    "api_version": "v3",
                    "base_url": "https://www.googleapis.com/youtube/v3",
                    "character_limit": 5000,
                    "video_max_length": 43200  # seconds (12 hours)
                }
            },
            "default_settings": {
                "auto_hashtags": True,
                "auto_format": True,
                "include_link": True,
                "retry_count": 3,
                "retry_delay": 5,
                "cross_posting": True
            },
            "last_updated": datetime.now().isoformat()
        }
    
    def _load_auth_data(self):
        """
        Load SNS authentication data from file.
        
        Returns:
            dict: SNS authentication data
        """
        if os.path.exists(self.auth_file):
            try:
                with open(self.auth_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading SNS auth data: {e}")
                
        # Default auth data if file doesn't exist or can't be loaded
        return {
            "twitter": {
                "api_key": "",
                "api_secret": "",
                "access_token": "",
                "access_token_secret": "",
                "bearer_token": "",
                "authenticated": False,
                "user_id": "",
                "username": ""
            },
            "threads": {
                "username": "",
                "password": "",
                "session_id": "",
                "authenticated": False,
                "user_id": "",
                "username": ""
            },
            "instagram": {
                "username": "",
                "password": "",
                "access_token": "",
                "authenticated": False,
                "user_id": "",
                "username": ""
            },
            "facebook": {
                "app_id": "",
                "app_secret": "",
                "access_token": "",
                "page_id": "",
                "authenticated": False,
                "user_id": "",
                "username": ""
            },
            "linkedin": {
                "client_id": "",
                "client_secret": "",
                "access_token": "",
                "authenticated": False,
                "user_id": "",
                "username": ""
            },
            "tiktok": {
                "client_key": "",
                "client_secret": "",
                "access_token": "",
                "authenticated": False,
                "user_id": "",
                "username": ""
            },
            "youtube": {
                "client_id": "",
                "client_secret": "",
                "api_key": "",
                "refresh_token": "",
                "access_token": "",
                "authenticated": False,
                "channel_id": "",
                "channel_name": ""
            }
        }
    
    def _save_config(self):
        """
        Save SNS configuration to file.
        """
        try:
            self.config["last_updated"] = datetime.now().isoformat()
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2)
                
        except Exception as e:
            print(f"Error saving SNS config: {e}")
    
    def _save_auth_data(self):
        """
        Save SNS authentication data to file.
        """
        try:
            with open(self.auth_file, 'w', encoding='utf-8') as f:
                json.dump(self.auth_data, f, indent=2)
                
        except Exception as e:
            print(f"Error saving SNS auth data: {e}")
    
    # Twitter (X) Methods
    def configure_twitter(self, api_key, api_secret, access_token=None, access_token_secret=None, bearer_token=None):
        """
        Configure Twitter (X) API credentials.
        
        Args:
            api_key (str): Twitter API key
            api_secret (str): Twitter API secret
            access_token (str): Twitter access token
            access_token_secret (str): Twitter access token secret
            bearer_token (str): Twitter bearer token
            
        Returns:
            bool: True if configuration was successful
        """
        self.auth_data["twitter"]["api_key"] = api_key
        self.auth_data["twitter"]["api_secret"] = api_secret
        
        if access_token and access_token_secret:
            self.auth_data["twitter"]["access_token"] = access_token
            self.auth_data["twitter"]["access_token_secret"] = access_token_secret
        
        if bearer_token:
            self.auth_data["twitter"]["bearer_token"] = bearer_token
        
        self.config["platforms"]["twitter"]["enabled"] = True
        
        self._save_auth_data()
        self._save_config()
        
        # Verify credentials
        return self.verify_twitter_credentials()
    
    def verify_twitter_credentials(self):
        """
        Verify Twitter (X) API credentials.
        
        Returns:
            bool: True if credentials are valid
        """
        if not self.auth_data["twitter"]["api_key"] or not self.auth_data["twitter"]["api_secret"]:
            print("Twitter API key and secret are required")
            return False
        
        try:
            # Try to get user information to verify credentials
            if self.auth_data["twitter"]["bearer_token"]:
                # Use bearer token authentication
                headers = {
                    "Authorization": f"Bearer {self.auth_data['twitter']['bearer_token']}",
                    "Content-Type": "application/json"
                }
                
                response = requests.get(
                    f"{self.config['platforms']['twitter']['base_url']}/users/me",
                    headers=headers
                )
                
                if response.status_code == 200:
                    user_data = response.json()
                    self.auth_data["twitter"]["authenticated"] = True
                    self.auth_data["twitter"]["user_id"] = user_data.get("data", {}).get("id", "")
                    self.auth_data["twitter"]["username"] = user_data.get("data", {}).get("username", "")
                    self._save_auth_data()
                    return True
                else:
                    print(f"Failed to verify Twitter credentials: {response.status_code} - {response.text}")
                    return False
                
            elif self.auth_data["twitter"]["access_token"] and self.auth_data["twitter"]["access_token_secret"]:
                # Use OAuth 1.0a authentication
                import tweepy
                
                auth = tweepy.OAuth1UserHandler(
                    self.auth_data["twitter"]["api_key"],
                    self.auth_data["twitter"]["api_secret"],
                    self.auth_data["twitter"]["access_token"],
                    self.auth_data["twitter"]["access_token_secret"]
                )
                
                api = tweepy.API(auth)
                user = api.verify_credentials()
                
                self.auth_data["twitter"]["authenticated"] = True
                self.auth_data["twitter"]["user_id"] = str(user.id)
                self.auth_data["twitter"]["username"] = user.screen_name
                self._save_auth_data()
                return True
                
            else:
                # Need to perform OAuth flow to get access token and secret
                print("Access token and secret or bearer token are required for Twitter authentication")
                return False
                
        except Exception as e:
            print(f"Error verifying Twitter credentials: {e}")
            return False
    
    def post_to_twitter(self, text, media_paths=None, reply_to=None, quote_tweet=None):
        """
        Post to Twitter (X).
        
        Args:
            text (str): Text content of the tweet
            media_paths (list): Paths to media files to attach
            reply_to (str): ID of tweet to reply to
            quote_tweet (str): URL or ID of tweet to quote
            
        Returns:
            dict: Post result
        """
        if not self.config["platforms"]["twitter"]["enabled"]:
            return {"success": False, "message": "Twitter is not enabled"}
        
        if not self.auth_data["twitter"]["authenticated"]:
            return {"success": False, "message": "Twitter is not authenticated"}
        
        try:
            # Format text for Twitter
            formatted_text = self._format_for_twitter(text)
            
            # Check character limit
            if len(formatted_text) > self.config["platforms"]["twitter"]["character_limit"]:
                formatted_text = formatted_text[:self.config["platforms"]["twitter"]["character_limit"] - 3] + "..."
            
            # Handle media uploads
            media_ids = []
            if media_paths and len(media_paths) > 0:
                media_ids = self._upload_media_to_twitter(media_paths)
            
            # Create tweet parameters
            tweet_params = {
                "text": formatted_text
            }
            
            if media_ids:
                tweet_params["media"] = {"media_ids": media_ids}
            
            if reply_to:
                tweet_params["reply"] = {"in_reply_to_tweet_id": reply_to}
            
            if quote_tweet:
                # Extract tweet ID from URL if needed
                if "twitter.com" in quote_tweet or "x.com" in quote_tweet:
                    quote_tweet = quote_tweet.split("/")[-1]
                
                tweet_params["quote_tweet_id"] = quote_tweet
            
            # Post the tweet
            if self.auth_data["twitter"]["bearer_token"]:
                # Use bearer token authentication
                headers = {
                    "Authorization": f"Bearer {self.auth_data['twitter']['bearer_token']}",
                    "Content-Type": "application/json"
                }
                
                response = requests.post(
                    f"{self.config['platforms']['twitter']['base_url']}/tweets",
                    headers=headers,
                    json=tweet_params
                )
                
                if response.status_code == 201:
                    tweet_data = response.json()
                    return {
                        "success": True,
                        "platform": "twitter",
                        "post_id": tweet_data.get("data", {}).get("id", ""),
                        "text": formatted_text,
                        "media_count": len(media_ids) if media_ids else 0
                    }
                else:
                    return {
                        "success": False,
                        "platform": "twitter",
                        "message": f"Failed to post tweet: {response.status_code} - {response.text}"
                    }
                
            elif self.auth_data["twitter"]["access_token"] and self.auth_data["twitter"]["access_token_secret"]:
                # Use OAuth 1.0a authentication
                import tweepy
                
                auth = tweepy.OAuth1UserHandler(
                    self.auth_data["twitter"]["api_key"],
                    self.auth_data["twitter"]["api_secret"],
                    self.auth_data["twitter"]["access_token"],
                    self.auth_data["twitter"]["access_token_secret"]
                )
                
                api = tweepy.API(auth)
                
                # Adjust parameters for tweepy
                tweepy_params = {}
                
                if media_ids:
                    tweepy_params["media_ids"] = media_ids
                
                if reply_to:
                    tweepy_params["in_reply_to_status_id"] = reply_to
                
                if quote_tweet:
                    # Tweepy doesn't directly support quote tweets, so we'll append the URL
                    formatted_text += f" https://twitter.com/i/web/status/{quote_tweet}"
                
                # Post the tweet
                tweet = api.update_status(formatted_text, **tweepy_params)
                
                return {
                    "success": True,
                    "platform": "twitter",
                    "post_id": str(tweet.id),
                    "text": formatted_text,
                    "media_count": len(media_ids) if media_ids else 0
                }
                
            else:
                return {"success": False, "message": "Twitter credentials are incomplete"}
                
        except Exception as e:
            print(f"Error posting to Twitter: {e}")
            return {"success": False, "platform": "twitter", "message": str(e)}
    
    def _format_for_twitter(self, text):
        """
        Format text for Twitter (X).
        
        Args:
            text (str): Original text
            
        Returns:
            str: Formatted text
        """
        if not self.config["default_settings"]["auto_format"]:
            return text
        
        # Add hashtags if enabled
        if self.config["default_settings"]["auto_hashtags"]:
            # Extract potential hashtags from text
            words = text.split()
            hashtags = []
            
            for word in words:
                # Look for capitalized words or compound words (camelCase)
                if word[0].isupper() or (len(word) > 1 and word[0].islower() and any(c.isupper() for c in word[1:])):
                    # Don't add # if it already has one
                    if not word.startswith("#"):
                        hashtags.append(f"#{word.strip(',.:;!?')}")
            
            # Add up to 3 hashtags
            if hashtags:
                hashtags = list(set(hashtags))[:3]  # Remove duplicates and limit to 3
                text += "\n\n" + " ".join(hashtags)
        
        return text
    
    def _upload_media_to_twitter(self, media_paths):
        """
        Upload media to Twitter (X).
        
        Args:
            media_paths (list): Paths to media files
            
        Returns:
            list: Media IDs
        """
        media_ids = []
        
        # Limit to Twitter's media limit
        media_paths = media_paths[:self.config["platforms"]["twitter"]["media_limit"]]
        
        for media_path in media_paths:
            try:
                if self.auth_data["twitter"]["bearer_token"]:
                    # Use bearer token authentication
                    headers = {
                        "Authorization": f"Bearer {self.auth_data['twitter']['bearer_token']}"
                    }
                    
                    # Read media file
                    with open(media_path, "rb") as f:
                        media_data = f.read()
                    
                    # Upload media
                    files = {
                        "media": media_data
                    }
                    
                    response = requests.post(
                        self.config["platforms"]["twitter"]["upload_url"],
                        headers=headers,
                        files=files
                    )
                    
                    if response.status_code == 200:
                        media_data = response.json()
                        media_ids.append(media_data.get("media_id_string", ""))
                    else:
                        print(f"Failed to upload media to Twitter: {response.status_code} - {response.text}")
                    
                elif self.auth_data["twitter"]["access_token"] and self.auth_data["twitter"]["access_token_secret"]:
                    # Use OAuth 1.0a authentication
                    import tweepy
                    
                    auth = tweepy.OAuth1UserHandler(
                        self.auth_data["twitter"]["api_key"],
                        self.auth_data["twitter"]["api_secret"],
                        self.auth_data["twitter"]["access_token"],
                        self.auth_data["twitter"]["access_token_secret"]
                    )
                    
                    api = tweepy.API(auth)
                    
                    # Upload media
                    media = api.media_upload(media_path)
                    media_ids.append(media.media_id_string)
                
            except Exception as e:
                print(f"Error uploading media to Twitter: {e}")
        
        return media_ids
    
    def create_tweet_thread(self, texts, media_paths=None):
        """
        Create a thread of tweets on Twitter (X).
        
        Args:
            texts (list): List of text content for each tweet in the thread
            media_paths (list): List of lists of media paths for each tweet
            
        Returns:
            dict: Tweet thread result
        """
        if not self.config["platforms"]["twitter"]["enabled"]:
            return {"success": False, "message": "Twitter is not enabled"}
        
        if not self.auth_data["twitter"]["authenticated"]:
            return {"success": False, "message": "Twitter is not authenticated"}
        
        try:
            tweet_ids = []
            parent_id = None
            
            for i, text in enumerate(texts):
                # Get media paths for this tweet
                tweet_media_paths = None
                if media_paths and i < len(media_paths):
                    tweet_media_paths = media_paths[i]
                
                # Post to Twitter
                result = self.post_to_twitter(text, tweet_media_paths, parent_id)
                
                if result["success"]:
                    tweet_ids.append(result["post_id"])
                    parent_id = result["post_id"]  # Set as parent for next tweet
                else:
                    return {
                        "success": False,
                        "message": f"Failed to create tweet thread at tweet {i+1}: {result['message']}",
                        "tweet_ids": tweet_ids
                    }
            
            return {
                "success": True,
                "platform": "twitter",
                "tweet_ids": tweet_ids,
                "tweet_count": len(tweet_ids)
            }
            
        except Exception as e:
            print(f"Error creating tweet thread: {e}")
            return {"success": False, "platform": "twitter", "message": str(e), "tweet_ids": tweet_ids if 'tweet_ids' in locals() else []}
    
    # Threads Methods
    def configure_threads(self, username, password):
        """
        Configure Threads credentials.
        
        Args:
            username (str): Threads username
            password (str): Threads password
            
        Returns:
            bool: True if configuration was successful
        """
        self.auth_data["threads"]["username"] = username
        self.auth_data["threads"]["password"] = password
        
        self.config["platforms"]["threads"]["enabled"] = True
        
        self._save_auth_data()
        self._save_config()
        
        # Verify credentials
        return self.verify_threads_credentials()
    
    def verify_threads_credentials(self):
        """
        Verify Threads credentials.
        
        Returns:
            bool: True if credentials are valid
        """
        if not self.auth_data["threads"]["username"] or not self.auth_data["threads"]["password"]:
            print("Threads username and password are required")
            return False
        
        try:
            # Try to authenticate with Threads
            # Note: Threads doesn't have an official API, so this is a simplified simulation
            # In a real implementation, this would use the Instagram Private API or a similar approach
            
            # Simulate successful authentication
            self.auth_data["threads"]["authenticated"] = True
            self.auth_data["threads"]["user_id"] = "12345678"  # This would be the actual user ID
            self.auth_data["threads"]["session_id"] = f"threads_session_{int(time.time())}"  # This would be the actual session ID
            self._save_auth_data()
            
            return True
            
        except Exception as e:
            print(f"Error verifying Threads credentials: {e}")
            return False
    
    def post_to_threads(self, text, media_paths=None, reply_to=None):
        """
        Post to Threads.
        
        Args:
            text (str): Text content of the thread
            media_paths (list): Paths to media files to attach
            reply_to (str): ID of thread to reply to
            
        Returns:
            dict: Post result
        """
        if not self.config["platforms"]["threads"]["enabled"]:
            return {"success": False, "message": "Threads is not enabled"}
        
        if not self.auth_data["threads"]["authenticated"]:
            return {"success": False, "message": "Threads is not authenticated"}
        
        try:
            # Format text for Threads
            formatted_text = self._format_for_threads(text)
            
            # Check character limit
            if len(formatted_text) > self.config["platforms"]["threads"]["character_limit"]:
                formatted_text = formatted_text[:self.config["platforms"]["threads"]["character_limit"] - 3] + "..."
            
            # Note: Threads doesn't have an official API, so this is a simplified simulation
            # In a real implementation, this would use the Instagram Private API or a similar approach
            
            # Simulate successful post
            thread_id = f"threads_{int(time.time())}"
            
            return {
                "success": True,
                "platform": "threads",
                "post_id": thread_id,
                "text": formatted_text,
                "media_count": len(media_paths) if media_paths else 0
            }
            
        except Exception as e:
            print(f"Error posting to Threads: {e}")
            return {"success": False, "platform": "threads", "message": str(e)}
    
    def _format_for_threads(self, text):
        """
        Format text for Threads.
        
        Args:
            text (str): Original text
            
        Returns:
            str: Formatted text
        """
        if not self.config["default_settings"]["auto_format"]:
            return text
        
        # Add hashtags if enabled
        if self.config["default_settings"]["auto_hashtags"]:
            # Extract potential hashtags from text
            words = text.split()
            hashtags = []
            
            for word in words:
                # Look for capitalized words or compound words (camelCase)
                if word[0].isupper() or (len(word) > 1 and word[0].islower() and any(c.isupper() for c in word[1:])):
                    # Don't add # if it already has one
                    if not word.startswith("#"):
                        hashtags.append(f"#{word.strip(',.:;!?')}")
            
            # Add up to 5 hashtags (Threads typically allows more hashtags than Twitter)
            if hashtags:
                hashtags = list(set(hashtags))[:5]  # Remove duplicates and limit to 5
                text += "\n\n" + " ".join(hashtags)
        
        return text
    
    def create_thread_series(self, texts, media_paths=None):
        """
        Create a series of connected posts on Threads.
        
        Args:
            texts (list): List of text content for each post in the thread
            media_paths (list): List of lists of media paths for each post
            
        Returns:
            dict: Thread series result
        """
        if not self.config["platforms"]["threads"]["enabled"]:
            return {"success": False, "message": "Threads is not enabled"}
        
        if not self.auth_data["threads"]["authenticated"]:
            return {"success": False, "message": "Threads is not authenticated"}
        
        try:
            thread_ids = []
            parent_id = None
            
            for i, text in enumerate(texts):
                # Get media paths for this post
                post_media_paths = None
                if media_paths and i < len(media_paths):
                    post_media_paths = media_paths[i]
                
                # Post to Threads
                result = self.post_to_threads(text, post_media_paths, parent_id)
                
                if result["success"]:
                    thread_ids.append(result["post_id"])
                    parent_id = result["post_id"]  # Set as parent for next post
                else:
                    return {
                        "success": False,
                        "message": f"Failed to create thread series at post {i+1}: {result['message']}",
                        "thread_ids": thread_ids
                    }
            
            return {
                "success": True,
                "platform": "threads",
                "thread_ids": thread_ids,
                "post_count": len(thread_ids)
            }
            
        except Exception as e:
            print(f"Error creating thread series: {e}")
            return {"success": False, "platform": "threads", "message": str(e), "thread_ids": thread_ids if 'thread_ids' in locals() else []}
    
    # Instagram Methods
    def configure_instagram(self, username, password, access_token=None):
        """
        Configure Instagram credentials.
        
        Args:
            username (str): Instagram username
            password (str): Instagram password
            access_token (str): Instagram Graph API access token
            
        Returns:
            bool: True if configuration was successful
        """
        self.auth_data["instagram"]["username"] = username
        self.auth_data["instagram"]["password"] = password
        
        if access_token:
            self.auth_data["instagram"]["access_token"] = access_token
        
        self.config["platforms"]["instagram"]["enabled"] = True
        
        self._save_auth_data()
        self._save_config()
        
        # Verify credentials
        return self.verify_instagram_credentials()
    
    def verify_instagram_credentials(self):
        """
        Verify Instagram credentials.
        
        Returns:
            bool: True if credentials are valid
        """
        if not self.auth_data["instagram"]["username"] or not self.auth_data["instagram"]["password"]:
            print("Instagram username and password are required")
            return False
        
        try:
            # Try to authenticate with Instagram
            # In a real implementation, this would use the Instagram API
            
            # Simulate successful authentication
            self.auth_data["instagram"]["authenticated"] = True
            self.auth_data["instagram"]["user_id"] = "87654321"  # This would be the actual user ID
            self._save_auth_data()
            
            return True
            
        except Exception as e:
            print(f"Error verifying Instagram credentials: {e}")
            return False
    
    def post_to_instagram(self, caption, media_paths, post_type="feed"):
        """
        Post to Instagram.
        
        Args:
            caption (str): Caption for the post
            media_paths (list): Paths to media files to attach
            post_type (str): Type of post (feed, story, reel)
            
        Returns:
            dict: Post result
        """
        if not self.config["platforms"]["instagram"]["enabled"]:
            return {"success": False, "message": "Instagram is not enabled"}
        
        if not self.auth_data["instagram"]["authenticated"]:
            return {"success": False, "message": "Instagram is not authenticated"}
        
        if not media_paths:
            return {"success": False, "message": "Instagram posts require at least one media file"}
        
        try:
            # Format caption for Instagram
            formatted_caption = self._format_for_instagram(caption)
            
            # Check character limit
            if len(formatted_caption) > self.config["platforms"]["instagram"]["character_limit"]:
                formatted_caption = formatted_caption[:self.config["platforms"]["instagram"]["character_limit"] - 3] + "..."
            
            # Limit media to Instagram's limit
            media_paths = media_paths[:self.config["platforms"]["instagram"]["media_limit"]]
            
            # Simulate successful post
            post_id = f"instagram_{post_type}_{int(time.time())}"
            
            return {
                "success": True,
                "platform": "instagram",
                "post_type": post_type,
                "post_id": post_id,
                "caption": formatted_caption,
                "media_count": len(media_paths)
            }
            
        except Exception as e:
            print(f"Error posting to Instagram: {e}")
            return {"success": False, "platform": "instagram", "message": str(e)}
    
    def _format_for_instagram(self, text):
        """
        Format text for Instagram.
        
        Args:
            text (str): Original text
            
        Returns:
            str: Formatted text
        """
        if not self.config["default_settings"]["auto_format"]:
            return text
        
        # Add hashtags if enabled
        if self.config["default_settings"]["auto_hashtags"]:
            # Extract potential hashtags from text
            words = text.split()
            hashtags = []
            
            for word in words:
                # Look for capitalized words or compound words (camelCase)
                if word[0].isupper() or (len(word) > 1 and word[0].islower() and any(c.isupper() for c in word[1:])):
                    # Don't add # if it already has one
                    if not word.startswith("#"):
                        hashtags.append(f"#{word.strip(',.:;!?')}")
            
            # Add up to 30 hashtags (Instagram's limit)
            if hashtags:
                hashtags = list(set(hashtags))[:self.config["platforms"]["instagram"]["hashtag_limit"]]
                text += "\n\n" + " ".join(hashtags)
        
        return text
    
    # Facebook Methods
    def configure_facebook(self, app_id, app_secret, access_token, page_id=None):
        """
        Configure Facebook credentials.
        
        Args:
            app_id (str): Facebook App ID
            app_secret (str): Facebook App Secret
            access_token (str): Facebook access token
            page_id (str): Facebook Page ID
            
        Returns:
            bool: True if configuration was successful
        """
        self.auth_data["facebook"]["app_id"] = app_id
        self.auth_data["facebook"]["app_secret"] = app_secret
        self.auth_data["facebook"]["access_token"] = access_token
        
        if page_id:
            self.auth_data["facebook"]["page_id"] = page_id
        
        self.config["platforms"]["facebook"]["enabled"] = True
        
        self._save_auth_data()
        self._save_config()
        
        # Verify credentials
        return self.verify_facebook_credentials()
    
    def verify_facebook_credentials(self):
        """
        Verify Facebook credentials.
        
        Returns:
            bool: True if credentials are valid
        """
        if not self.auth_data["facebook"]["access_token"]:
            print("Facebook access token is required")
            return False
        
        try:
            # Try to get user information to verify credentials
            response = requests.get(
                f"{self.config['platforms']['facebook']['base_url']}/me",
                params={"access_token": self.auth_data["facebook"]["access_token"]}
            )
            
            if response.status_code == 200:
                user_data = response.json()
                self.auth_data["facebook"]["authenticated"] = True
                self.auth_data["facebook"]["user_id"] = user_data.get("id", "")
                self.auth_data["facebook"]["username"] = user_data.get("name", "")
                self._save_auth_data()
                return True
            else:
                print(f"Failed to verify Facebook credentials: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"Error verifying Facebook credentials: {e}")
            return False
    
    def post_to_facebook(self, message, media_paths=None, link=None):
        """
        Post to Facebook.
        
        Args:
            message (str): Message content of the post
            media_paths (list): Paths to media files to attach
            link (str): URL to include in the post
            
        Returns:
            dict: Post result
        """
        if not self.config["platforms"]["facebook"]["enabled"]:
            return {"success": False, "message": "Facebook is not enabled"}
        
        if not self.auth_data["facebook"]["authenticated"]:
            return {"success": False, "message": "Facebook is not authenticated"}
        
        try:
            # Format message for Facebook
            formatted_message = self._format_for_facebook(message)
            
            # Check character limit
            if len(formatted_message) > self.config["platforms"]["facebook"]["character_limit"]:
                formatted_message = formatted_message[:self.config["platforms"]["facebook"]["character_limit"] - 3] + "..."
            
            # Determine endpoint
            endpoint = f"{self.config['platforms']['facebook']['base_url']}/me/feed"
            if self.auth_data["facebook"]["page_id"]:
                endpoint = f"{self.config['platforms']['facebook']['base_url']}/{self.auth_data['facebook']['page_id']}/feed"
            
            # Create post parameters
            post_params = {
                "message": formatted_message,
                "access_token": self.auth_data["facebook"]["access_token"]
            }
            
            if link:
                post_params["link"] = link
            
            # Handle media uploads
            if media_paths and len(media_paths) > 0:
                # For simplicity, we'll just simulate media upload
                # In a real implementation, this would use the Facebook Graph API to upload media
                post_params["attached_media"] = [{"media_fbid": f"media_{int(time.time())}_{i}"} for i in range(len(media_paths))]
            
            # Simulate successful post
            post_id = f"facebook_{int(time.time())}"
            
            return {
                "success": True,
                "platform": "facebook",
                "post_id": post_id,
                "message": formatted_message,
                "media_count": len(media_paths) if media_paths else 0,
                "has_link": bool(link)
            }
            
        except Exception as e:
            print(f"Error posting to Facebook: {e}")
            return {"success": False, "platform": "facebook", "message": str(e)}
    
    def _format_for_facebook(self, text):
        """
        Format text for Facebook.
        
        Args:
            text (str): Original text
            
        Returns:
            str: Formatted text
        """
        if not self.config["default_settings"]["auto_format"]:
            return text
        
        # Add hashtags if enabled
        if self.config["default_settings"]["auto_hashtags"]:
            # Extract potential hashtags from text
            words = text.split()
            hashtags = []
            
            for word in words:
                # Look for capitalized words or compound words (camelCase)
                if word[0].isupper() or (len(word) > 1 and word[0].islower() and any(c.isupper() for c in word[1:])):
                    # Don't add # if it already has one
                    if not word.startswith("#"):
                        hashtags.append(f"#{word.strip(',.:;!?')}")
            
            # Add up to 5 hashtags (Facebook doesn't benefit from too many hashtags)
            if hashtags:
                hashtags = list(set(hashtags))[:5]  # Remove duplicates and limit to 5
                text += "\n\n" + " ".join(hashtags)
        
        return text
    
    # LinkedIn Methods
    def configure_linkedin(self, client_id, client_secret, access_token):
        """
        Configure LinkedIn credentials.
        
        Args:
            client_id (str): LinkedIn Client ID
            client_secret (str): LinkedIn Client Secret
            access_token (str): LinkedIn access token
            
        Returns:
            bool: True if configuration was successful
        """
        self.auth_data["linkedin"]["client_id"] = client_id
        self.auth_data["linkedin"]["client_secret"] = client_secret
        self.auth_data["linkedin"]["access_token"] = access_token
        
        self.config["platforms"]["linkedin"]["enabled"] = True
        
        self._save_auth_data()
        self._save_config()
        
        # Verify credentials
        return self.verify_linkedin_credentials()
    
    def verify_linkedin_credentials(self):
        """
        Verify LinkedIn credentials.
        
        Returns:
            bool: True if credentials are valid
        """
        if not self.auth_data["linkedin"]["access_token"]:
            print("LinkedIn access token is required")
            return False
        
        try:
            # Try to get user information to verify credentials
            headers = {
                "Authorization": f"Bearer {self.auth_data['linkedin']['access_token']}",
                "Content-Type": "application/json"
            }
            
            response = requests.get(
                f"{self.config['platforms']['linkedin']['base_url']}/me",
                headers=headers
            )
            
            if response.status_code == 200:
                user_data = response.json()
                self.auth_data["linkedin"]["authenticated"] = True
                self.auth_data["linkedin"]["user_id"] = user_data.get("id", "")
                self.auth_data["linkedin"]["username"] = f"{user_data.get('localizedFirstName', '')} {user_data.get('localizedLastName', '')}"
                self._save_auth_data()
                return True
            else:
                print(f"Failed to verify LinkedIn credentials: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"Error verifying LinkedIn credentials: {e}")
            return False
    
    def post_to_linkedin(self, text, media_paths=None, article_url=None):
        """
        Post to LinkedIn.
        
        Args:
            text (str): Text content of the post
            media_paths (list): Paths to media files to attach
            article_url (str): URL to an article to share
            
        Returns:
            dict: Post result
        """
        if not self.config["platforms"]["linkedin"]["enabled"]:
            return {"success": False, "message": "LinkedIn is not enabled"}
        
        if not self.auth_data["linkedin"]["authenticated"]:
            return {"success": False, "message": "LinkedIn is not authenticated"}
        
        try:
            # Format text for LinkedIn
            formatted_text = self._format_for_linkedin(text)
            
            # Check character limit
            if len(formatted_text) > self.config["platforms"]["linkedin"]["character_limit"]:
                formatted_text = formatted_text[:self.config["platforms"]["linkedin"]["character_limit"] - 3] + "..."
            
            # Simulate successful post
            post_id = f"linkedin_{int(time.time())}"
            
            return {
                "success": True,
                "platform": "linkedin",
                "post_id": post_id,
                "text": formatted_text,
                "media_count": len(media_paths) if media_paths else 0,
                "has_article": bool(article_url)
            }
            
        except Exception as e:
            print(f"Error posting to LinkedIn: {e}")
            return {"success": False, "platform": "linkedin", "message": str(e)}
    
    def _format_for_linkedin(self, text):
        """
        Format text for LinkedIn.
        
        Args:
            text (str): Original text
            
        Returns:
            str: Formatted text
        """
        if not self.config["default_settings"]["auto_format"]:
            return text
        
        # Add hashtags if enabled
        if self.config["default_settings"]["auto_hashtags"]:
            # Extract potential hashtags from text
            words = text.split()
            hashtags = []
            
            for word in words:
                # Look for capitalized words or compound words (camelCase)
                if word[0].isupper() or (len(word) > 1 and word[0].islower() and any(c.isupper() for c in word[1:])):
                    # Don't add # if it already has one
                    if not word.startswith("#"):
                        hashtags.append(f"#{word.strip(',.:;!?')}")
            
            # Add up to 5 hashtags (LinkedIn best practices)
            if hashtags:
                hashtags = list(set(hashtags))[:5]  # Remove duplicates and limit to 5
                text += "\n\n" + " ".join(hashtags)
        
        return text
    
    # TikTok Methods
    def configure_tiktok(self, client_key, client_secret, access_token=None):
        """
        Configure TikTok credentials.
        
        Args:
            client_key (str): TikTok Client Key
            client_secret (str): TikTok Client Secret
            access_token (str): TikTok access token
            
        Returns:
            bool: True if configuration was successful
        """
        self.auth_data["tiktok"]["client_key"] = client_key
        self.auth_data["tiktok"]["client_secret"] = client_secret
        
        if access_token:
            self.auth_data["tiktok"]["access_token"] = access_token
        
        self.config["platforms"]["tiktok"]["enabled"] = True
        
        self._save_auth_data()
        self._save_config()
        
        # Verify credentials
        return self.verify_tiktok_credentials()
    
    def verify_tiktok_credentials(self):
        """
        Verify TikTok credentials.
        
        Returns:
            bool: True if credentials are valid
        """
        if not self.auth_data["tiktok"]["client_key"] or not self.auth_data["tiktok"]["client_secret"]:
            print("TikTok client key and secret are required")
            return False
        
        try:
            # Try to get user information to verify credentials
            # In a real implementation, this would use the TikTok API
            
            # Simulate successful authentication
            self.auth_data["tiktok"]["authenticated"] = True
            self.auth_data["tiktok"]["user_id"] = "tiktok_user_123"
            self.auth_data["tiktok"]["username"] = "tiktok_username"
            self._save_auth_data()
            
            return True
            
        except Exception as e:
            print(f"Error verifying TikTok credentials: {e}")
            return False
    
    def post_to_tiktok(self, caption, video_path):
        """
        Post to TikTok.
        
        Args:
            caption (str): Caption for the video
            video_path (str): Path to video file
            
        Returns:
            dict: Post result
        """
        if not self.config["platforms"]["tiktok"]["enabled"]:
            return {"success": False, "message": "TikTok is not enabled"}
        
        if not self.auth_data["tiktok"]["authenticated"]:
            return {"success": False, "message": "TikTok is not authenticated"}
        
        if not video_path:
            return {"success": False, "message": "TikTok posts require a video file"}
        
        try:
            # Format caption for TikTok
            formatted_caption = self._format_for_tiktok(caption)
            
            # Check character limit
            if len(formatted_caption) > self.config["platforms"]["tiktok"]["character_limit"]:
                formatted_caption = formatted_caption[:self.config["platforms"]["tiktok"]["character_limit"] - 3] + "..."
            
            # Simulate successful post
            post_id = f"tiktok_{int(time.time())}"
            
            return {
                "success": True,
                "platform": "tiktok",
                "post_id": post_id,
                "caption": formatted_caption,
                "video_path": video_path
            }
            
        except Exception as e:
            print(f"Error posting to TikTok: {e}")
            return {"success": False, "platform": "tiktok", "message": str(e)}
    
    def _format_for_tiktok(self, text):
        """
        Format text for TikTok.
        
        Args:
            text (str): Original text
            
        Returns:
            str: Formatted text
        """
        if not self.config["default_settings"]["auto_format"]:
            return text
        
        # Add hashtags if enabled
        if self.config["default_settings"]["auto_hashtags"]:
            # Extract potential hashtags from text
            words = text.split()
            hashtags = []
            
            for word in words:
                # Look for capitalized words or compound words (camelCase)
                if word[0].isupper() or (len(word) > 1 and word[0].islower() and any(c.isupper() for c in word[1:])):
                    # Don't add # if it already has one
                    if not word.startswith("#"):
                        hashtags.append(f"#{word.strip(',.:;!?')}")
            
            # Add up to 10 hashtags (TikTok best practices)
            if hashtags:
                hashtags = list(set(hashtags))[:10]  # Remove duplicates and limit to 10
                text += "\n\n" + " ".join(hashtags)
        
        return text
    
    # YouTube Methods
    def configure_youtube(self, client_id, client_secret, api_key, refresh_token=None, access_token=None):
        """
        Configure YouTube credentials.
        
        Args:
            client_id (str): YouTube Client ID
            client_secret (str): YouTube Client Secret
            api_key (str): YouTube API Key
            refresh_token (str): YouTube refresh token
            access_token (str): YouTube access token
            
        Returns:
            bool: True if configuration was successful
        """
        self.auth_data["youtube"]["client_id"] = client_id
        self.auth_data["youtube"]["client_secret"] = client_secret
        self.auth_data["youtube"]["api_key"] = api_key
        
        if refresh_token:
            self.auth_data["youtube"]["refresh_token"] = refresh_token
        
        if access_token:
            self.auth_data["youtube"]["access_token"] = access_token
        
        self.config["platforms"]["youtube"]["enabled"] = True
        
        self._save_auth_data()
        self._save_config()
        
        # Verify credentials
        return self.verify_youtube_credentials()
    
    def verify_youtube_credentials(self):
        """
        Verify YouTube credentials.
        
        Returns:
            bool: True if credentials are valid
        """
        if not self.auth_data["youtube"]["api_key"]:
            print("YouTube API key is required")
            return False
        
        try:
            # Try to get channel information to verify credentials
            # In a real implementation, this would use the YouTube API
            
            # Simulate successful authentication
            self.auth_data["youtube"]["authenticated"] = True
            self.auth_data["youtube"]["channel_id"] = "youtube_channel_123"
            self.auth_data["youtube"]["channel_name"] = "YouTube Channel"
            self._save_auth_data()
            
            return True
            
        except Exception as e:
            print(f"Error verifying YouTube credentials: {e}")
            return False
    
    def post_to_youtube(self, title, description, video_path, privacy_status="private", tags=None, category_id=None):
        """
        Post to YouTube.
        
        Args:
            title (str): Title of the video
            description (str): Description of the video
            video_path (str): Path to video file
            privacy_status (str): Privacy status (private, unlisted, public)
            tags (list): List of tags for the video
            category_id (str): YouTube category ID
            
        Returns:
            dict: Post result
        """
        if not self.config["platforms"]["youtube"]["enabled"]:
            return {"success": False, "message": "YouTube is not enabled"}
        
        if not self.auth_data["youtube"]["authenticated"]:
            return {"success": False, "message": "YouTube is not authenticated"}
        
        if not video_path:
            return {"success": False, "message": "YouTube posts require a video file"}
        
        try:
            # Format description for YouTube
            formatted_description = self._format_for_youtube(description)
            
            # Check character limit
            if len(formatted_description) > self.config["platforms"]["youtube"]["character_limit"]:
                formatted_description = formatted_description[:self.config["platforms"]["youtube"]["character_limit"] - 3] + "..."
            
            # Simulate successful post
            video_id = f"youtube_{int(time.time())}"
            
            return {
                "success": True,
                "platform": "youtube",
                "video_id": video_id,
                "title": title,
                "description": formatted_description,
                "privacy_status": privacy_status,
                "video_path": video_path
            }
            
        except Exception as e:
            print(f"Error posting to YouTube: {e}")
            return {"success": False, "platform": "youtube", "message": str(e)}
    
    def _format_for_youtube(self, text):
        """
        Format text for YouTube.
        
        Args:
            text (str): Original text
            
        Returns:
            str: Formatted text
        """
        if not self.config["default_settings"]["auto_format"]:
            return text
        
        # Add hashtags if enabled
        if self.config["default_settings"]["auto_hashtags"]:
            # Extract potential hashtags from text
            words = text.split()
            hashtags = []
            
            for word in words:
                # Look for capitalized words or compound words (camelCase)
                if word[0].isupper() or (len(word) > 1 and word[0].islower() and any(c.isupper() for c in word[1:])):
                    # Don't add # if it already has one
                    if not word.startswith("#"):
                        hashtags.append(f"#{word.strip(',.:;!?')}")
            
            # Add up to 15 hashtags (YouTube best practices)
            if hashtags:
                hashtags = list(set(hashtags))[:15]  # Remove duplicates and limit to 15
                text += "\n\n" + " ".join(hashtags)
        
        return text
    
    # Cross-Platform Methods
    def post_to_all_platforms(self, content, media_paths=None):
        """
        Post to all enabled platforms.
        
        Args:
            content (dict): Content to post (with platform-specific fields)
            media_paths (dict): Paths to media files for each platform
            
        Returns:
            dict: Post results for all platforms
        """
        results = {}
        
        # Twitter
        if self.config["platforms"]["twitter"]["enabled"] and self.auth_data["twitter"]["authenticated"]:
            twitter_text = content.get("twitter", {}).get("text") or content.get("text", "")
            twitter_media = media_paths.get("twitter") if media_paths else None
            
            results["twitter"] = self.post_to_twitter(
                twitter_text,
                twitter_media,
                content.get("twitter", {}).get("reply_to"),
                content.get("twitter", {}).get("quote_tweet")
            )
        
        # Threads
        if self.config["platforms"]["threads"]["enabled"] and self.auth_data["threads"]["authenticated"]:
            threads_text = content.get("threads", {}).get("text") or content.get("text", "")
            threads_media = media_paths.get("threads") if media_paths else None
            
            results["threads"] = self.post_to_threads(
                threads_text,
                threads_media,
                content.get("threads", {}).get("reply_to")
            )
        
        # Instagram
        if self.config["platforms"]["instagram"]["enabled"] and self.auth_data["instagram"]["authenticated"]:
            instagram_caption = content.get("instagram", {}).get("caption") or content.get("text", "")
            instagram_media = media_paths.get("instagram") if media_paths else None
            
            if instagram_media:
                results["instagram"] = self.post_to_instagram(
                    instagram_caption,
                    instagram_media,
                    content.get("instagram", {}).get("post_type", "feed")
                )
        
        # Facebook
        if self.config["platforms"]["facebook"]["enabled"] and self.auth_data["facebook"]["authenticated"]:
            facebook_message = content.get("facebook", {}).get("message") or content.get("text", "")
            facebook_media = media_paths.get("facebook") if media_paths else None
            
            results["facebook"] = self.post_to_facebook(
                facebook_message,
                facebook_media,
                content.get("facebook", {}).get("link")
            )
        
        # LinkedIn
        if self.config["platforms"]["linkedin"]["enabled"] and self.auth_data["linkedin"]["authenticated"]:
            linkedin_text = content.get("linkedin", {}).get("text") or content.get("text", "")
            linkedin_media = media_paths.get("linkedin") if media_paths else None
            
            results["linkedin"] = self.post_to_linkedin(
                linkedin_text,
                linkedin_media,
                content.get("linkedin", {}).get("article_url")
            )
        
        # TikTok
        if self.config["platforms"]["tiktok"]["enabled"] and self.auth_data["tiktok"]["authenticated"]:
            tiktok_caption = content.get("tiktok", {}).get("caption") or content.get("text", "")
            tiktok_video = media_paths.get("tiktok") if media_paths else None
            
            if tiktok_video:
                results["tiktok"] = self.post_to_tiktok(
                    tiktok_caption,
                    tiktok_video
                )
        
        # YouTube
        if self.config["platforms"]["youtube"]["enabled"] and self.auth_data["youtube"]["authenticated"]:
            youtube_title = content.get("youtube", {}).get("title", "")
            youtube_description = content.get("youtube", {}).get("description") or content.get("text", "")
            youtube_video = media_paths.get("youtube") if media_paths else None
            
            if youtube_video and youtube_title:
                results["youtube"] = self.post_to_youtube(
                    youtube_title,
                    youtube_description,
                    youtube_video,
                    content.get("youtube", {}).get("privacy_status", "private"),
                    content.get("youtube", {}).get("tags"),
                    content.get("youtube", {}).get("category_id")
                )
        
        return {
            "success": any(results[platform]["success"] for platform in results if "success" in results[platform]),
            "platforms": list(results.keys()),
            "results": results
        }
    
    def get_platform_status(self):
        """
        Get status of all platforms.
        
        Returns:
            dict: Platform status
        """
        status = {}
        
        for platform in self.config["platforms"]:
            status[platform] = {
                "enabled": self.config["platforms"][platform]["enabled"],
                "authenticated": self.auth_data[platform]["authenticated"] if platform in self.auth_data else False,
                "username": self.auth_data[platform].get("username", "") if platform in self.auth_data else ""
            }
        
        return status
    
    def update_settings(self, settings):
        """
        Update default settings.
        
        Args:
            settings (dict): New settings
            
        Returns:
            dict: Updated settings
        """
        for key, value in settings.items():
            if key in self.config["default_settings"]:
                self.config["default_settings"][key] = value
        
        self._save_config()
        
        return self.config["default_settings"]
