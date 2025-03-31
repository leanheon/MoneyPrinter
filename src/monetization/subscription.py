import os
import json
from uuid import uuid4
from datetime import datetime
from src.config import get_config
from src.constants import ROOT_DIR
from src.openai_generator import OpenAIGenerator

class SubscriptionManager:
    """
    Class for managing subscription models and membership content
    """
    def __init__(self):
        """
        Initialize the SubscriptionManager with configuration settings
        """
        config = get_config()
        self.subscription_config = config.get("monetization", {}).get("subscription", {})
        self.openai_generator = OpenAIGenerator()
        
        # Create subscription directory if it doesn't exist
        self.subscription_dir = os.path.join(ROOT_DIR, ".mp", "subscription")
        os.makedirs(self.subscription_dir, exist_ok=True)
        
        # Load subscription tiers and members
        self.tiers = self._load_tiers()
        self.members = self._load_members()
        self.content = self._load_content()
        
    def _load_tiers(self):
        """
        Load subscription tiers from storage or create default
        
        Returns:
            dict: Dictionary of subscription tiers
        """
        tiers_file = os.path.join(self.subscription_dir, "tiers.json")
        
        if os.path.exists(tiers_file):
            with open(tiers_file, 'r') as f:
                return json.load(f)
        else:
            # Create default subscription tiers
            default_tiers = {
                "basic": {
                    "name": "Basic Supporter",
                    "price": 4.99,
                    "description": "Support my content and get access to exclusive posts",
                    "benefits": [
                        "Exclusive posts",
                        "Community access",
                        "Monthly Q&A"
                    ],
                    "created_at": datetime.now().isoformat()
                },
                "premium": {
                    "name": "Premium Supporter",
                    "price": 9.99,
                    "description": "Get early access to content and behind-the-scenes material",
                    "benefits": [
                        "All Basic benefits",
                        "Early access to content",
                        "Behind-the-scenes content",
                        "Monthly group call"
                    ],
                    "created_at": datetime.now().isoformat()
                },
                "vip": {
                    "name": "VIP Supporter",
                    "price": 19.99,
                    "description": "Get personalized content and direct access",
                    "benefits": [
                        "All Premium benefits",
                        "Personalized content",
                        "Direct messaging",
                        "Input on future content"
                    ],
                    "created_at": datetime.now().isoformat()
                }
            }
            
            # Save default tiers
            with open(tiers_file, 'w') as f:
                json.dump(default_tiers, f, indent=2)
                
            return default_tiers
            
    def _load_members(self):
        """
        Load members from storage or create default
        
        Returns:
            dict: Dictionary of members
        """
        members_file = os.path.join(self.subscription_dir, "members.json")
        
        if os.path.exists(members_file):
            with open(members_file, 'r') as f:
                return json.load(f)
        else:
            # Create default empty members dictionary
            default_members = {}
            
            # Save default members
            with open(members_file, 'w') as f:
                json.dump(default_members, f, indent=2)
                
            return default_members
            
    def _load_content(self):
        """
        Load subscription content from storage or create default
        
        Returns:
            dict: Dictionary of subscription content
        """
        content_file = os.path.join(self.subscription_dir, "content.json")
        
        if os.path.exists(content_file):
            with open(content_file, 'r') as f:
                return json.load(f)
        else:
            # Create default empty content dictionary
            default_content = {}
            
            # Save default content
            with open(content_file, 'w') as f:
                json.dump(default_content, f, indent=2)
                
            return default_content
            
    def add_tier(self, name, price, description, benefits):
        """
        Add a new subscription tier
        
        Args:
            name (str): Tier name
            price (float): Monthly price
            description (str): Tier description
            benefits (list): List of benefits
            
        Returns:
            str: Tier ID if successful, None otherwise
        """
        try:
            tier_id = name.lower().replace(' ', '_')
            
            self.tiers[tier_id] = {
                "name": name,
                "price": price,
                "description": description,
                "benefits": benefits,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
            
            # Save updated tiers
            tiers_file = os.path.join(self.subscription_dir, "tiers.json")
            with open(tiers_file, 'w') as f:
                json.dump(self.tiers, f, indent=2)
                
            return tier_id
        except Exception as e:
            print(f"Error adding tier: {e}")
            return None
            
    def add_member(self, name, email, tier_id, platform_username=None):
        """
        Add a new member to a subscription tier
        
        Args:
            name (str): Member name
            email (str): Member email
            tier_id (str): Subscription tier ID
            platform_username (str, optional): Username on platform
            
        Returns:
            str: Member ID if successful, None otherwise
        """
        try:
            if tier_id not in self.tiers:
                print(f"Tier {tier_id} not found")
                return None
                
            member_id = f"member_{uuid4().hex[:8]}"
            
            self.members[member_id] = {
                "name": name,
                "email": email,
                "tier_id": tier_id,
                "platform_username": platform_username,
                "join_date": datetime.now().isoformat(),
                "status": "active",
                "last_payment": datetime.now().isoformat()
            }
            
            # Save updated members
            members_file = os.path.join(self.subscription_dir, "members.json")
            with open(members_file, 'w') as f:
                json.dump(self.members, f, indent=2)
                
            return member_id
        except Exception as e:
            print(f"Error adding member: {e}")
            return None
            
    def get_members_by_tier(self, tier_id):
        """
        Get all members of a specific tier
        
        Args:
            tier_id (str): Subscription tier ID
            
        Returns:
            list: List of member dictionaries
        """
        tier_members = []
        
        for member_id, member in self.members.items():
            if member.get("tier_id") == tier_id and member.get("status") == "active":
                member_with_id = member.copy()
                member_with_id["member_id"] = member_id
                tier_members.append(member_with_id)
                
        return tier_members
        
    def add_subscription_content(self, title, content_type, tier_ids, content_text, platform=None):
        """
        Add new subscription content
        
        Args:
            title (str): Content title
            content_type (str): Type of content (post, video, etc.)
            tier_ids (list): List of tier IDs that can access this content
            content_text (str): The content text
            platform (str, optional): Platform for the content
            
        Returns:
            str: Content ID if successful, None otherwise
        """
        try:
            content_id = f"content_{uuid4().hex[:8]}"
            
            self.content[content_id] = {
                "title": title,
                "content_type": content_type,
                "tier_ids": tier_ids,
                "content_text": content_text,
                "platform": platform,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
            
            # Save updated content
            content_file = os.path.join(self.subscription_dir, "content.json")
            with open(content_file, 'w') as f:
                json.dump(self.content, f, indent=2)
                
            return content_id
        except Exception as e:
            print(f"Error adding subscription content: {e}")
            return None
            
    def get_content_for_tier(self, tier_id):
        """
        Get all content available for a specific tier
        
        Args:
            tier_id (str): Subscription tier ID
            
        Returns:
            list: List of content dictionaries
        """
        tier_content = []
        
        for content_id, content_item in self.content.items():
            if tier_id in content_item.get("tier_ids", []):
                content_with_id = content_item.copy()
                content_with_id["content_id"] = content_id
                tier_content.append(content_with_id)
                
        return tier_content
        
    def generate_subscription_content(self, topic, content_type, tier_id):
        """
        Generate subscription content for a specific tier
        
        Args:
            topic (str): Content topic
            content_type (str): Type of content (post, update, tutorial, etc.)
            tier_id (str): Tier ID for which to generate content
            
        Returns:
            dict: Generated content information
        """
        if tier_id not in self.tiers:
            print(f"Tier {tier_id} not found")
            return None
            
        tier = self.tiers[tier_id]
        
        system_message = "You are a content creator who specializes in creating exclusive content for subscribers."
        
        prompt = f"""
        Create exclusive {content_type} content for subscribers about:
        
        Topic: {topic}
        Subscription Tier: {tier['name']} (${tier['price']}/month)
        Tier Benefits: {', '.join(tier['benefits'])}
        
        The content should:
        1. Be valuable and exclusive
        2. Match the quality expected for this tier level
        3. Include a personal touch for subscribers
        4. Be engaging and informative
        
        Format your response as a JSON object with 'title' and 'content' fields.
        """
        
        try:
            response = self.openai_generator.generate_structured_content(
                prompt, 
                system_message,
                output_structure={
                    "title": "Content Title",
                    "content": "Exclusive content for subscribers"
                }
            )
            
            if not response:
                return None
                
            # Add the content to the subscription system
            content_id = self.add_subscription_content(
                title=response["title"],
                content_type=content_type,
                tier_ids=[tier_id],
                content_text=response["content"]
            )
            
            if content_id:
                return {
                    "content_id": content_id,
                    "title": response["title"],
                    "content": response["content"],
                    "tier_id": tier_id,
                    "tier_name": tier["name"]
                }
            else:
                return None
                
        except Exception as e:
            print(f"Error generating subscription content: {e}")
            return None
            
    def generate_tier_promotion(self, tier_id, platform):
        """
        Generate promotional content for a subscription tier
        
        Args:
            tier_id (str): ID of the tier to promote
            platform (str): Platform for promotion (youtube, twitter, threads)
            
        Returns:
            dict: Generated promotional content
        """
        if tier_id not in self.tiers:
            print(f"Tier {tier_id} not found")
            return None
            
        tier = self.tiers[tier_id]
        
        # Generate content based on platform
        if platform == "youtube":
            return self.generate_youtube_tier_promotion(tier, tier_id)
        elif platform == "twitter":
            return self.generate_twitter_tier_promotion(tier, tier_id)
        elif platform == "threads":
            return self.generate_threads_tier_promotion(tier, tier_id)
        else:
            print(f"Unsupported platform: {platform}")
            return None
            
    def generate_youtube_tier_promotion(self, tier, tier_id):
        """
        Generate YouTube promotional content for a subscription tier
        
        Args:
            tier (dict): Tier information
            tier_id (str): Tier ID
            
        Returns:
            dict: Generated promotional content
        """
        system_message = "You are a YouTube content creator who promotes subscription memberships."
        
        prompt = f"""
        Create a YouTube video script and description to promote the following subscription tier:
        
        Tier: {tier['name']}
        Price: ${tier['price']}/month
        Description: {tier['description']}
        Benefits: {', '.join(tier['benefits'])}
        
        The content should:
        1. Be engaging and highlight the value
        2. Explain the benefits clearly
        3. Include a clear call-to-action
        4. Make subscribers feel special
        
        Format your response as a JSON object with 'title', 'script', and 'description' fields.
        """
        
        try:
            response = self.openai_generator.generate_structured_content(
                prompt, 
                system_message,
                output_structure={
                    "title": "Video Title",
                    "script": "Video script",
                    "description": "Video description"
                }
            )
            
            if not response:
                return None
                
            # Add subscription link to description
            description = response.get("description", "")
            description += f"\n\nJoin the {tier['name']} tier here: [SUBSCRIPTION_LINK]\n"
            response["description"] = description
            
            # Add tier information to response
            response["tier"] = {
                "tier_id": tier_id,
                "name": tier['name'],
                "price": tier['price'],
                "benefits": tier['benefits']
            }
            
            return response
        except Exception as e:
            print(f"Error generating YouTube tier promotion: {e}")
            return None
            
    def generate_twitter_tier_promotion(self, tier, tier_id):
        """
        Generate Twitter/X promotional content for a subscription tier
        
        Args:
            tier (dict): Tier information
            tier_id (str): Tier ID
            
        Returns:
            dict: Generated promotional content
        """
        system_message = "You are a social media marketer who promotes subscription memberships."
        
        prompt = f"""
        Create a Twitter/X post to promote the following subscription tier:
        
        Tier: {tier['name']}
        Price: ${tier['price']}/month
        Description: {tier['description']}
        Benefits: {', '.join(tier['benefits'])}
        
        The post should:
        1. Be engaging and highlight the value
        2. Mention a key benefit
        3. Include a clear call-to-action
        4. Be under 280 characters (Twitter's limit)
        
        Format your response as a JSON object with a 'post' field containing the tweet text.
        """
        
        try:
            response = self.openai_generator.generate_structured_content(
                prompt, 
                system_message,
                output_structure={
                    "post": "Twitter post"
                }
            )
            
            if not response:
                return None
                
            # Add tier information to response
            response["tier"] = {
                "tier_id": tier_id,
                "name": tier['name'],
                "price": tier['price'],
                "benefits": tier['benefits']
            }
            
            return response
        except Exception as e:
            print(f"Error generating Twitter tier promotion: {e}")
            return None
            
    def generate_threads_tier_promotion(self, tier, tier_id):
        """
        Generate Threads promotional content for a subscription tier
        
        Args:
            tier (dict): Tier information
            tier_id (str): Tier ID
            
        Returns:
            dict: Generated promotional content
        """
        system_message = "You are a social media marketer who promotes subscription memberships."
        
        prompt = f"""
        Create a Threads post to promote the following subscription tier:
        
        Tier: {tier['name']}
        Price: ${tier['price']}/month
        Description: {tier['description']}
        Benefits: {', '.join(tier['benefits'])}
        
        The post should:
        1. Be engaging and highlight the value
        2. Explain the key benefits
        3. Include a clear call-to-action
        4. Be under 500 characters (Threads' limit)
        
        Format your response as a JSON object with a 'post' field containing the Threads post text.
        """
        
        try:
            response = self.openai_generator.generate_structured_content(
                prompt, 
                system_message,
                output_structure={
                    "post": "Threads post"
                }
            )
            
            if not response:
                return None
                
            # Add tier information to response
            response["tier"] = {
                "tier_id": tier_id,
                "name": tier['name'],
                "price": tier['price'],
                "benefits": tier['benefits']
            }
            
            return response
        except Exception as e:
            print(f"Error generating Threads tier promotion: {e}")
            return None
