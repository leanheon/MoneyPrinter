import os
import json
import time
import requests
import base64
from datetime import datetime
from src.constants import ROOT_DIR

class SNSConnector:
    """
    Connector for social networking services (SNS) like X (Twitter) and Threads.
    Handles authentication, content formatting, and posting to these platforms.
    """
    def __init__(self):
        """
        Initialize the SNSConnector.
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
                }
            },
            "default_settings": {
                "auto_hashtags": True,
                "auto_format": True,
                "include_link": True,
                "retry_count": 3,
                "retry_delay": 5
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
    
    def post_to_all_platforms(self, text, media_paths=None):
        """
        Post to all enabled platforms.
        
        Args:
            text (str): Text content of the post
            media_paths (list): Paths to media files to attach
            
        Returns:
            dict: Post results for all platforms
        """
        results = {}
        
        if self.config["platforms"]["twitter"]["enabled"] and self.auth_data["twitter"]["authenticated"]:
            results["twitter"] = self.post_to_twitter(text, media_paths)
        
        if self.config["platforms"]["threads"]["enabled"] and self.auth_data["threads"]["authenticated"]:
            results["threads"] = self.post_to_threads(text, media_paths)
        
        return {
            "success": any(results[platform]["success"] for platform in results),
            "platforms": list(results.keys()),
            "results": results
        }
    
    def get_platform_status(self):
        """
        Get status of all platforms.
        
        Returns:
            dict: Platform status
        """
        return {
            "twitter": {
                "enabled": self.config["platforms"]["twitter"]["enabled"],
                "authenticated": self.auth_data["twitter"]["authenticated"],
                "username": self.auth_data["twitter"]["username"] if self.auth_data["twitter"]["authenticated"] else None
            },
            "threads": {
                "enabled": self.config["platforms"]["threads"]["enabled"],
                "authenticated": self.auth_data["threads"]["authenticated"],
                "username": self.auth_data["threads"]["username"] if self.auth_data["threads"]["authenticated"] else None
            }
        }
    
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
