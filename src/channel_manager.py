import os
import json
import random
import time
from datetime import datetime, timedelta
from src.openai_generator import OpenAIGenerator
from src.enhanced_shorts import EnhancedShorts
from src.news_automation_system import NewsAutomationSystem
from src.constants import ROOT_DIR

class ChannelManager:
    """
    System for managing multiple themed channels, each with its own personality and content focus.
    Automatically generates and elevates shorts content based on the thematic personality of each channel.
    """
    def __init__(self, dropbox_token=None):
        """
        Initialize the ChannelManager.
        
        Args:
            dropbox_token (str): Optional Dropbox access token for uploading videos
        """
        self.openai_generator = OpenAIGenerator()
        self.enhanced_shorts = EnhancedShorts(dropbox_token)
        self.news_automation = NewsAutomationSystem()
        
        self.output_dir = os.path.join(ROOT_DIR, ".mp", "channel_manager")
        self.data_file = os.path.join(self.output_dir, "channels_data.json")
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Load existing data if available
        self.channels_data = self._load_data()
        
    def _load_data(self):
        """
        Load channels data from file.
        
        Returns:
            dict: Channels data
        """
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading channels data: {e}")
                
        # Default structure if file doesn't exist or can't be loaded
        return {
            "channels": [],
            "content": [],
            "stats": {
                "total_channels": 0,
                "total_content": 0,
                "content_by_type": {}
            },
            "last_updated": datetime.now().isoformat()
        }
    
    def _save_data(self):
        """
        Save channels data to file.
        """
        try:
            self.channels_data["last_updated"] = datetime.now().isoformat()
            self.channels_data["stats"]["total_channels"] = len(self.channels_data["channels"])
            self.channels_data["stats"]["total_content"] = len(self.channels_data["content"])
            
            # Update content by type stats
            content_by_type = {}
            for content in self.channels_data["content"]:
                content_type = content.get("content_type", "unknown")
                if content_type in content_by_type:
                    content_by_type[content_type] += 1
                else:
                    content_by_type[content_type] = 1
            
            self.channels_data["stats"]["content_by_type"] = content_by_type
            
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.channels_data, f, indent=2)
                
        except Exception as e:
            print(f"Error saving channels data: {e}")
    
    def create_channel(self, name, theme, personality, target_audience=None, content_types=None, posting_frequency=None):
        """
        Create a new themed channel.
        
        Args:
            name (str): Name of the channel
            theme (str): Theme of the channel (e.g., tech, fashion, gaming)
            personality (str): Personality of the channel (e.g., informative, humorous, inspirational)
            target_audience (str): Target audience of the channel
            content_types (list): Types of content to create (shorts, posts, blogs)
            posting_frequency (dict): Frequency of posting for each content type
            
        Returns:
            dict: Created channel data
        """
        # Generate a unique channel ID
        channel_id = f"channel_{len(self.channels_data['channels']) + 1}"
        
        # Set default values if not provided
        if not target_audience:
            target_audience = self._generate_target_audience(theme, personality)
            
        if not content_types:
            content_types = ["shorts", "social"]
            
        if not posting_frequency:
            posting_frequency = {
                "shorts": "daily",
                "social": "daily",
                "blog": "weekly"
            }
        
        # Generate channel description and content strategy
        channel_details = self._generate_channel_details(name, theme, personality, target_audience)
        
        channel = {
            "id": channel_id,
            "name": name,
            "theme": theme,
            "personality": personality,
            "target_audience": target_audience,
            "content_types": content_types,
            "posting_frequency": posting_frequency,
            "description": channel_details.get("description", ""),
            "content_strategy": channel_details.get("content_strategy", ""),
            "visual_style": channel_details.get("visual_style", ""),
            "keywords": channel_details.get("keywords", []),
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "stats": {
                "content_count": 0,
                "views": 0,
                "likes": 0,
                "comments": 0,
                "shares": 0
            }
        }
        
        self.channels_data["channels"].append(channel)
        self._save_data()
        
        return channel
    
    def _generate_target_audience(self, theme, personality):
        """
        Generate a target audience description based on theme and personality.
        
        Args:
            theme (str): Theme of the channel
            personality (str): Personality of the channel
            
        Returns:
            str: Target audience description
        """
        system_message = "You are a social media strategist who specializes in audience targeting."
        
        prompt = f"""
        Generate a concise target audience description for a content channel with the following characteristics:
        
        Theme: {theme}
        Personality: {personality}
        
        The target audience description should include:
        - Age range
        - Interests
        - Behavioral characteristics
        
        Keep the description under 100 words and focus on the most relevant audience for this theme and personality.
        """
        
        target_audience = self.openai_generator.generate_content(prompt, system_message, max_tokens=150)
        return target_audience.strip() if target_audience else f"People interested in {theme}"
    
    def _generate_channel_details(self, name, theme, personality, target_audience):
        """
        Generate detailed channel information.
        
        Args:
            name (str): Name of the channel
            theme (str): Theme of the channel
            personality (str): Personality of the channel
            target_audience (str): Target audience of the channel
            
        Returns:
            dict: Channel details including description, content strategy, visual style, and keywords
        """
        system_message = "You are a content strategy expert who helps creators develop cohesive channel identities."
        
        prompt = f"""
        Create a detailed channel strategy for a content creator with the following parameters:
        
        Channel Name: {name}
        Theme: {theme}
        Personality: {personality}
        Target Audience: {target_audience}
        
        Please provide:
        1. A channel description (100-150 words)
        2. A content strategy outlining the types of content that would work well (100-150 words)
        3. A visual style guide with color palette and aesthetic recommendations (50-100 words)
        4. A list of 10-15 relevant keywords for the channel
        
        Format your response as a JSON object with the following keys: description, content_strategy, visual_style, and keywords (as an array).
        """
        
        response = self.openai_generator.generate_structured_content(
            prompt, 
            system_message,
            output_structure={
                "description": "Channel description text",
                "content_strategy": "Content strategy text",
                "visual_style": "Visual style guide text",
                "keywords": ["keyword1", "keyword2", "etc"]
            }
        )
        
        if not response:
            # Fallback if structured generation fails
            return {
                "description": f"A {personality} channel about {theme} for {target_audience}.",
                "content_strategy": f"Create {personality} content about {theme} topics.",
                "visual_style": "Clean, modern aesthetic with consistent branding.",
                "keywords": [theme, personality, "content", "channel", "social media"]
            }
            
        return response
    
    def generate_content_for_channel(self, channel_id, content_type="shorts", topic=None):
        """
        Generate content for a specific channel based on its theme and personality.
        
        Args:
            channel_id (str): ID of the channel
            content_type (str): Type of content to generate (shorts, social, blog)
            topic (str): Optional specific topic to create content about
            
        Returns:
            dict: Generated content data
        """
        # Find the channel
        channel = None
        for ch in self.channels_data["channels"]:
            if ch["id"] == channel_id:
                channel = ch
                break
                
        if not channel:
            return {"error": f"Channel with ID {channel_id} not found"}
            
        # If no topic is provided, generate one based on channel theme
        if not topic:
            topic = self._generate_topic_for_channel(channel)
            
        # Generate content based on type
        content_data = None
        
        if content_type == "shorts":
            # Determine the best method based on channel personality
            method = self._get_shorts_method_for_personality(channel["personality"])
            
            # Generate shorts content
            result = self.enhanced_shorts.create_short_by_method(
                method=method,
                topic=topic,
                script=None,  # Auto-generate script
                custom_images=None,  # Auto-generate images
                upload_to_dropbox=True
            )
            
            if result and "video_path" in result:
                cid = f"content_{len(self.channels_data['content']) + 1}"
                content_data = {
                    "content_id": cid,
                    "id": cid,
                    "channel_id": channel_id,
                    "content_type": "shorts",
                    "topic": topic,
                    "method": method,
                    "title": result.get("title", f"{channel['name']} - {topic}"),
                    "description": result.get("description", ""),
                    "video_path": result.get("video_path"),
                    "thumbnail_path": result.get("thumbnail_path"),
                    "dropbox_link": result.get("dropbox_link"),
                    "created_at": datetime.now().isoformat(),
                    "stats": {
                        "views": 0,
                        "likes": 0,
                        "comments": 0,
                        "shares": 0
                    }
                }
                
        elif content_type == "social":
            # Generate social media post
            post_data = self._generate_social_post(channel, topic)
            
            if post_data:
                cid = f"content_{len(self.channels_data['content']) + 1}"
                content_data = {
                    "content_id": cid,
                    "id": cid,
                    "channel_id": channel_id,
                    "content_type": "social",
                    "topic": topic,
                    "platform": post_data.get("platform", "twitter"),
                    "text": post_data.get("text", ""),
                    "image_path": post_data.get("image_path"),
                    "created_at": datetime.now().isoformat(),
                    "stats": {
                        "likes": 0,
                        "comments": 0,
                        "shares": 0
                    }
                }
                
        elif content_type == "blog":
            # Generate blog post
            blog_post = self._generate_blog_post(channel, topic)
            
            if blog_post:
                cid = f"content_{len(self.channels_data['content']) + 1}"
                content_data = {
                    "content_id": cid,
                    "id": cid,
                    "channel_id": channel_id,
                    "content_type": "blog",
                    "topic": topic,
                    "title": blog_post.get("title", f"{topic} - {channel['name']}"),
                    "content": blog_post.get("content", ""),
                    "image_path": blog_post.get("image_path"),
                    "created_at": datetime.now().isoformat(),
                    "stats": {
                        "views": 0,
                        "likes": 0,
                        "comments": 0
                    }
                }
                
        # Save content data if generated successfully
        if content_data:
            self.channels_data["content"].append(content_data)
            
            # Update channel stats
            for ch in self.channels_data["channels"]:
                if ch["id"] == channel_id:
                    ch["stats"]["content_count"] += 1
                    ch["updated_at"] = datetime.now().isoformat()
                    break
                    
            self._save_data()
            
        return content_data

    # Simple helper used in tests
    def generate_channel_content(self, channel_id, content_type="shorts", topic=None, count=1):
        contents = []
        for _ in range(count):
            content = self.generate_content_for_channel(channel_id, content_type, topic)
            if content:
                contents.append(content)
        return contents
    
    def _generate_topic_for_channel(self, channel):
        """
        Generate a topic that aligns with the channel's theme and personality.
        
        Args:
            channel (dict): Channel data
            
        Returns:
            str: Generated topic
        """
        system_message = "You are a content strategist who specializes in topic ideation."
        
        prompt = f"""
        Generate an engaging content topic for a channel with the following characteristics:
        
        Theme: {channel['theme']}
        Personality: {channel['personality']}
        Target Audience: {channel['target_audience']}
        
        The topic should:
        - Be specific enough to create focused content
        - Align with the channel's theme
        - Appeal to the target audience
        - Match the channel's personality
        
        Just provide the topic as a short phrase or title, no explanation needed.
        """
        
        topic = self.openai_generator.generate_content(prompt, system_message, max_tokens=50)
        return topic.strip() if topic else channel['theme']
    
    def _get_shorts_method_for_personality(self, personality):
        """
        Determine the best shorts creation method based on channel personality.
        
        Args:
            personality (str): Channel personality
            
        Returns:
            str: Shorts creation method
        """
        personality = personality.lower()
        
        if "informative" in personality or "educational" in personality or "expert" in personality:
            return "knowledge"
        elif "storyteller" in personality or "narrative" in personality:
            return "story"
        elif "reviewer" in personality or "critic" in personality:
            return "review"
        else:
            # Default to story for other personalities
            return "story"
    
    def _generate_social_post(self, channel, topic):
        """
        Generate a social media post for a channel.
        
        Args:
            channel (dict): Channel data
            topic (str): Post topic
            
        Returns:
            dict: Social post data
        """
        # Determine platform based on channel content types
        platform = "twitter"  # Default
        
        # Generate post text
        system_message = f"You are a social media content creator with a {channel['personality']} personality."
        
        prompt = f"""
        Create an engaging social media post about:
        
        {topic}
        
        The post should:
        - Match a {channel['personality']} personality
        - Be relevant to the theme: {channel['theme']}
        - Appeal to: {channel['target_audience']}
        - Include relevant hashtags
        
        Keep the post under 280 characters for Twitter compatibility.
        """
        
        post_text = self.openai_generator.generate_content(prompt, system_message, max_tokens=200)
        
        # Generate image if needed
        image_path = None
        if random.random() < 0.7:  # 70% chance to include an image
            image_prompt = f"A {channel['visual_style']} image about {topic}, related to {channel['theme']}"
            image_path = self.openai_generator.generate_image(image_prompt)
            
        return {
            "platform": platform,
            "text": post_text.strip() if post_text else f"Check out this content about {topic}! #content",
            "image_path": image_path
        }
    
    def _generate_blog_post(self, channel, topic):
        """
        Generate a blog post for a channel.
        
        Args:
            channel (dict): Channel data
            topic (str): Blog post topic
            
        Returns:
            dict: Blog post data
        """
        # Determine length based on channel personality
        personality = channel['personality'].lower()
        if "detailed" in personality or "thorough" in personality:
            length = "long"
        elif "concise" in personality or "brief" in personality:
            length = "short"
        else:
            length = "medium"
            
        # Generate blog post
        system_message = f"You are a blog writer with a {channel['personality']} personality who writes about {channel['theme']}."
        
        prompt = f"""
        Write a blog post about:
        
        {topic}
        
        The post should:
        - Have a {channel['personality']} tone
        - Be relevant to the theme: {channel['theme']}
        - Appeal to: {channel['target_audience']}
        - Include a compelling title
        - Be formatted in HTML
        
        Length: {length} (short: ~500 words, medium: ~1000 words, long: ~1500 words)
        """
        
        blog_content = self.openai_generator.generate_content(prompt, system_message, max_tokens=3000)
        
        # Extract title from content or generate one
        title = topic
        if blog_content:
            # Try to extract title from H1 or H2 tag
            import re
            title_match = re.search(r"<h[12][^>]*>(.*?)</h[12]>", blog_content, re.IGNORECASE)
            if title_match:
                title = title_match.group(1)
                
        # Generate featured image
        image_path = None
        image_prompt = f"A {channel['visual_style']} featured image for a blog post about {topic}, related to {channel['theme']}"
        image_path = self.openai_generator.generate_image(image_prompt, size="1024x1024")
            
        return {
            "title": title,
            "content": blog_content.strip() if blog_content else f"<p>Content about {topic}</p>",
            "image_path": image_path
        }
    
    def get_channel(self, channel_id):
        """
        Get a channel by ID.
        
        Args:
            channel_id (str): ID of the channel
            
        Returns:
            dict: Channel data or None if not found
        """
        for channel in self.channels_data["channels"]:
            if channel["id"] == channel_id:
                return channel
                
        return None
    
    def get_channel_content(self, channel_id, content_type=None, limit=10):
        """
        Get content for a specific channel.
        
        Args:
            channel_id (str): ID of the channel
            content_type (str): Optional filter by content type
            limit (int): Maximum number of items to return
            
        Returns:
            list: Channel content
        """
        content_list = []
        
        for content in self.channels_data["content"]:
            if content["channel_id"] == channel_id:
                if not content_type or content["content_type"] == content_type:
                    content_list.append(content)
                    
                    if len(content_list) >= limit:
                        break
                        
        return content_list
    
    def get_content(self, content_id):
        """
        Get content by ID.
        
        Args:
            content_id (str): ID of the content
            
        Returns:
            dict: Content data or None if not found
        """
        for content in self.channels_data["content"]:
            if content["content_id"] == content_id:
                return content
                
        return None
    
    def update_channel(self, channel_id, updates):
        """
        Update a channel's information.
        
        Args:
            channel_id (str): ID of the channel
            updates (dict): Updates to apply
            
        Returns:
            dict: Updated channel data or None if not found
        """
        for i, channel in enumerate(self.channels_data["channels"]):
            if channel["id"] == channel_id:
                # Apply updates
                for key, value in updates.items():
                    if key != "id" and key != "created_at":  # Don't allow changing these fields
                        channel[key] = value
                        
                channel["updated_at"] = datetime.now().isoformat()
                self.channels_data["channels"][i] = channel
                self._save_data()
                return channel
                
        return None
    
    def delete_channel(self, channel_id):
        """
        Delete a channel and all its content.
        
        Args:
            channel_id (str): ID of the channel
            
        Returns:
            bool: True if deleted, False if not found
        """
        # Find channel index
        channel_index = None
        for i, channel in enumerate(self.channels_data["channels"]):
            if channel["id"] == channel_id:
                channel_index = i
                break
                
        if channel_index is None:
            return False
            
        # Remove channel
        self.channels_data["channels"].pop(channel_index)
        
        # Remove all content for this channel
        self.channels_data["content"] = [
            content for content in self.channels_data["content"]
            if content["channel_id"] != channel_id
        ]
        
        self._save_data()
        return True
    
    def generate_content_schedule(self, channel_id, days=7):
        """
        Generate a content schedule for a channel.
        
        Args:
            channel_id (str): ID of the channel
            days (int): Number of days to schedule
            
        Returns:
            list: Scheduled content items
        """
        channel = self.get_channel(channel_id)
        if not channel:
            return []
            
        schedule = []
        current_date = datetime.now()
        
        for day in range(days):
            day_date = current_date + timedelta(days=day)
            day_schedule = {
                "date": day_date.strftime("%Y-%m-%d"),
                "content": []
            }
            
            # Check posting frequency for each content type
            for content_type in channel["content_types"]:
                frequency = channel["posting_frequency"].get(content_type, "weekly")
                
                if frequency == "daily":
                    # Schedule every day
                    should_post = True
                elif frequency == "weekly":
                    # Schedule once a week (e.g., on Monday)
                    should_post = day_date.weekday() == 0
                elif frequency == "biweekly":
                    # Schedule twice a week (e.g., on Monday and Thursday)
                    should_post = day_date.weekday() in [0, 3]
                elif frequency == "monthly":
                    # Schedule once a month (e.g., on the 1st)
                    should_post = day_date.day == 1
                else:
                    should_post = False
                    
                if should_post:
                    # Generate topic
                    topic = self._generate_topic_for_channel(channel)
                    
                    day_schedule["content"].append({
                        "content_type": content_type,
                        "topic": topic,
                        "time": f"{random.randint(9, 17):02d}:00"  # Random time between 9 AM and 5 PM
                    })
                    
            schedule.append(day_schedule)
            
        return schedule
    
    def execute_content_schedule(self, schedule_item):
        """
        Execute a scheduled content item.
        
        Args:
            schedule_item (dict): Schedule item with channel_id, content_type, and topic
            
        Returns:
            dict: Generated content data
        """
        return self.generate_content_for_channel(
            schedule_item["channel_id"],
            schedule_item["content_type"],
            schedule_item["topic"]
        )
    
    def get_channel_analytics(self, channel_id, days=30):
        """
        Get analytics for a channel.
        
        Args:
            channel_id (str): ID of the channel
            days (int): Number of days to include
            
        Returns:
            dict: Channel analytics
        """
        channel = self.get_channel(channel_id)
        if not channel:
            return None
            
        # Get content for this channel
        content_list = self.get_channel_content(channel_id, limit=1000)
        
        # Filter by date
        cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
        recent_content = [
            content for content in content_list
            if content["created_at"] >= cutoff_date
        ]
        
        # Calculate metrics
        total_views = sum(content["stats"].get("views", 0) for content in recent_content)
        total_likes = sum(content["stats"].get("likes", 0) for content in recent_content)
        total_comments = sum(content["stats"].get("comments", 0) for content in recent_content)
        total_shares = sum(content["stats"].get("shares", 0) for content in recent_content)
        
        # Group by content type
        content_by_type = {}
        for content in recent_content:
            content_type = content["content_type"]
            if content_type not in content_by_type:
                content_by_type[content_type] = {
                    "count": 0,
                    "views": 0,
                    "likes": 0,
                    "comments": 0,
                    "shares": 0
                }
                
            content_by_type[content_type]["count"] += 1
            content_by_type[content_type]["views"] += content["stats"].get("views", 0)
            content_by_type[content_type]["likes"] += content["stats"].get("likes", 0)
            content_by_type[content_type]["comments"] += content["stats"].get("comments", 0)
            content_by_type[content_type]["shares"] += content["stats"].get("shares", 0)
            
        return {
            "channel_id": channel_id,
            "channel_name": channel["name"],
            "days": days,
            "content_count": len(recent_content),
            "total_views": total_views,
            "total_likes": total_likes,
            "total_comments": total_comments,
            "total_shares": total_shares,
            "engagement_rate": (total_likes + total_comments + total_shares) / max(total_views, 1) * 100,
            "content_by_type": content_by_type
        }

    def get_overall_stats(self):
        """Return overall stats for all channels."""
        return self.channels_data.get("stats", {})

    # Additional simple helper methods for testing purposes
    def publish_content(self, content_id):
        """Simulate publishing content."""
        return {"success": True, "content_id": content_id}

    def generate_content_for_all_channels(self, content_type="social"):
        """Generate one piece of content for each channel."""
        results = {}
        for channel in self.channels_data.get("channels", []):
            content = self.generate_content_for_channel(channel["id"], content_type)
            results[channel["id"]] = content
        return results

    def publish_all_pending_content(self):
        """Simulate publishing all pending content."""
        return {"success": True}

    def get_channel_stats(self, channel_id):
        """Return basic stats for a channel."""
        analytics = self.get_channel_analytics(channel_id, days=30)
        return analytics if analytics else {}
