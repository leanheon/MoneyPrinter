import os
import json
from src.automated_posting_workflow import AutomatedPostingWorkflow
from src.expanded_sns_connector import ExpandedSNSConnector
from src.integrated_workflow import IntegratedWorkflow
from src.channel_manager import ChannelManager
from src.news_automation_system import NewsAutomationSystem
from src.constants import ROOT_DIR

class IntegratedSocialMediaSystem:
    """
    Integrated system that connects the automated posting workflow with all existing components
    of the MoneyPrinter system, providing a unified interface for content creation and distribution
    across multiple social media platforms.
    """
    def __init__(self):
        """
        Initialize the IntegratedSocialMediaSystem.
        """
        self.posting_workflow = AutomatedPostingWorkflow()
        self.sns_connector = ExpandedSNSConnector()
        self.integrated_workflow = IntegratedWorkflow()
        self.channel_manager = ChannelManager()
        self.news_automation = NewsAutomationSystem()
        
        self.output_dir = os.path.join(ROOT_DIR, ".mp", "integrated_social")
        self.config_file = os.path.join(self.output_dir, "integrated_config.json")
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Load configuration
        self.config = self._load_config()
    
    def _load_config(self):
        """
        Load integrated configuration from file.
        
        Returns:
            dict: Integrated configuration
        """
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading integrated config: {e}")
                
        # Default configuration if file doesn't exist or can't be loaded
        return {
            "enabled_platforms": {
                "twitter": True,
                "threads": True,
                "instagram": True,
                "facebook": True,
                "linkedin": True,
                "tiktok": True,
                "youtube": True
            },
            "content_distribution": {
                "auto_distribute": True,
                "platform_mapping": {
                    "shorts": ["twitter", "threads", "instagram", "tiktok", "youtube"],
                    "blog": ["twitter", "threads", "facebook", "linkedin"],
                    "news": ["twitter", "threads", "facebook", "linkedin"],
                    "images": ["instagram", "facebook"],
                    "videos": ["youtube", "facebook"]
                }
            },
            "workflow_integration": {
                "auto_schedule_new_content": True,
                "default_schedule_type": "daily",
                "default_time_of_day": "09:00",
                "default_days_of_week": [0, 2, 4]  # Monday, Wednesday, Friday
            }
        }
    
    def _save_config(self):
        """
        Save integrated configuration to file.
        """
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2)
                
        except Exception as e:
            print(f"Error saving integrated config: {e}")
    
    def configure_platform_integration(self, platform, enabled):
        """
        Configure platform integration.
        
        Args:
            platform (str): Platform name
            enabled (bool): Whether the platform is enabled
            
        Returns:
            dict: Updated platform integration configuration
        """
        if platform in self.config["enabled_platforms"]:
            self.config["enabled_platforms"][platform] = enabled
            self._save_config()
            
            # Also update the posting workflow configuration
            self.posting_workflow.configure_platform_preferences(platform, enabled=enabled)
        
        return self.config["enabled_platforms"]
    
    def configure_content_distribution(self, auto_distribute=None, platform_mapping=None):
        """
        Configure content distribution.
        
        Args:
            auto_distribute (bool): Whether to automatically distribute content
            platform_mapping (dict): Mapping of content types to platforms
            
        Returns:
            dict: Updated content distribution configuration
        """
        if auto_distribute is not None:
            self.config["content_distribution"]["auto_distribute"] = auto_distribute
        
        if platform_mapping is not None:
            self.config["content_distribution"]["platform_mapping"] = platform_mapping
        
        self._save_config()
        
        return self.config["content_distribution"]
    
    def configure_workflow_integration(self, auto_schedule=None, schedule_type=None, time_of_day=None, days_of_week=None):
        """
        Configure workflow integration.
        
        Args:
            auto_schedule (bool): Whether to automatically schedule new content
            schedule_type (str): Default schedule type
            time_of_day (str): Default time of day
            days_of_week (list): Default days of week
            
        Returns:
            dict: Updated workflow integration configuration
        """
        if auto_schedule is not None:
            self.config["workflow_integration"]["auto_schedule_new_content"] = auto_schedule
        
        if schedule_type is not None:
            self.config["workflow_integration"]["default_schedule_type"] = schedule_type
        
        if time_of_day is not None:
            self.config["workflow_integration"]["default_time_of_day"] = time_of_day
        
        if days_of_week is not None:
            self.config["workflow_integration"]["default_days_of_week"] = days_of_week
        
        self._save_config()
        
        return self.config["workflow_integration"]
    
    def setup_social_media_account(self, platform, credentials):
        """
        Set up a social media account.
        
        Args:
            platform (str): Platform name
            credentials (dict): Platform credentials
            
        Returns:
            bool: True if setup was successful
        """
        if platform == "twitter":
            return self.sns_connector.configure_twitter(
                api_key=credentials.get("api_key"),
                api_secret=credentials.get("api_secret"),
                access_token=credentials.get("access_token"),
                access_token_secret=credentials.get("access_token_secret"),
                bearer_token=credentials.get("bearer_token")
            )
            
        elif platform == "threads":
            return self.sns_connector.configure_threads(
                username=credentials.get("username"),
                password=credentials.get("password")
            )
            
        elif platform == "instagram":
            return self.sns_connector.configure_instagram(
                username=credentials.get("username"),
                password=credentials.get("password"),
                access_token=credentials.get("access_token")
            )
            
        elif platform == "facebook":
            return self.sns_connector.configure_facebook(
                app_id=credentials.get("app_id"),
                app_secret=credentials.get("app_secret"),
                access_token=credentials.get("access_token"),
                page_id=credentials.get("page_id")
            )
            
        elif platform == "linkedin":
            return self.sns_connector.configure_linkedin(
                client_id=credentials.get("client_id"),
                client_secret=credentials.get("client_secret"),
                access_token=credentials.get("access_token")
            )
            
        elif platform == "tiktok":
            return self.sns_connector.configure_tiktok(
                client_key=credentials.get("client_key"),
                client_secret=credentials.get("client_secret"),
                access_token=credentials.get("access_token")
            )
            
        elif platform == "youtube":
            return self.sns_connector.configure_youtube(
                client_id=credentials.get("client_id"),
                client_secret=credentials.get("client_secret"),
                api_key=credentials.get("api_key"),
                refresh_token=credentials.get("refresh_token"),
                access_token=credentials.get("access_token")
            )
            
        else:
            print(f"Unknown platform: {platform}")
            return False
    
    def create_content_and_post(self, content_type, topic=None, channel_id=None):
        """
        Create content and post it to social media.
        
        Args:
            content_type (str): Type of content to create (shorts, blog, news)
            topic (str): Topic for the content
            channel_id (str): Channel ID to use for content creation
            
        Returns:
            dict: Result of content creation and posting
        """
        # Create content
        content = self._create_content(content_type, topic, channel_id)
        
        if not content:
            return {"success": False, "message": f"Failed to create content of type: {content_type}"}
        
        # Determine platforms to post to
        platforms = self._get_platforms_for_content_type(content_type)
        
        # Post content
        if content_type == "shorts":
            # For shorts, we need to handle video upload
            result = self._post_shorts_to_platforms(content, platforms)
        else:
            # For other content types, use the posting workflow
            result = self.posting_workflow.post_content_now(
                content_source=f"channel:{channel_id}" if channel_id else content_type,
                platforms=platforms
            )
        
        # If auto-schedule is enabled, create a schedule for similar content
        if self.config["workflow_integration"]["auto_schedule_new_content"] and result["success"]:
            self._create_schedule_for_content_type(content_type, channel_id)
        
        return {
            "success": result["success"],
            "content_type": content_type,
            "platforms": platforms,
            "post_results": result["results"] if "results" in result else {},
            "content_id": content.get("id") if content else None
        }
    
    def _create_content(self, content_type, topic=None, channel_id=None):
        """
        Create content of a specific type.
        
        Args:
            content_type (str): Type of content to create
            topic (str): Topic for the content
            channel_id (str): Channel ID to use for content creation
            
        Returns:
            dict: Created content
        """
        if content_type == "shorts":
            if channel_id:
                # Create shorts from channel
                content = self.channel_manager.generate_channel_content(
                    channel_id=channel_id,
                    content_type="shorts",
                    topic=topic,
                    count=1
                )
                
                return content[0] if content and len(content) > 0 else None
            else:
                # Create shorts from topic
                # This is a placeholder - in a real implementation, this would create shorts from a topic
                return {
                    "id": f"shorts_{int(time.time())}",
                    "type": "shorts",
                    "title": f"Shorts about {topic}",
                    "video_path": "/path/to/video.mp4",  # This would be a real video path
                    "thumbnail_path": "/path/to/thumbnail.jpg"  # This would be a real thumbnail path
                }
                
        elif content_type == "blog":
            # Create blog post
            # This is a placeholder - in a real implementation, this would create a blog post
            return {
                "id": f"blog_{int(time.time())}",
                "type": "blog",
                "title": f"Blog post about {topic}",
                "text": f"This is a blog post about {topic}.",
                "image_path": "/path/to/image.jpg"  # This would be a real image path
            }
            
        elif content_type == "news":
            # Create news article
            articles = self.news_automation.crawl_news(
                max_articles=1,
                topic=topic
            )
            
            if not articles or len(articles) == 0:
                return None
            
            # Process article
            processed_content = self.news_automation.process_articles(
                article_ids=[articles[0]["id"]],
                platforms=["social"]
            )
            
            return processed_content[0] if processed_content and len(processed_content) > 0 else None
            
        else:
            print(f"Unknown content type: {content_type}")
            return None
    
    def _get_platforms_for_content_type(self, content_type):
        """
        Get platforms for a specific content type.
        
        Args:
            content_type (str): Content type
            
        Returns:
            list: Platforms to post to
        """
        # Get platforms from configuration
        platforms = self.config["content_distribution"]["platform_mapping"].get(content_type, [])
        
        # Filter by enabled platforms
        return [p for p in platforms if self.config["enabled_platforms"].get(p, False)]
    
    def _post_shorts_to_platforms(self, shorts_content, platforms):
        """
        Post shorts to platforms.
        
        Args:
            shorts_content (dict): Shorts content
            platforms (list): Platforms to post to
            
        Returns:
            dict: Post results
        """
        # Prepare content for each platform
        formatted_content = {}
        media_paths = {}
        
        for platform in platforms:
            if platform == "twitter":
                formatted_content["twitter"] = {
                    "text": f"{shorts_content.get('title', 'New Shorts')} #shorts #video"
                }
                media_paths["twitter"] = [shorts_content.get("video_path")]
                
            elif platform == "threads":
                formatted_content["threads"] = {
                    "text": f"{shorts_content.get('title', 'New Shorts')} #shorts #video"
                }
                media_paths["threads"] = [shorts_content.get("video_path")]
                
            elif platform == "instagram":
                formatted_content["instagram"] = {
                    "caption": f"{shorts_content.get('title', 'New Shorts')} #shorts #video",
                    "post_type": "reel"
                }
                media_paths["instagram"] = [shorts_content.get("video_path")]
                
            elif platform == "tiktok":
                formatted_content["tiktok"] = {
                    "caption": f"{shorts_content.get('title', 'New Shorts')} #shorts #video"
                }
                media_paths["tiktok"] = shorts_content.get("video_path")
                
            elif platform == "youtube":
                formatted_content["youtube"] = {
                    "title": shorts_content.get("title", "New Shorts"),
                    "description": f"{shorts_content.get('title', 'New Shorts')} #shorts #video"
                }
                media_paths["youtube"] = shorts_content.get("video_path")
        
        # Post to all platforms
        return self.sns_connector.post_to_all_platforms(formatted_content, media_paths)
    
    def _create_schedule_for_content_type(self, content_type, channel_id=None):
        """
        Create a schedule for a specific content type.
        
        Args:
            content_type (str): Content type
            channel_id (str): Channel ID
            
        Returns:
            dict: Created schedule
        """
        # Get platforms for this content type
        platforms = self._get_platforms_for_content_type(content_type)
        
        # Create schedule name
        schedule_name = f"Auto {content_type.capitalize()}"
        if channel_id:
            channel = self.channel_manager.get_channel(channel_id)
            if channel:
                schedule_name += f" - {channel['name']}"
        
        # Create content source
        content_source = f"channel:{channel_id}" if channel_id else content_type
        
        # Create schedule
        return self.posting_workflow.create_posting_schedule(
            name=schedule_name,
            content_source=content_source,
            platforms=platforms,
            schedule_type=self.config["workflow_integration"]["default_schedule_type"],
            time_of_day=self.config["workflow_integration"]["default_time_of_day"],
            days_of_week=self.config["workflow_integration"]["default_days_of_week"]
        )
    
    def run_integrated_workflow(self, workflow_id):
        """
        Run an integrated workflow that includes social media posting.
        
        Args:
            workflow_id (str): Workflow ID
            
        Returns:
            dict: Workflow run result
        """
        # Run the workflow
        workflow_result = self.integrated_workflow.run_workflow(workflow_id)
        
        if not workflow_result["success"]:
            return workflow_result
        
        # Get content generated by the workflow
        content = self._get_content_from_workflow_run(workflow_result["run_id"])
        
        if not content:
            return {
                "success": True,
                "workflow_id": workflow_id,
                "run_id": workflow_result["run_id"],
                "message": "Workflow completed successfully, but no content was generated for social media posting"
            }
        
        # Post content to social media
        posting_results = []
        
        for content_item in content:
            content_type = content_item.get("type")
            platforms = self._get_platforms_for_content_type(content_type)
            
            if content_type == "shorts":
                result = self._post_shorts_to_platforms(content_item, platforms)
            else:
                result = self.posting_workflow.post_content_now(
                    content_source=content_item.get("source", "workflow"),
                    platforms=platforms
                )
            
            posting_results.append({
                "content_id": content_item.get("id"),
                "content_type": content_type,
                "platforms": platforms,
                "result": result
            })
        
        return {
            "success": True,
            "workflow_id": workflow_id,
            "run_id": workflow_result["run_id"],
            "workflow_result": workflow_result,
            "posting_results": posting_results
        }
    
    def _get_content_from_workflow_run(self, run_id):
        """
        Get content generated by a workflow run.
        
        Args:
            run_id (str): Run ID
            
        Returns:
            list: Content items
        """
        # This is a placeholder - in a real implementation, this would get content from the workflow run
        # For now, we'll return a simulated content item
        return [
            {
                "id": f"content_{int(time.time())}",
                "type": "shorts",
                "title": "Workflow Generated Shorts",
                "video_path": "/path/to/video.mp4",  # This would be a real video path
                "thumbnail_path": "/path/to/thumbnail.jpg",  # This would be a real thumbnail path
                "source": "workflow"
            }
        ]
    
    def create_complete_social_media_pipeline(self, name, channel_config=None, content_types=None, platforms=None, schedule_config=None):
        """
        Create a complete social media pipeline.
        
        Args:
            name (str): Pipeline name
            channel_config (dict): Channel configuration
            content_types (list): Content types to generate
            platforms (list): Platforms to post to
            schedule_config (dict): Schedule configuration
            
        Returns:
            dict: Created pipeline
        """
        # Create channel if configuration is provided
        channel_id = None
        if channel_config:
            channel = self.channel_manager.create_channel(
                name=channel_config.get("name", name),
                theme=channel_config.get("theme", "General"),
                personality=channel_config.get("personality", "Informative"),
                target_audience=channel_config.get("target_audience"),
                content_types=content_types or ["shorts", "social", "blog"]
            )
            channel_id = channel["id"]
        
        # Create schedules for each content type
        schedules = []
        for content_type in content_types or ["shorts", "social", "blog"]:
            # Get platforms for this content type
            content_platforms = platforms or self._get_platforms_for_content_type(content_type)
            
            # Create schedule
            schedule = self.posting_workflow.create_posting_schedule(
                name=f"{name} - {content_type.capitalize()}",
                content_source=f"channel:{channel_id}" if channel_id else content_type,
                platforms=content_platforms,
                schedule_type=schedule_config.get("type", self.config["workflow_integration"]["default_schedule_type"]),
                time_of_day=schedule_config.get("time_of_day", self.config["workflow_integration"]["default_time_of_day"]),
                days_of_week=schedule_config.get("days_of_week", self.config["workflow_integration"]["default_days_of_week"])
            )
            
            schedules.append(schedule)
        
        # Create integrated workflow
        workflow = self.integrated_workflow.create_workflow(
            name=f"{name} Pipeline",
            description=f"Social media pipeline for {name}",
            steps=[
                {
                    "id": "step_1",
                    "name": "Generate Content",
                    "type": "channel_generate" if channel_id else "news_crawl",
                    "params": {
                        "channel_id": channel_id,
                        "content_type": "shorts",
                        "count": 1
                    } if channel_id else {
                        "max_articles": 5,
                        "hours_back": 24
                    }
                },
                {
                    "id": "step_2",
                    "name": "Process Content",
                    "type": "channel_process" if channel_id else "news_process",
                    "params": {
                        "channel_id": channel_id,
                        "platforms": platforms or ["twitter", "instagram", "youtube"]
                    } if channel_id else {
                        "platforms": ["blog", "social"]
                    }
                },
                {
                    "id": "step_3",
                    "name": "Publish Content",
                    "type": "publish_all",
                    "params": {}
                }
            ]
        )
        
        # Schedule the workflow
        workflow_schedule = self.integrated_workflow.schedule_workflow(
            workflow["id"],
            schedule_config.get("interval_hours", 24)
        )
        
        return {
            "name": name,
            "channel": {"id": channel_id} if channel_id else None,
            "content_types": content_types or ["shorts", "social", "blog"],
            "platforms": platforms or self._get_enabled_platforms(),
            "schedules": schedules,
            "workflow": workflow,
            "workflow_schedule": workflow_schedule
        }
    
    def _get_enabled_platforms(self):
        """
        Get all enabled platforms.
        
        Returns:
            list: Enabled platforms
        """
        return [p for p, enabled in self.config["enabled_platforms"].items() if enabled]
    
    def get_social_media_status(self):
        """
        Get status of all social media platforms.
        
        Returns:
            dict: Platform status
        """
        return self.sns_connector.get_platform_status()
    
    def get_recent_posts(self, limit=10):
        """
        Get recent social media posts.
        
        Args:
            limit (int): Maximum number of posts to return
            
        Returns:
            list: Recent posts
        """
        return self.posting_workflow.get_recent_posts(limit)
    
    def get_posting_schedules(self):
        """
        Get all posting schedules.
        
        Returns:
            dict: All posting schedules
        """
        return self.posting_workflow.get_posting_schedules()
    
    def get_posting_stats(self):
        """
        Get posting statistics.
        
        Returns:
            dict: Posting statistics
        """
        return self.posting_workflow.get_stats()
    
    def start_all_services(self):
        """
        Start all services.
        
        Returns:
            dict: Service status
        """
        posting_started = self.posting_workflow.start_scheduler()
        workflow_started = self.integrated_workflow.start_all_services()
        
        return {
            "posting_scheduler_started": posting_started,
            "workflow_services_started": workflow_started["status"] == "running",
            "status": "running" if posting_started and workflow_started["status"] == "running" else "partial"
        }
    
    def stop_all_services(self):
        """
        Stop all services.
        
        Returns:
            dict: Service status
        """
        posting_stopped = self.posting_workflow.stop_scheduler()
        workflow_stopped = self.integrated_workflow.stop_all_services()
        
        return {
            "posting_scheduler_stopped": posting_stopped,
            "workflow_services_stopped": workflow_stopped["status"] == "stopped",
            "status": "stopped" if posting_stopped and workflow_stopped["status"] == "stopped" else "partial"
        }
