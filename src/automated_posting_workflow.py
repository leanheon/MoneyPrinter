import os
import json
import time
from datetime import datetime
from src.expanded_sns_connector import ExpandedSNSConnector
from src.channel_manager import ChannelManager
from src.news_automation_system import NewsAutomationSystem
from src.constants import ROOT_DIR

class AutomatedPostingWorkflow:
    """
    Automated posting workflow that integrates the expanded SNS connector with the content generation system.
    Handles scheduling, content formatting, and posting to multiple social media platforms.
    """
    def __init__(self):
        """
        Initialize the AutomatedPostingWorkflow.
        """
        self.sns_connector = ExpandedSNSConnector()
        self.channel_manager = ChannelManager()
        self.news_automation = NewsAutomationSystem()
        
        self.output_dir = os.path.join(ROOT_DIR, ".mp", "automated_posting")
        self.config_file = os.path.join(self.output_dir, "posting_config.json")
        self.data_file = os.path.join(self.output_dir, "posting_data.json")
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Load configuration and data
        self.config = self._load_config()
        self.data = self._load_data()
    
    def _load_config(self):
        """
        Load posting configuration from file.
        
        Returns:
            dict: Posting configuration
        """
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading posting config: {e}")
                
        # Default configuration if file doesn't exist or can't be loaded
        return {
            "posting_schedules": {},
            "platform_preferences": {
                "twitter": {
                    "enabled": True,
                    "content_types": ["shorts", "news", "blog"],
                    "posting_frequency": "high"
                },
                "threads": {
                    "enabled": True,
                    "content_types": ["shorts", "news", "blog"],
                    "posting_frequency": "medium"
                },
                "instagram": {
                    "enabled": True,
                    "content_types": ["shorts", "images"],
                    "posting_frequency": "medium"
                },
                "facebook": {
                    "enabled": True,
                    "content_types": ["shorts", "news", "blog"],
                    "posting_frequency": "medium"
                },
                "linkedin": {
                    "enabled": True,
                    "content_types": ["blog", "news"],
                    "posting_frequency": "low"
                },
                "tiktok": {
                    "enabled": True,
                    "content_types": ["shorts"],
                    "posting_frequency": "high"
                },
                "youtube": {
                    "enabled": True,
                    "content_types": ["shorts", "videos"],
                    "posting_frequency": "low"
                }
            },
            "content_formatting": {
                "auto_hashtags": True,
                "auto_format": True,
                "include_link": True,
                "cross_posting": True
            },
            "last_updated": datetime.now().isoformat()
        }
    
    def _load_data(self):
        """
        Load posting data from file.
        
        Returns:
            dict: Posting data
        """
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading posting data: {e}")
                
        # Default data if file doesn't exist or can't be loaded
        return {
            "posts": [],
            "schedules": [],
            "stats": {
                "total_posts": 0,
                "successful_posts": 0,
                "failed_posts": 0,
                "posts_by_platform": {}
            },
            "last_updated": datetime.now().isoformat()
        }
    
    def _save_config(self):
        """
        Save posting configuration to file.
        """
        try:
            self.config["last_updated"] = datetime.now().isoformat()
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2)
                
        except Exception as e:
            print(f"Error saving posting config: {e}")
    
    def _save_data(self):
        """
        Save posting data to file.
        """
        try:
            self.data["last_updated"] = datetime.now().isoformat()
            
            # Update stats
            self.data["stats"]["total_posts"] = len(self.data["posts"])
            self.data["stats"]["successful_posts"] = len([p for p in self.data["posts"] if p.get("success", False)])
            self.data["stats"]["failed_posts"] = len([p for p in self.data["posts"] if not p.get("success", False)])
            
            # Update platform stats
            platform_stats = {}
            for post in self.data["posts"]:
                for platform in post.get("platforms", []):
                    if platform not in platform_stats:
                        platform_stats[platform] = 0
                    platform_stats[platform] += 1
            
            self.data["stats"]["posts_by_platform"] = platform_stats
            
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, indent=2)
                
        except Exception as e:
            print(f"Error saving posting data: {e}")
    
    def configure_platform_preferences(self, platform, enabled=None, content_types=None, posting_frequency=None):
        """
        Configure platform preferences.
        
        Args:
            platform (str): Platform name
            enabled (bool): Whether the platform is enabled
            content_types (list): Content types to post to this platform
            posting_frequency (str): Posting frequency (high, medium, low)
            
        Returns:
            dict: Updated platform preferences
        """
        if platform not in self.config["platform_preferences"]:
            self.config["platform_preferences"][platform] = {
                "enabled": True,
                "content_types": ["shorts", "news", "blog"],
                "posting_frequency": "medium"
            }
        
        if enabled is not None:
            self.config["platform_preferences"][platform]["enabled"] = enabled
        
        if content_types is not None:
            self.config["platform_preferences"][platform]["content_types"] = content_types
        
        if posting_frequency is not None:
            self.config["platform_preferences"][platform]["posting_frequency"] = posting_frequency
        
        self._save_config()
        
        return self.config["platform_preferences"][platform]
    
    def configure_content_formatting(self, auto_hashtags=None, auto_format=None, include_link=None, cross_posting=None):
        """
        Configure content formatting preferences.
        
        Args:
            auto_hashtags (bool): Whether to automatically add hashtags
            auto_format (bool): Whether to automatically format content
            include_link (bool): Whether to include links in posts
            cross_posting (bool): Whether to cross-post content to multiple platforms
            
        Returns:
            dict: Updated content formatting preferences
        """
        if auto_hashtags is not None:
            self.config["content_formatting"]["auto_hashtags"] = auto_hashtags
        
        if auto_format is not None:
            self.config["content_formatting"]["auto_format"] = auto_format
        
        if include_link is not None:
            self.config["content_formatting"]["include_link"] = include_link
        
        if cross_posting is not None:
            self.config["content_formatting"]["cross_posting"] = cross_posting
        
        self._save_config()
        
        # Update SNS connector settings
        self.sns_connector.update_settings({
            "auto_hashtags": self.config["content_formatting"]["auto_hashtags"],
            "auto_format": self.config["content_formatting"]["auto_format"],
            "include_link": self.config["content_formatting"]["include_link"],
            "cross_posting": self.config["content_formatting"]["cross_posting"]
        })
        
        return self.config["content_formatting"]
    
    def create_posting_schedule(self, name, content_source, platforms, schedule_type="daily", time_of_day=None, days_of_week=None):
        """
        Create a posting schedule.
        
        Args:
            name (str): Schedule name
            content_source (str): Content source (channel, news, blog)
            platforms (list): Platforms to post to
            schedule_type (str): Schedule type (daily, weekly, monthly)
            time_of_day (str): Time of day to post (HH:MM)
            days_of_week (list): Days of week to post (0-6, where 0 is Monday)
            
        Returns:
            dict: Created schedule
        """
        schedule_id = f"schedule_{int(time.time())}"
        
        schedule = {
            "id": schedule_id,
            "name": name,
            "content_source": content_source,
            "platforms": platforms,
            "schedule_type": schedule_type,
            "time_of_day": time_of_day or "09:00",
            "days_of_week": days_of_week or [0, 2, 4],  # Monday, Wednesday, Friday
            "enabled": True,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "last_run": None,
            "next_run": self._calculate_next_run(schedule_type, time_of_day or "09:00", days_of_week or [0, 2, 4])
        }
        
        self.config["posting_schedules"][schedule_id] = schedule
        self._save_config()
        
        return schedule
    
    def _calculate_next_run(self, schedule_type, time_of_day, days_of_week):
        """
        Calculate the next run time for a schedule.
        
        Args:
            schedule_type (str): Schedule type (daily, weekly, monthly)
            time_of_day (str): Time of day to post (HH:MM)
            days_of_week (list): Days of week to post (0-6, where 0 is Monday)
            
        Returns:
            str: Next run time (ISO format)
        """
        from datetime import datetime, timedelta
        
        now = datetime.now()
        hour, minute = map(int, time_of_day.split(':'))
        
        if schedule_type == "daily":
            # If the time has already passed today, schedule for tomorrow
            target_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
            if target_time <= now:
                target_time += timedelta(days=1)
            
        elif schedule_type == "weekly":
            # Find the next day of week that matches
            current_day = now.weekday()  # 0-6, where 0 is Monday
            days_until_next = None
            
            for day in sorted(days_of_week):
                if day > current_day:
                    days_until_next = day - current_day
                    break
            
            if days_until_next is None:
                # No days left this week, schedule for the first day next week
                days_until_next = 7 - current_day + days_of_week[0]
            
            target_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0) + timedelta(days=days_until_next)
            
        elif schedule_type == "monthly":
            # Schedule for the same day next month
            if now.month == 12:
                target_time = now.replace(year=now.year + 1, month=1, day=1, hour=hour, minute=minute, second=0, microsecond=0)
            else:
                target_time = now.replace(month=now.month + 1, day=1, hour=hour, minute=minute, second=0, microsecond=0)
        
        return target_time.isoformat()
    
    def update_posting_schedule(self, schedule_id, **kwargs):
        """
        Update a posting schedule.
        
        Args:
            schedule_id (str): Schedule ID
            **kwargs: Fields to update
            
        Returns:
            dict: Updated schedule or None if not found
        """
        if schedule_id not in self.config["posting_schedules"]:
            return None
        
        schedule = self.config["posting_schedules"][schedule_id]
        
        # Update fields
        for key, value in kwargs.items():
            if key in schedule:
                schedule[key] = value
        
        schedule["updated_at"] = datetime.now().isoformat()
        
        # Recalculate next run if relevant fields were updated
        if any(key in kwargs for key in ["schedule_type", "time_of_day", "days_of_week"]):
            schedule["next_run"] = self._calculate_next_run(
                schedule["schedule_type"],
                schedule["time_of_day"],
                schedule["days_of_week"]
            )
        
        self.config["posting_schedules"][schedule_id] = schedule
        self._save_config()
        
        return schedule
    
    def delete_posting_schedule(self, schedule_id):
        """
        Delete a posting schedule.
        
        Args:
            schedule_id (str): Schedule ID
            
        Returns:
            bool: True if deleted, False if not found
        """
        if schedule_id not in self.config["posting_schedules"]:
            return False
        
        del self.config["posting_schedules"][schedule_id]
        self._save_config()
        
        return True
    
    def get_posting_schedules(self):
        """
        Get all posting schedules.
        
        Returns:
            dict: All posting schedules
        """
        return self.config["posting_schedules"]
    
    def get_posting_schedule(self, schedule_id):
        """
        Get a specific posting schedule.
        
        Args:
            schedule_id (str): Schedule ID
            
        Returns:
            dict: Posting schedule or None if not found
        """
        return self.config["posting_schedules"].get(schedule_id)
    
    def run_posting_schedule(self, schedule_id):
        """
        Run a specific posting schedule.
        
        Args:
            schedule_id (str): Schedule ID
            
        Returns:
            dict: Run result
        """
        schedule = self.get_posting_schedule(schedule_id)
        
        if not schedule:
            return {"success": False, "message": f"Schedule not found: {schedule_id}"}
        
        if not schedule["enabled"]:
            return {"success": False, "message": f"Schedule is disabled: {schedule_id}"}
        
        # Get content based on the content source
        content = self._get_content_from_source(schedule["content_source"])
        
        if not content:
            return {"success": False, "message": f"No content available from source: {schedule['content_source']}"}
        
        # Post content to platforms
        post_results = self._post_content_to_platforms(content, schedule["platforms"])
        
        # Update schedule
        schedule["last_run"] = datetime.now().isoformat()
        schedule["next_run"] = self._calculate_next_run(
            schedule["schedule_type"],
            schedule["time_of_day"],
            schedule["days_of_week"]
        )
        
        self.config["posting_schedules"][schedule_id] = schedule
        self._save_config()
        
        # Save post data
        post_data = {
            "id": f"post_{int(time.time())}",
            "schedule_id": schedule_id,
            "content_source": schedule["content_source"],
            "platforms": schedule["platforms"],
            "success": any(post_results["results"][platform]["success"] for platform in post_results["results"]),
            "timestamp": datetime.now().isoformat(),
            "results": post_results["results"]
        }
        
        self.data["posts"].append(post_data)
        self._save_data()
        
        return {
            "success": post_data["success"],
            "schedule_id": schedule_id,
            "post_id": post_data["id"],
            "platforms": schedule["platforms"],
            "results": post_results["results"]
        }
    
    def _get_content_from_source(self, content_source):
        """
        Get content from a specific source.
        
        Args:
            content_source (str): Content source (channel, news, blog)
            
        Returns:
            dict: Content data
        """
        if content_source.startswith("channel:"):
            # Get content from a specific channel
            channel_id = content_source.split(":")[1]
            return self._get_content_from_channel(channel_id)
            
        elif content_source == "news":
            # Get content from news automation
            return self._get_content_from_news()
            
        elif content_source == "blog":
            # Get content from blog generator
            return self._get_content_from_blog()
            
        else:
            print(f"Unknown content source: {content_source}")
            return None
    
    def _get_content_from_channel(self, channel_id):
        """
        Get content from a specific channel.
        
        Args:
            channel_id (str): Channel ID
            
        Returns:
            dict: Content data
        """
        # Get channel content
        content = self.channel_manager.generate_channel_content(
            channel_id=channel_id,
            content_type="social",
            count=1
        )
        
        if not content or len(content) == 0:
            return None
        
        # Format content for posting
        content_item = content[0]
        
        return {
            "text": content_item["text"],
            "title": content_item.get("title", ""),
            "media_paths": content_item.get("media_paths", []),
            "source": "channel",
            "channel_id": channel_id,
            "content_id": content_item["id"]
        }
    
    def _get_content_from_news(self):
        """
        Get content from news automation.
        
        Returns:
            dict: Content data
        """
        # Get news content
        articles = self.news_automation.crawl_news(max_articles=1)
        
        if not articles or len(articles) == 0:
            return None
        
        # Process article
        processed_content = self.news_automation.process_articles(
            article_ids=[articles[0]["id"]],
            platforms=["social"]
        )
        
        if not processed_content or len(processed_content) == 0:
            return None
        
        # Format content for posting
        content_item = processed_content[0]
        
        return {
            "text": content_item["text"],
            "title": content_item.get("title", ""),
            "media_paths": content_item.get("media_paths", []),
            "source": "news",
            "article_id": articles[0]["id"],
            "content_id": content_item["id"]
        }
    
    def _get_content_from_blog(self):
        """
        Get content from blog generator.
        
        Returns:
            dict: Content data
        """
        # This is a placeholder - in a real implementation, this would get content from the blog generator
        # For now, we'll return a simulated blog post
        return {
            "text": "Check out our latest blog post on the future of AI technology!",
            "title": "The Future of AI Technology",
            "media_paths": [],
            "source": "blog",
            "blog_id": f"blog_{int(time.time())}",
            "content_id": f"content_{int(time.time())}"
        }
    
    def _post_content_to_platforms(self, content, platforms):
        """
        Post content to multiple platforms.
        
        Args:
            content (dict): Content data
            platforms (list): Platforms to post to
            
        Returns:
            dict: Post results
        """
        # Format content for each platform
        formatted_content = {}
        media_paths = {}
        
        for platform in platforms:
            if platform == "twitter":
                formatted_content["twitter"] = {
                    "text": self._format_content_for_platform(content, "twitter")
                }
                media_paths["twitter"] = content.get("media_paths", [])
                
            elif platform == "threads":
                formatted_content["threads"] = {
                    "text": self._format_content_for_platform(content, "threads")
                }
                media_paths["threads"] = content.get("media_paths", [])
                
            elif platform == "instagram":
                formatted_content["instagram"] = {
                    "caption": self._format_content_for_platform(content, "instagram"),
                    "post_type": "feed"
                }
                media_paths["instagram"] = content.get("media_paths", [])
                
            elif platform == "facebook":
                formatted_content["facebook"] = {
                    "message": self._format_content_for_platform(content, "facebook")
                }
                media_paths["facebook"] = content.get("media_paths", [])
                
            elif platform == "linkedin":
                formatted_content["linkedin"] = {
                    "text": self._format_content_for_platform(content, "linkedin")
                }
                media_paths["linkedin"] = content.get("media_paths", [])
                
            elif platform == "tiktok":
                formatted_content["tiktok"] = {
                    "caption": self._format_content_for_platform(content, "tiktok")
                }
                # TikTok requires a video
                if content.get("media_paths") and any(path.endswith((".mp4", ".mov")) for path in content.get("media_paths", [])):
                    video_paths = [path for path in content.get("media_paths", []) if path.endswith((".mp4", ".mov"))]
                    media_paths["tiktok"] = video_paths[0] if video_paths else None
                
            elif platform == "youtube":
                formatted_content["youtube"] = {
                    "title": content.get("title", "New Video"),
                    "description": self._format_content_for_platform(content, "youtube")
                }
                # YouTube requires a video
                if content.get("media_paths") and any(path.endswith((".mp4", ".mov")) for path in content.get("media_paths", [])):
                    video_paths = [path for path in content.get("media_paths", []) if path.endswith((".mp4", ".mov"))]
                    media_paths["youtube"] = video_paths[0] if video_paths else None
        
        # Post to all platforms
        return self.sns_connector.post_to_all_platforms(formatted_content, media_paths)
    
    def _format_content_for_platform(self, content, platform):
        """
        Format content for a specific platform.
        
        Args:
            content (dict): Content data
            platform (str): Platform name
            
        Returns:
            str: Formatted content
        """
        text = content.get("text", "")
        
        # Add title if available and appropriate for the platform
        if content.get("title") and platform in ["linkedin", "facebook", "youtube"]:
            text = f"{content['title']}\n\n{text}"
        
        # Add link if available and enabled
        if content.get("link") and self.config["content_formatting"]["include_link"]:
            text += f"\n\n{content['link']}"
        
        # Platform-specific formatting will be handled by the SNS connector
        return text
    
    def check_due_schedules(self):
        """
        Check for schedules that are due to run.
        
        Returns:
            list: Results of run schedules
        """
        now = datetime.now()
        results = []
        
        for schedule_id, schedule in self.config["posting_schedules"].items():
            if not schedule["enabled"]:
                continue
            
            next_run = datetime.fromisoformat(schedule["next_run"])
            
            if next_run <= now:
                # Schedule is due to run
                result = self.run_posting_schedule(schedule_id)
                results.append(result)
        
        return results
    
    def post_content_now(self, content_source, platforms):
        """
        Post content immediately.
        
        Args:
            content_source (str): Content source (channel, news, blog)
            platforms (list): Platforms to post to
            
        Returns:
            dict: Post result
        """
        # Get content
        content = self._get_content_from_source(content_source)
        
        if not content:
            return {"success": False, "message": f"No content available from source: {content_source}"}
        
        # Post content
        post_results = self._post_content_to_platforms(content, platforms)
        
        # Save post data
        post_data = {
            "id": f"post_{int(time.time())}",
            "schedule_id": None,
            "content_source": content_source,
            "platforms": platforms,
            "success": any(post_results["results"][platform]["success"] for platform in post_results["results"]),
            "timestamp": datetime.now().isoformat(),
            "results": post_results["results"]
        }
        
        self.data["posts"].append(post_data)
        self._save_data()
        
        return {
            "success": post_data["success"],
            "post_id": post_data["id"],
            "platforms": platforms,
            "results": post_results["results"]
        }
    
    def get_recent_posts(self, limit=10):
        """
        Get recent posts.
        
        Args:
            limit (int): Maximum number of posts to return
            
        Returns:
            list: Recent posts
        """
        # Sort posts by timestamp (newest first)
        sorted_posts = sorted(
            self.data["posts"],
            key=lambda p: p["timestamp"],
            reverse=True
        )
        
        return sorted_posts[:limit]
    
    def get_post(self, post_id):
        """
        Get a specific post.
        
        Args:
            post_id (str): Post ID
            
        Returns:
            dict: Post data or None if not found
        """
        for post in self.data["posts"]:
            if post["id"] == post_id:
                return post
                
        return None
    
    def get_stats(self):
        """
        Get posting statistics.
        
        Returns:
            dict: Posting statistics
        """
        return self.data["stats"]
    
    def start_scheduler(self):
        """
        Start the posting scheduler.
        
        Returns:
            bool: True if started successfully
        """
        # This is a placeholder - in a real implementation, this would start a background scheduler
        # For now, we'll just return True
        return True
    
    def stop_scheduler(self):
        """
        Stop the posting scheduler.
        
        Returns:
            bool: True if stopped successfully
        """
        # This is a placeholder - in a real implementation, this would stop the background scheduler
        # For now, we'll just return True
        return True
