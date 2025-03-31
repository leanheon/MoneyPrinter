import os
import json
import requests
from uuid import uuid4
from src.config import get_config
from src.constants import ROOT_DIR
from src.openai_generator import OpenAIGenerator

class AffiliateManager:
    """
    Class for managing affiliate marketing integrations and content generation
    """
    def __init__(self):
        """
        Initialize the AffiliateManager with configuration settings
        """
        config = get_config()
        self.affiliate_config = config.get("monetization", {}).get("affiliate", {})
        self.openai_generator = OpenAIGenerator()
        
        # Create affiliate directory if it doesn't exist
        self.affiliate_dir = os.path.join(ROOT_DIR, ".mp", "affiliate")
        os.makedirs(self.affiliate_dir, exist_ok=True)
        
        # Load affiliate programs and products
        self.affiliate_programs = self._load_affiliate_programs()
        
    def _load_affiliate_programs(self):
        """
        Load affiliate programs from configuration or default
        
        Returns:
            dict: Dictionary of affiliate programs and their details
        """
        # Check if affiliate programs file exists
        affiliate_file = os.path.join(self.affiliate_dir, "programs.json")
        
        if os.path.exists(affiliate_file):
            with open(affiliate_file, 'r') as f:
                return json.load(f)
        else:
            # Create default affiliate programs
            default_programs = {
                "amazon": {
                    "name": "Amazon Associates",
                    "base_url": "https://www.amazon.com/dp/",
                    "tag_param": "tag",
                    "tag_id": self.affiliate_config.get("amazon_tag", ""),
                    "commission": "1-10%",
                    "products": {}
                },
                "clickbank": {
                    "name": "ClickBank",
                    "base_url": "https://hop.clickbank.net/",
                    "tag_param": "affiliate",
                    "tag_id": self.affiliate_config.get("clickbank_id", ""),
                    "commission": "30-75%",
                    "products": {}
                }
            }
            
            # Save default programs
            with open(affiliate_file, 'w') as f:
                json.dump(default_programs, f, indent=2)
                
            return default_programs
            
    def add_affiliate_program(self, program_id, name, base_url, tag_param, tag_id, commission):
        """
        Add a new affiliate program
        
        Args:
            program_id (str): Unique identifier for the program
            name (str): Name of the affiliate program
            base_url (str): Base URL for affiliate links
            tag_param (str): Parameter name for affiliate ID
            tag_id (str): Your affiliate ID
            commission (str): Commission rate description
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            self.affiliate_programs[program_id] = {
                "name": name,
                "base_url": base_url,
                "tag_param": tag_param,
                "tag_id": tag_id,
                "commission": commission,
                "products": {}
            }
            
            # Save updated programs
            affiliate_file = os.path.join(self.affiliate_dir, "programs.json")
            with open(affiliate_file, 'w') as f:
                json.dump(self.affiliate_programs, f, indent=2)
                
            return True
        except Exception as e:
            print(f"Error adding affiliate program: {e}")
            return False
            
    def add_product(self, program_id, product_id, name, description, price, category, url_suffix=""):
        """
        Add a product to an affiliate program
        
        Args:
            program_id (str): ID of the affiliate program
            product_id (str): Unique product identifier
            name (str): Product name
            description (str): Product description
            price (str): Product price
            category (str): Product category
            url_suffix (str, optional): Additional URL parameters
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if program_id not in self.affiliate_programs:
                print(f"Affiliate program {program_id} not found")
                return False
                
            self.affiliate_programs[program_id]["products"][product_id] = {
                "name": name,
                "description": description,
                "price": price,
                "category": category,
                "url_suffix": url_suffix
            }
            
            # Save updated programs
            affiliate_file = os.path.join(self.affiliate_dir, "programs.json")
            with open(affiliate_file, 'w') as f:
                json.dump(self.affiliate_programs, f, indent=2)
                
            return True
        except Exception as e:
            print(f"Error adding product: {e}")
            return False
            
    def generate_affiliate_link(self, program_id, product_id):
        """
        Generate an affiliate link for a specific product
        
        Args:
            program_id (str): ID of the affiliate program
            product_id (str): ID of the product
            
        Returns:
            str: Affiliate link or None if error
        """
        try:
            if program_id not in self.affiliate_programs:
                print(f"Affiliate program {program_id} not found")
                return None
                
            program = self.affiliate_programs[program_id]
            
            if product_id not in program["products"]:
                print(f"Product {product_id} not found in {program_id}")
                return None
                
            base_url = program["base_url"]
            tag_param = program["tag_param"]
            tag_id = program["tag_id"]
            url_suffix = program["products"][product_id].get("url_suffix", "")
            
            # Construct the affiliate link based on the program
            if program_id == "amazon":
                # Amazon format: https://www.amazon.com/dp/PRODUCTID?tag=TAGID
                affiliate_link = f"{base_url}{product_id}?{tag_param}={tag_id}{url_suffix}"
            elif program_id == "clickbank":
                # ClickBank format: https://hop.clickbank.net/?affiliate=TAGID&vendor=PRODUCTID
                affiliate_link = f"{base_url}?{tag_param}={tag_id}&vendor={product_id}{url_suffix}"
            else:
                # Generic format
                affiliate_link = f"{base_url}{product_id}?{tag_param}={tag_id}{url_suffix}"
                
            return affiliate_link
        except Exception as e:
            print(f"Error generating affiliate link: {e}")
            return None
            
    def find_relevant_products(self, topic, category=None, max_products=3):
        """
        Find relevant products for a given topic
        
        Args:
            topic (str): The content topic
            category (str, optional): Specific product category
            max_products (int, optional): Maximum number of products to return
            
        Returns:
            list: List of relevant product dictionaries with affiliate links
        """
        relevant_products = []
        
        # Iterate through all programs and their products
        for program_id, program in self.affiliate_programs.items():
            for product_id, product in program["products"].items():
                # Skip if category is specified and doesn't match
                if category and product["category"] != category:
                    continue
                    
                # Check if product is relevant to the topic
                # This is a simple check - could be enhanced with AI
                if (topic.lower() in product["name"].lower() or 
                    topic.lower() in product["description"].lower()):
                    
                    # Generate affiliate link
                    affiliate_link = self.generate_affiliate_link(program_id, product_id)
                    
                    if affiliate_link:
                        relevant_products.append({
                            "program_id": program_id,
                            "program_name": program["name"],
                            "product_id": product_id,
                            "name": product["name"],
                            "description": product["description"],
                            "price": product["price"],
                            "category": product["category"],
                            "affiliate_link": affiliate_link
                        })
                        
                        # Break if we've reached the maximum number of products
                        if len(relevant_products) >= max_products:
                            return relevant_products
                            
        return relevant_products
        
    def generate_affiliate_content(self, topic, platform, product_count=1):
        """
        Generate content with affiliate links for a given topic and platform
        
        Args:
            topic (str): The content topic
            platform (str): The platform (youtube, twitter, threads)
            product_count (int, optional): Number of products to include
            
        Returns:
            dict: Generated content with affiliate links
        """
        # Find relevant products
        products = self.find_relevant_products(topic, max_products=product_count)
        
        if not products:
            # No relevant products found, try to suggest some using AI
            products = self.suggest_products_with_ai(topic, product_count)
            
        if not products:
            # Still no products, return None
            return None
            
        # Generate content based on platform
        if platform == "youtube":
            return self.generate_youtube_affiliate_content(topic, products)
        elif platform == "twitter":
            return self.generate_twitter_affiliate_content(topic, products)
        elif platform == "threads":
            return self.generate_threads_affiliate_content(topic, products)
        else:
            print(f"Unsupported platform: {platform}")
            return None
            
    def suggest_products_with_ai(self, topic, product_count=1):
        """
        Use AI to suggest relevant products for a topic
        
        Args:
            topic (str): The content topic
            product_count (int, optional): Number of products to suggest
            
        Returns:
            list: List of suggested product dictionaries
        """
        system_message = "You are a product recommendation expert who specializes in affiliate marketing."
        
        prompt = f"""
        Suggest {product_count} relevant products that would be good for affiliate marketing for content about:
        
        Topic: {topic}
        
        For each product, provide:
        1. A product name
        2. A brief description
        3. An estimated price range
        4. A suitable category
        5. Which affiliate program would be best (Amazon or ClickBank)
        
        Format your response as a JSON array of objects with the fields: name, description, price, category, and program.
        """
        
        try:
            # Generate product suggestions
            response = self.openai_generator.generate_structured_content(
                prompt, 
                system_message,
                output_structure=[{
                    "name": "Product Name",
                    "description": "Brief product description",
                    "price": "$XX.XX",
                    "category": "Category",
                    "program": "amazon or clickbank"
                }]
            )
            
            if not response or not isinstance(response, list):
                return []
                
            # Convert AI suggestions to product format
            suggested_products = []
            for item in response:
                program_id = item.get("program", "").lower()
                if program_id not in ["amazon", "clickbank"]:
                    program_id = "amazon"  # Default to Amazon
                    
                # Create a unique product ID
                product_id = f"ai_{uuid4().hex[:8]}"
                
                # Add the product to the affiliate program
                self.add_product(
                    program_id,
                    product_id,
                    item.get("name", ""),
                    item.get("description", ""),
                    item.get("price", ""),
                    item.get("category", "")
                )
                
                # Generate affiliate link
                affiliate_link = self.generate_affiliate_link(program_id, product_id)
                
                if affiliate_link:
                    suggested_products.append({
                        "program_id": program_id,
                        "program_name": self.affiliate_programs[program_id]["name"],
                        "product_id": product_id,
                        "name": item.get("name", ""),
                        "description": item.get("description", ""),
                        "price": item.get("price", ""),
                        "category": item.get("category", ""),
                        "affiliate_link": affiliate_link
                    })
                    
            return suggested_products
        except Exception as e:
            print(f"Error suggesting products with AI: {e}")
            return []
            
    def generate_youtube_affiliate_content(self, topic, products):
        """
        Generate YouTube description with affiliate links
        
        Args:
            topic (str): The content topic
            products (list): List of product dictionaries
            
        Returns:
            dict: Generated content with affiliate links
        """
        system_message = "You are a YouTube content creator who specializes in affiliate marketing."
        
        product_info = "\n".join([
            f"Product: {p['name']}\nDescription: {p['description']}\nPrice: {p['price']}\nLink: {p['affiliate_link']}"
            for p in products
        ])
        
        prompt = f"""
        Create a YouTube video description that naturally incorporates affiliate links for the following products.
        The video is about: {topic}
        
        Products to promote:
        {product_info}
        
        The description should:
        1. Start with an engaging introduction about the video content
        2. Naturally mention the products in context
        3. Include a clear call-to-action to check out the products
        4. Include proper affiliate disclosure
        5. End with channel-related calls to action (subscribe, etc.)
        
        Also create a title that is engaging but doesn't sound like an advertisement.
        
        Format your response as a JSON object with 'title' and 'description' fields.
        """
        
        try:
            response = self.openai_generator.generate_structured_content(
                prompt, 
                system_message,
                output_structure={
                    "title": "Video Title",
                    "description": "Video description with affiliate links"
                }
            )
            
            if not response:
                return None
                
            # Add affiliate disclosure if not present
            description = response.get("description", "")
            if "affiliate" not in description.lower():
                description += "\n\n[This description contains affiliate links. As an affiliate, I earn from qualifying purchases.]"
                response["description"] = description
                
            # Add product links section
            product_links = "\n\n📌 Products mentioned:\n" + "\n".join([
                f"• {p['name']} - {p['affiliate_link']}" for p in products
            ])
            
            response["description"] += product_links
            response["products"] = products
            
            return response
        except Exception as e:
            print(f"Error generating YouTube affiliate content: {e}")
            return None
            
    def generate_twitter_affiliate_content(self, topic, products):
        """
        Generate Twitter/X post with affiliate links
        
        Args:
            topic (str): The content topic
            products (list): List of product dictionaries
            
        Returns:
            dict: Generated content with affiliate links
        """
        system_message = "You are a social media marketer who creates engaging posts with affiliate links."
        
        product_info = "\n".join([
            f"Product: {p['name']}\nDescription: {p['description']}\nPrice: {p['price']}\nLink: {p['affiliate_link']}"
            for p in products
        ])
        
        prompt = f"""
        Create a Twitter/X post about {topic} that naturally incorporates an affiliate link.
        
        Products to promote:
        {product_info}
        
        The post should:
        1. Be engaging and relevant to the topic
        2. Naturally mention the product
        3. Include a clear call-to-action
        4. Include a brief affiliate disclosure
        5. Be under 280 characters (Twitter's limit)
        
        Format your response as a JSON object with a 'post' field containing the tweet text.
        """
        
        try:
            response = self.openai_generator.generate_structured_content(
                prompt, 
                system_message,
                output_structure={
                    "post": "Twitter post with affiliate link"
                }
            )
            
            if not response:
                return None
                
            # Add affiliate disclosure if not present
            post = response.get("post", "")
            if "affiliate" not in post.lower() and "#ad" not in post.lower():
                # Try to add a minimal disclosure
                if len(post) <= 275:
                    post += " #ad"
                    
            response["post"] = post
            response["products"] = products
            
            return response
        except Exception as e:
            print(f"Error generating Twitter affiliate content: {e}")
            return None
            
    def generate_threads_affiliate_content(self, topic, products):
        """
        Generate Threads post with affiliate links
        
        Args:
            topic (str): The content topic
            products (list): List of product dictionaries
            
        Returns:
            dict: Generated content with affiliate links
        """
        system_message = "You are a social media marketer who creates engaging posts with affiliate links."
        
        product_info = "\n".join([
            f"Product: {p['name']}\nDescription: {p['description']}\nPrice: {p['price']}\nLink: {p['affiliate_link']}"
            for p in products
        ])
        
        prompt = f"""
        Create a Threads post about {topic} that naturally incorporates an affiliate link.
        
        Products to promote:
        {product_info}
        
        The post should:
        1. Be engaging and relevant to the topic
        2. Naturally mention the product
        3. Include a clear call-to-action
        4. Include a brief affiliate disclosure
        5. Be under 500 characters (Threads' limit)
        
        Format your response as a JSON object with a 'post' field containing the Threads post text.
        """
        
        try:
            response = self.openai_generator.generate_structured_content(
                prompt, 
                system_message,
                output_structure={
                    "post": "Threads post with affiliate link"
                }
            )
            
            if not response:
                return None
                
            # Add affiliate disclosure if not present
            post = response.get("post", "")
            if "affiliate" not in post.lower() and "#ad" not in post.lower():
                # Try to add a disclosure
                if len(post) <= 480:
                    post += "\n\n#ad #affiliate"
                    
            response["post"] = post
            response["products"] = products
            
            return response
        except Exception as e:
            print(f"Error generating Threads affiliate content: {e}")
            return None
