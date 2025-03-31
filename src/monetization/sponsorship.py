import os
import json
import requests
from uuid import uuid4
from datetime import datetime
from src.config import get_config
from src.constants import ROOT_DIR
from src.openai_generator import OpenAIGenerator

class SponsorshipManager:
    """
    Class for managing brand sponsorships and sponsored content generation
    """
    def __init__(self):
        """
        Initialize the SponsorshipManager with configuration settings
        """
        config = get_config()
        self.sponsorship_config = config.get("monetization", {}).get("sponsorship", {})
        self.openai_generator = OpenAIGenerator()
        
        # Create sponsorship directory if it doesn't exist
        self.sponsorship_dir = os.path.join(ROOT_DIR, ".mp", "sponsorship")
        os.makedirs(self.sponsorship_dir, exist_ok=True)
        
        # Load sponsorship brands and campaigns
        self.brands = self._load_brands()
        self.campaigns = self._load_campaigns()
        
    def _load_brands(self):
        """
        Load brand information from storage or create default
        
        Returns:
            dict: Dictionary of brands and their details
        """
        brands_file = os.path.join(self.sponsorship_dir, "brands.json")
        
        if os.path.exists(brands_file):
            with open(brands_file, 'r') as f:
                return json.load(f)
        else:
            # Create default empty brands dictionary
            default_brands = {}
            
            # Save default brands
            with open(brands_file, 'w') as f:
                json.dump(default_brands, f, indent=2)
                
            return default_brands
            
    def _load_campaigns(self):
        """
        Load campaign information from storage or create default
        
        Returns:
            dict: Dictionary of campaigns and their details
        """
        campaigns_file = os.path.join(self.sponsorship_dir, "campaigns.json")
        
        if os.path.exists(campaigns_file):
            with open(campaigns_file, 'r') as f:
                return json.load(f)
        else:
            # Create default empty campaigns dictionary
            default_campaigns = {}
            
            # Save default campaigns
            with open(campaigns_file, 'w') as f:
                json.dump(default_campaigns, f, indent=2)
                
            return default_campaigns
            
    def add_brand(self, name, industry, website, contact_email=None, description=None):
        """
        Add a new brand to the sponsorship system
        
        Args:
            name (str): Brand name
            industry (str): Industry category
            website (str): Brand website
            contact_email (str, optional): Contact email
            description (str, optional): Brand description
            
        Returns:
            str: Brand ID if successful, None otherwise
        """
        try:
            brand_id = f"brand_{uuid4().hex[:8]}"
            
            self.brands[brand_id] = {
                "name": name,
                "industry": industry,
                "website": website,
                "contact_email": contact_email,
                "description": description,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
            
            # Save updated brands
            brands_file = os.path.join(self.sponsorship_dir, "brands.json")
            with open(brands_file, 'w') as f:
                json.dump(self.brands, f, indent=2)
                
            return brand_id
        except Exception as e:
            print(f"Error adding brand: {e}")
            return None
            
    def add_campaign(self, brand_id, name, budget, start_date, end_date, 
                    platforms, requirements=None, talking_points=None):
        """
        Add a new sponsorship campaign
        
        Args:
            brand_id (str): ID of the brand
            name (str): Campaign name
            budget (float): Campaign budget
            start_date (str): Start date (YYYY-MM-DD)
            end_date (str): End date (YYYY-MM-DD)
            platforms (list): List of platforms (youtube, twitter, threads)
            requirements (list, optional): List of campaign requirements
            talking_points (list, optional): List of talking points
            
        Returns:
            str: Campaign ID if successful, None otherwise
        """
        try:
            if brand_id not in self.brands:
                print(f"Brand {brand_id} not found")
                return None
                
            campaign_id = f"campaign_{uuid4().hex[:8]}"
            
            self.campaigns[campaign_id] = {
                "brand_id": brand_id,
                "name": name,
                "budget": budget,
                "start_date": start_date,
                "end_date": end_date,
                "platforms": platforms,
                "requirements": requirements or [],
                "talking_points": talking_points or [],
                "status": "active",
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "posts": []
            }
            
            # Save updated campaigns
            campaigns_file = os.path.join(self.sponsorship_dir, "campaigns.json")
            with open(campaigns_file, 'w') as f:
                json.dump(self.campaigns, f, indent=2)
                
            return campaign_id
        except Exception as e:
            print(f"Error adding campaign: {e}")
            return None
            
    def get_active_campaigns(self, platform=None):
        """
        Get active campaigns, optionally filtered by platform
        
        Args:
            platform (str, optional): Filter by platform
            
        Returns:
            list: List of active campaign dictionaries
        """
        active_campaigns = []
        
        for campaign_id, campaign in self.campaigns.items():
            # Skip if campaign is not active
            if campaign.get("status") != "active":
                continue
                
            # Skip if platform is specified and not in campaign platforms
            if platform and platform not in campaign.get("platforms", []):
                continue
                
            # Add brand information to campaign
            brand_id = campaign.get("brand_id")
            if brand_id in self.brands:
                campaign_with_brand = campaign.copy()
                campaign_with_brand["brand"] = self.brands[brand_id]
                campaign_with_brand["campaign_id"] = campaign_id
                active_campaigns.append(campaign_with_brand)
                
        return active_campaigns
        
    def find_relevant_campaign(self, topic, platform):
        """
        Find a relevant campaign for a given topic and platform
        
        Args:
            topic (str): Content topic
            platform (str): Platform (youtube, twitter, threads)
            
        Returns:
            dict: Relevant campaign or None if not found
        """
        # Get active campaigns for the platform
        active_campaigns = self.get_active_campaigns(platform)
        
        if not active_campaigns:
            return None
            
        # Use OpenAI to find the most relevant campaign
        system_message = "You are a sponsorship matching expert who helps content creators find relevant brand partnerships."
        
        campaigns_info = "\n".join([
            f"Campaign ID: {c['campaign_id']}\nBrand: {c['brand']['name']}\nIndustry: {c['brand']['industry']}\nCampaign: {c['name']}\nTalking Points: {', '.join(c['talking_points'])}"
            for c in active_campaigns
        ])
        
        prompt = f"""
        Find the most relevant sponsorship campaign for content about:
        
        Topic: {topic}
        Platform: {platform}
        
        Available campaigns:
        {campaigns_info}
        
        Return only the campaign ID of the most relevant campaign, or "none" if none are relevant.
        """
        
        try:
            response = self.openai_generator.generate_content(prompt, system_message, max_tokens=50)
            
            if not response:
                return None
                
            # Extract campaign ID from response
            for campaign in active_campaigns:
                if campaign["campaign_id"] in response:
                    return campaign
                    
            return None
        except Exception as e:
            print(f"Error finding relevant campaign: {e}")
            return None
            
    def generate_sponsored_content(self, topic, platform, campaign=None):
        """
        Generate sponsored content for a given topic and platform
        
        Args:
            topic (str): Content topic
            platform (str): Platform (youtube, twitter, threads)
            campaign (dict, optional): Specific campaign to use
            
        Returns:
            dict: Generated sponsored content
        """
        # Find relevant campaign if not provided
        if not campaign:
            campaign = self.find_relevant_campaign(topic, platform)
            
        if not campaign:
            # No relevant campaign found, generate mock campaign for demonstration
            brand_id = self.add_brand(
                name="Example Brand",
                industry="Technology",
                website="https://example.com",
                description="A demonstration brand for sponsored content"
            )
            
            campaign_id = self.add_campaign(
                brand_id=brand_id,
                name="Example Campaign",
                budget=1000.0,
                start_date=datetime.now().strftime("%Y-%m-%d"),
                end_date=(datetime.now().replace(month=datetime.now().month+1)).strftime("%Y-%m-%d"),
                platforms=[platform],
                talking_points=["Product features", "Benefits", "Special offer"]
            )
            
            campaign = self.campaigns[campaign_id]
            campaign["brand"] = self.brands[brand_id]
            campaign["campaign_id"] = campaign_id
            
        # Generate content based on platform
        if platform == "youtube":
            return self.generate_youtube_sponsored_content(topic, campaign)
        elif platform == "twitter":
            return self.generate_twitter_sponsored_content(topic, campaign)
        elif platform == "threads":
            return self.generate_threads_sponsored_content(topic, campaign)
        else:
            print(f"Unsupported platform: {platform}")
            return None
            
    def generate_youtube_sponsored_content(self, topic, campaign):
        """
        Generate YouTube sponsored content
        
        Args:
            topic (str): Content topic
            campaign (dict): Campaign information
            
        Returns:
            dict: Generated sponsored content
        """
        brand = campaign["brand"]
        talking_points = campaign.get("talking_points", [])
        
        system_message = "You are a YouTube content creator who specializes in sponsored content."
        
        prompt = f"""
        Create a YouTube video script and description for sponsored content.
        
        Topic: {topic}
        Brand: {brand['name']}
        Industry: {brand['industry']}
        Brand Description: {brand.get('description', 'N/A')}
        Talking Points: {', '.join(talking_points)}
        
        The content should:
        1. Be engaging and relevant to the topic
        2. Naturally integrate the brand and talking points
        3. Include a clear sponsorship disclosure
        4. Have a call-to-action for the brand
        5. Be structured as an introduction, main content, and conclusion
        
        Format your response as a JSON object with 'title', 'script', and 'description' fields.
        """
        
        try:
            response = self.openai_generator.generate_structured_content(
                prompt, 
                system_message,
                output_structure={
                    "title": "Video Title",
                    "script": "Video script with sponsorship",
                    "description": "Video description with sponsorship"
                }
            )
            
            if not response:
                return None
                
            # Add sponsorship disclosure if not present
            script = response.get("script", "")
            if "sponsor" not in script.lower():
                response["script"] = "This video is sponsored by " + brand["name"] + ".\n\n" + script
                
            description = response.get("description", "")
            if "sponsor" not in description.lower():
                response["description"] += f"\n\n#ad #sponsored @{brand['name'].replace(' ', '')}"
                
            # Add campaign information to response
            response["campaign"] = {
                "campaign_id": campaign["campaign_id"],
                "brand_name": brand["name"],
                "brand_website": brand["website"]
            }
            
            # Record this post in the campaign
            self._record_sponsored_post(
                campaign["campaign_id"],
                platform="youtube",
                content_type="video",
                title=response["title"]
            )
            
            return response
        except Exception as e:
            print(f"Error generating YouTube sponsored content: {e}")
            return None
            
    def generate_twitter_sponsored_content(self, topic, campaign):
        """
        Generate Twitter/X sponsored content
        
        Args:
            topic (str): Content topic
            campaign (dict): Campaign information
            
        Returns:
            dict: Generated sponsored content
        """
        brand = campaign["brand"]
        talking_points = campaign.get("talking_points", [])
        
        system_message = "You are a social media marketer who creates engaging sponsored posts."
        
        prompt = f"""
        Create a Twitter/X sponsored post.
        
        Topic: {topic}
        Brand: {brand['name']}
        Industry: {brand['industry']}
        Brand Description: {brand.get('description', 'N/A')}
        Talking Points: {', '.join(talking_points)}
        
        The post should:
        1. Be engaging and relevant to the topic
        2. Naturally integrate the brand
        3. Include a clear sponsorship disclosure
        4. Have a call-to-action
        5. Be under 280 characters (Twitter's limit)
        
        Format your response as a JSON object with a 'post' field containing the tweet text.
        """
        
        try:
            response = self.openai_generator.generate_structured_content(
                prompt, 
                system_message,
                output_structure={
                    "post": "Twitter sponsored post"
                }
            )
            
            if not response:
                return None
                
            # Add sponsorship disclosure if not present
            post = response.get("post", "")
            if "sponsor" not in post.lower() and "#ad" not in post.lower():
                # Try to add a minimal disclosure
                if len(post) <= 275:
                    post += " #ad"
                    
            response["post"] = post
            
            # Add campaign information to response
            response["campaign"] = {
                "campaign_id": campaign["campaign_id"],
                "brand_name": brand["name"],
                "brand_website": brand["website"]
            }
            
            # Record this post in the campaign
            self._record_sponsored_post(
                campaign["campaign_id"],
                platform="twitter",
                content_type="post",
                title=post[:30] + "..."
            )
            
            return response
        except Exception as e:
            print(f"Error generating Twitter sponsored content: {e}")
            return None
            
    def generate_threads_sponsored_content(self, topic, campaign):
        """
        Generate Threads sponsored content
        
        Args:
            topic (str): Content topic
            campaign (dict): Campaign information
            
        Returns:
            dict: Generated sponsored content
        """
        brand = campaign["brand"]
        talking_points = campaign.get("talking_points", [])
        
        system_message = "You are a social media marketer who creates engaging sponsored posts."
        
        prompt = f"""
        Create a Threads sponsored post.
        
        Topic: {topic}
        Brand: {brand['name']}
        Industry: {brand['industry']}
        Brand Description: {brand.get('description', 'N/A')}
        Talking Points: {', '.join(talking_points)}
        
        The post should:
        1. Be engaging and relevant to the topic
        2. Naturally integrate the brand
        3. Include a clear sponsorship disclosure
        4. Have a call-to-action
        5. Be under 500 characters (Threads' limit)
        
        Format your response as a JSON object with a 'post' field containing the Threads post text.
        """
        
        try:
            response = self.openai_generator.generate_structured_content(
                prompt, 
                system_message,
                output_structure={
                    "post": "Threads sponsored post"
                }
            )
            
            if not response:
                return None
                
            # Add sponsorship disclosure if not present
            post = response.get("post", "")
            if "sponsor" not in post.lower() and "#ad" not in post.lower():
                # Try to add a disclosure
                if len(post) <= 480:
                    post += "\n\n#ad #sponsored"
                    
            response["post"] = post
            
            # Add campaign information to response
            response["campaign"] = {
                "campaign_id": campaign["campaign_id"],
                "brand_name": brand["name"],
                "brand_website": brand["website"]
            }
            
            # Record this post in the campaign
            self._record_sponsored_post(
                campaign["campaign_id"],
                platform="threads",
                content_type="post",
                title=post[:30] + "..."
            )
            
            return response
        except Exception as e:
            print(f"Error generating Threads sponsored content: {e}")
            return None
            
    def _record_sponsored_post(self, campaign_id, platform, content_type, title):
        """
        Record a sponsored post in the campaign
        
        Args:
            campaign_id (str): Campaign ID
            platform (str): Platform
            content_type (str): Content type
            title (str): Content title
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if campaign_id not in self.campaigns:
                return False
                
            post = {
                "platform": platform,
                "content_type": content_type,
                "title": title,
                "created_at": datetime.now().isoformat()
            }
            
            self.campaigns[campaign_id]["posts"].append(post)
            self.campaigns[campaign_id]["updated_at"] = datetime.now().isoformat()
            
            # Save updated campaigns
            campaigns_file = os.path.join(self.sponsorship_dir, "campaigns.json")
            with open(campaigns_file, 'w') as f:
                json.dump(self.campaigns, f, indent=2)
                
            return True
        except Exception as e:
            print(f"Error recording sponsored post: {e}")
            return False
            
    def generate_media_kit(self, platform_stats):
        """
        Generate a media kit for sponsorship outreach
        
        Args:
            platform_stats (dict): Statistics for each platform
            
        Returns:
            dict: Media kit content
        """
        system_message = "You are a professional media kit creator for content creators seeking sponsorships."
        
        platforms_info = "\n".join([
            f"Platform: {platform}\nFollowers: {stats.get('followers', 'N/A')}\nEngagement Rate: {stats.get('engagement_rate', 'N/A')}\nAverage Views: {stats.get('avg_views', 'N/A')}"
            for platform, stats in platform_stats.items()
        ])
        
        prompt = f"""
        Create a professional media kit for a content creator seeking brand sponsorships.
        
        Platform Statistics:
        {platforms_info}
        
        The media kit should include:
        1. A compelling bio/introduction
        2. Audience demographics and reach
        3. Content themes and topics
        4. Sponsorship packages and rates
        5. Previous brand collaborations (hypothetical if needed)
        6. Contact information
        
        Format your response as a JSON object with sections for each part of the media kit.
        """
        
        try:
            response = self.openai_generator.generate_structured_content(
                prompt, 
                system_message,
                output_structure={
                    "introduction": "Creator bio and introduction",
                    "audience": "Audience demographics and reach",
                    "content": "Content themes and topics",
                    "packages": "Sponsorship packages and rates",
                    "collaborations": "Previous brand collaborations",
                    "contact": "Contact information"
                }
            )
            
            return response
        except Exception as e:
            print(f"Error generating media kit: {e}")
            return None
