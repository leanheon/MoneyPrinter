import os
import json
import random
import time
from datetime import datetime
from src.openai_generator import OpenAIGenerator
from src.constants import ROOT_DIR

class AutomatedAffiliateSystem:
    """
    Automated system for generating affiliate marketing content and tracking conversions.
    Automatically researches products, creates content, and optimizes for conversions.
    """
    def __init__(self):
        """
        Initialize the AutomatedAffiliateSystem.
        """
        self.openai_generator = OpenAIGenerator()
        self.output_dir = os.path.join(ROOT_DIR, ".mp", "affiliate")
        self.data_file = os.path.join(self.output_dir, "affiliate_data.json")
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Load existing data if available
        self.affiliate_data = self._load_data()
        
    def _load_data(self):
        """
        Load affiliate data from file.
        
        Returns:
            dict: Affiliate data
        """
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading affiliate data: {e}")
                
        # Default structure if file doesn't exist or can't be loaded
        return {
            "networks": [],
            "products": [],
            "campaigns": [],
            "performance": {
                "clicks": 0,
                "conversions": 0,
                "revenue": 0.0
            },
            "last_updated": datetime.now().isoformat()
        }
    
    def _save_data(self):
        """
        Save affiliate data to file.
        """
        try:
            self.affiliate_data["last_updated"] = datetime.now().isoformat()
            
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.affiliate_data, f, indent=2)
                
        except Exception as e:
            print(f"Error saving affiliate data: {e}")
    
    def add_affiliate_network(self, name, api_key=None, base_url=None, commission_rate=None):
        """
        Add an affiliate network.
        
        Args:
            name (str): Name of the affiliate network
            api_key (str): API key for the network
            base_url (str): Base URL for API calls
            commission_rate (float): Default commission rate
            
        Returns:
            dict: Added network data
        """
        network = {
            "id": f"network_{len(self.affiliate_data['networks']) + 1}",
            "name": name,
            "api_key": api_key,
            "base_url": base_url,
            "commission_rate": commission_rate or 0.1,  # 10% default
            "date_added": datetime.now().isoformat()
        }
        
        self.affiliate_data["networks"].append(network)
        self._save_data()
        
        return network
    
    def add_product(self, name, description, price, affiliate_link, network_id=None, commission_rate=None, category=None):
        """
        Add a product for affiliate marketing.
        
        Args:
            name (str): Product name
            description (str): Product description
            price (float): Product price
            affiliate_link (str): Affiliate link for the product
            network_id (str): ID of the affiliate network
            commission_rate (float): Commission rate for this product
            category (str): Product category
            
        Returns:
            dict: Added product data
        """
        # Find network if provided
        network = None
        if network_id:
            for n in self.affiliate_data["networks"]:
                if n["id"] == network_id:
                    network = n
                    break
        
        # Use network commission rate if not specified
        if commission_rate is None and network:
            commission_rate = network.get("commission_rate", 0.1)
        elif commission_rate is None:
            commission_rate = 0.1  # 10% default
        
        product = {
            "id": f"product_{len(self.affiliate_data['products']) + 1}",
            "name": name,
            "description": description,
            "price": price,
            "affiliate_link": affiliate_link,
            "network_id": network_id,
            "commission_rate": commission_rate,
            "category": category or "General",
            "date_added": datetime.now().isoformat(),
            "performance": {
                "clicks": 0,
                "conversions": 0,
                "revenue": 0.0
            }
        }
        
        self.affiliate_data["products"].append(product)
        self._save_data()
        
        return product
    
    def research_products(self, niche, count=5):
        """
        Research products in a specific niche for affiliate marketing.
        
        Args:
            niche (str): The niche to research
            count (int): Number of products to research
            
        Returns:
            list: Researched product suggestions
        """
        system_message = "You are an expert affiliate marketer who researches profitable products."
        
        output_structure = {
            "products": [
                {
                    "name": "Product name",
                    "description": "Product description",
                    "estimated_price": 0.0,
                    "potential_commission": 0.0,
                    "target_audience": "Target audience",
                    "selling_points": ["Selling point 1", "Selling point 2"],
                    "affiliate_programs": ["Program 1", "Program 2"]
                }
            ]
        }
        
        prompt = f"""
        Research {count} profitable products in the {niche} niche for affiliate marketing.
        
        For each product:
        1. Provide a product name and brief description
        2. Estimate the price range
        3. Suggest potential commission rates
        4. Identify the target audience
        5. List key selling points
        6. Suggest affiliate programs or networks where this product might be available
        
        Focus on products with:
        - High commission rates
        - Good conversion potential
        - Recurring commissions when possible
        - Established reputation
        
        Format your response as a JSON object with an array of products.
        """
        
        try:
            response = self.openai_generator.generate_structured_content(
                prompt, 
                system_message,
                output_structure=output_structure
            )
            
            if response and "products" in response:
                return response["products"]
            else:
                return []
                
        except Exception as e:
            print(f"Error researching products: {e}")
            return []
    
    def create_affiliate_campaign(self, product_id, platform, content_type):
        """
        Create an affiliate marketing campaign for a specific product.
        
        Args:
            product_id (str): ID of the product
            platform (str): Platform for the campaign (blog, youtube, social)
            content_type (str): Type of content (review, comparison, tutorial)
            
        Returns:
            dict: Created campaign data
        """
        # Find the product
        product = None
        for p in self.affiliate_data["products"]:
            if p["id"] == product_id:
                product = p
                break
                
        if not product:
            raise ValueError(f"Product not found with ID: {product_id}")
        
        # Generate campaign content
        content = self._generate_campaign_content(product, platform, content_type)
        
        campaign = {
            "id": f"campaign_{len(self.affiliate_data['campaigns']) + 1}",
            "product_id": product_id,
            "platform": platform,
            "content_type": content_type,
            "content": content,
            "status": "active",
            "date_created": datetime.now().isoformat(),
            "performance": {
                "clicks": 0,
                "conversions": 0,
                "revenue": 0.0
            }
        }
        
        self.affiliate_data["campaigns"].append(campaign)
        self._save_data()
        
        return campaign
    
    def _generate_campaign_content(self, product, platform, content_type):
        """
        Generate content for an affiliate campaign.
        
        Args:
            product (dict): Product data
            platform (str): Platform for the campaign
            content_type (str): Type of content
            
        Returns:
            dict: Generated content
        """
        system_message = "You are an expert affiliate marketer who creates high-converting content."
        
        # Adjust prompt based on platform and content type
        if platform == "blog":
            if content_type == "review":
                prompt = f"""
                Create a comprehensive product review blog post for:
                
                Product: {product['name']}
                Description: {product['description']}
                Price: ${product['price']}
                
                The blog post should:
                - Have an attention-grabbing title
                - Include an introduction that hooks the reader
                - Discuss the key features and benefits
                - Include pros and cons
                - Provide personal experiences (hypothetical)
                - Include a strong call-to-action with the affiliate link
                - Be between 1000-1500 words
                
                Make the content persuasive but authentic, focusing on how the product solves problems.
                """
            elif content_type == "comparison":
                prompt = f"""
                Create a product comparison blog post featuring:
                
                Main Product: {product['name']}
                Description: {product['description']}
                Price: ${product['price']}
                
                Compare it with 2-3 similar products in the market. For each comparison:
                - Highlight where {product['name']} excels
                - Be fair about areas where competitors might be better
                - Create a comparison table of features
                - Conclude with a recommendation for {product['name']} with justification
                - Include a strong call-to-action with the affiliate link
                
                The post should be 1200-1800 words and position {product['name']} as the best choice for most readers.
                """
            else:  # tutorial
                prompt = f"""
                Create a tutorial blog post that features:
                
                Product: {product['name']}
                Description: {product['description']}
                Price: ${product['price']}
                
                The tutorial should:
                - Solve a specific problem that {product['name']} addresses
                - Include step-by-step instructions with clear headings
                - Highlight how {product['name']} makes the process easier
                - Include tips and best practices
                - Naturally incorporate the product throughout the tutorial
                - End with a summary of benefits and a call-to-action
                
                The post should be 1500-2000 words and demonstrate the value of the product through practical application.
                """
        elif platform == "youtube":
            if content_type == "review":
                prompt = f"""
                Create a YouTube video script for a product review of:
                
                Product: {product['name']}
                Description: {product['description']}
                Price: ${product['price']}
                
                The script should include:
                - An engaging introduction (30 seconds)
                - Overview of what will be covered (15 seconds)
                - Product unboxing/overview section (1-2 minutes)
                - Key features and benefits (2-3 minutes)
                - Demonstration of the product in use (2-3 minutes)
                - Pros and cons (1-2 minutes)
                - Final verdict and recommendation (1 minute)
                - Call-to-action with affiliate link mention (30 seconds)
                
                Format the script with timestamps and include notes for visuals/b-roll suggestions.
                """
            elif content_type == "comparison":
                prompt = f"""
                Create a YouTube video script comparing:
                
                Main Product: {product['name']}
                Description: {product['description']}
                Price: ${product['price']}
                
                With 2-3 competitor products. The script should include:
                - Introduction explaining the comparison criteria (30 seconds)
                - Brief overview of all products being compared (1 minute)
                - Side-by-side comparison of key features (3-4 minutes)
                - Price comparison and value analysis (1 minute)
                - Performance tests or demonstrations (2-3 minutes)
                - Pros and cons of each (1-2 minutes)
                - Final recommendation favoring {product['name']} (1 minute)
                - Call-to-action with affiliate link mention (30 seconds)
                
                Format the script with timestamps and include notes for comparison visuals.
                """
            else:  # tutorial
                prompt = f"""
                Create a YouTube tutorial video script featuring:
                
                Product: {product['name']}
                Description: {product['description']}
                Price: ${product['price']}
                
                The script should include:
                - Introduction to the problem being solved (30 seconds)
                - Brief mention of {product['name']} as the solution (30 seconds)
                - Required materials/setup (30 seconds)
                - Step-by-step instructions using the product (4-5 minutes)
                - Tips and tricks for best results (1-2 minutes)
                - Showcase of final results (1 minute)
                - Summary of how {product['name']} made the process better (1 minute)
                - Call-to-action with affiliate link mention (30 seconds)
                
                Format the script with timestamps and include notes for demonstration shots.
                """
        else:  # social
            if content_type == "review":
                prompt = f"""
                Create a series of 5 social media posts reviewing:
                
                Product: {product['name']}
                Description: {product['description']}
                Price: ${product['price']}
                
                Each post should:
                - Be under 280 characters (for Twitter compatibility)
                - Focus on a different aspect of the product
                - Include relevant hashtags
                - Be engaging and shareable
                - Include a call-to-action where appropriate
                
                Also include 2 longer posts (under 2200 characters) for platforms like Instagram or Facebook that go into more detail.
                """
            elif content_type == "comparison":
                prompt = f"""
                Create a series of 5 social media posts comparing:
                
                Main Product: {product['name']}
                Description: {product['description']}
                Price: ${product['price']}
                
                With its competitors. Each post should:
                - Be under 280 characters (for Twitter compatibility)
                - Focus on a different comparison point
                - Position {product['name']} favorably
                - Include relevant hashtags
                - Include a call-to-action where appropriate
                
                Also include 2 longer posts (under 2200 characters) for platforms like Instagram or Facebook that provide more detailed comparisons.
                """
            else:  # tutorial
                prompt = f"""
                Create a series of 5 social media posts showing a tutorial using:
                
                Product: {product['name']}
                Description: {product['description']}
                Price: ${product['price']}
                
                Each post should:
                - Be under 280 characters (for Twitter compatibility)
                - Represent one step in the tutorial process
                - Highlight how {product['name']} helps
                - Include relevant hashtags
                - Build on the previous post
                
                Also include 2 longer posts (under 2200 characters) for platforms like Instagram or Facebook that provide the complete tutorial in a single post.
                """
        
        content = self.openai_generator.generate_content(prompt, system_message, max_tokens=2000)
        
        # Generate title
        title_prompt = f"""
        Create an attention-grabbing, SEO-friendly title for a {content_type} about {product['name']} on {platform}.
        The title should be compelling, include keywords, and encourage clicks.
        Keep it under 60 characters if possible.
        Just provide the title with no additional explanation.
        """
        
        title = self.openai_generator.generate_content(title_prompt, system_message, max_tokens=100)
        
        return {
            "title": title.strip() if title else f"{content_type.capitalize()} of {product['name']}",
            "body": content.strip() if content else f"Content about {product['name']}",
            "platform": platform,
            "content_type": content_type
        }
    
    def generate_tracking_link(self, campaign_id):
        """
        Generate a tracking link for an affiliate campaign.
        
        Args:
            campaign_id (str): ID of the campaign
            
        Returns:
            str: Tracking link
        """
        # Find the campaign
        campaign = None
        for c in self.affiliate_data["campaigns"]:
            if c["id"] == campaign_id:
                campaign = c
                break
                
        if not campaign:
            raise ValueError(f"Campaign not found with ID: {campaign_id}")
        
        # Find the product
        product = None
        for p in self.affiliate_data["products"]:
            if p["id"] == campaign["product_id"]:
                product = p
                break
                
        if not product:
            raise ValueError(f"Product not found with ID: {campaign['product_id']}")
        
        # Generate a tracking link by adding campaign parameters
        base_link = product["affiliate_link"]
        tracking_params = f"utm_source=moneyprinter&utm_medium={campaign['platform']}&utm_campaign={campaign['id']}"
        
        if "?" in base_link:
            tracking_link = f"{base_link}&{tracking_params}"
        else:
            tracking_link = f"{base_link}?{tracking_params}"
            
        return tracking_link
    
    def simulate_campaign_performance(self, campaign_id, days=30):
        """
        Simulate performance for an affiliate campaign.
        
        Args:
            campaign_id (str): ID of the campaign
            days (int): Number of days to simulate
            
        Returns:
            dict: Simulated performance data
        """
        # Find the campaign
        campaign = None
        for i, c in enumerate(self.affiliate_data["campaigns"]):
            if c["id"] == campaign_id:
                campaign = c
                campaign_index = i
                break
                
        if not campaign:
            raise ValueError(f"Campaign not found with ID: {campaign_id}")
        
        # Find the product
        product = None
        for i, p in enumerate(self.affiliate_data["products"]):
            if p["id"] == campaign["product_id"]:
                product = p
                product_index = i
                break
                
        if not product:
            raise ValueError(f"Product not found with ID: {campaign['product_id']}")
        
        # Simulate performance based on platform and content type
        base_clicks = 0
        base_conversion_rate = 0
        
        if campaign["platform"] == "blog":
            if campaign["content_type"] == "review":
                base_clicks = random.randint(100, 500)
                base_conversion_rate = random.uniform(0.02, 0.05)  # 2-5%
            elif campaign["content_type"] == "comparison":
                base_clicks = random.randint(200, 700)
                base_conversion_rate = random.uniform(0.03, 0.06)  # 3-6%
            else:  # tutorial
                base_clicks = random.randint(150, 600)
                base_conversion_rate = random.uniform(0.01, 0.04)  # 1-4%
        elif campaign["platform"] == "youtube":
            if campaign["content_type"] == "review":
                base_clicks = random.randint(300, 1000)
                base_conversion_rate = random.uniform(0.01, 0.03)  # 1-3%
            elif campaign["content_type"] == "comparison":
                base_clicks = random.randint(400, 1200)
                base_conversion_rate = random.uniform(0.02, 0.04)  # 2-4%
            else:  # tutorial
                base_clicks = random.randint(500, 1500)
                base_conversion_rate = random.uniform(0.01, 0.03)  # 1-3%
        else:  # social
            if campaign["content_type"] == "review":
                base_clicks = random.randint(50, 300)
                base_conversion_rate = random.uniform(0.01, 0.02)  # 1-2%
            elif campaign["content_type"] == "comparison":
                base_clicks = random.randint(75, 350)
                base_conversion_rate = random.uniform(0.01, 0.03)  # 1-3%
            else:  # tutorial
                base_clicks = random.randint(100, 400)
                base_conversion_rate = random.uniform(0.005, 0.02)  # 0.5-2%
        
        # Adjust for number of days
        clicks = int(base_clicks * (days / 30))
        conversions = int(clicks * base_conversion_rate)
        revenue = conversions * product["price"] * product["commission_rate"]
        
        # Update campaign performance
        self.affiliate_data["campaigns"][campaign_index]["performance"] = {
            "clicks": clicks,
            "conversions": conversions,
            "revenue": revenue
        }
        
        # Update product performance
        self.affiliate_data["products"][product_index]["performance"]["clicks"] += clicks
        self.affiliate_data["products"][product_index]["performance"]["conversions"] += conversions
        self.affiliate_data["products"][product_index]["performance"]["revenue"] += revenue
        
        # Update overall performance
        self.affiliate_data["performance"]["clicks"] += clicks
        self.affiliate_data["performance"]["conversions"] += conversions
        self.affiliate_data["performance"]["revenue"] += revenue
        
        self._save_data()
        
        return {
            "campaign_id": campaign_id,
            "days": days,
            "clicks": clicks,
            "conversions": conversions,
            "revenue": revenue,
            "conversion_rate": conversions / clicks if clicks > 0 else 0
        }
    
    def get_top_performing_campaigns(self, metric="revenue", limit=5):
        """
        Get top performing campaigns based on a metric.
        
        Args:
            metric (str): Metric to sort by (revenue, conversions, clicks)
            limit (int): Number of campaigns to return
            
        Returns:
            list: Top performing campaigns
        """
        sorted_campaigns = sorted(
            self.affiliate_data["campaigns"],
            key=lambda c: c["performance"].get(metric, 0),
            reverse=True
        )
        
        return sorted_campaigns[:limit]
    
    def get_top_performing_products(self, metric="revenue", limit=5):
        """
        Get top performing products based on a metric.
        
        Args:
            metric (str): Metric to sort by (revenue, conversions, clicks)
            limit (int): Number of products to return
            
        Returns:
            list: Top performing products
        """
        sorted_products = sorted(
            self.affiliate_data["products"],
            key=lambda p: p["performance"].get(metric, 0),
            reverse=True
        )
        
        return sorted_products[:limit]
    
    def get_performance_summary(self):
        """
        Get overall performance summary.
        
        Returns:
            dict: Performance summary
        """
        return {
            "total_campaigns": len(self.affiliate_data["campaigns"]),
            "total_products": len(self.affiliate_data["products"]),
            "total_clicks": self.affiliate_data["performance"]["clicks"],
            "total_conversions": self.affiliate_data["performance"]["conversions"],
            "total_revenue": self.affiliate_data["performance"]["revenue"],
            "conversion_rate": self.affiliate_data["performance"]["conversions"] / self.affiliate_data["performance"]["clicks"] 
                if self.affiliate_data["performance"]["clicks"] > 0 else 0
        }
    
    def optimize_campaign(self, campaign_id):
        """
        Optimize an existing affiliate campaign based on performance.
        
        Args:
            campaign_id (str): ID of the campaign
            
        Returns:
            dict: Optimized campaign data
        """
        # Find the campaign
        campaign = None
        for i, c in enumerate(self.affiliate_data["campaigns"]):
            if c["id"] == campaign_id:
                campaign = c
                campaign_index = i
                break
                
        if not campaign:
            raise ValueError(f"Campaign not found with ID: {campaign_id}")
        
        # Find the product
        product = None
        for p in self.affiliate_data["products"]:
            if p["id"] == campaign["product_id"]:
                product = p
                break
                
        if not product:
            raise ValueError(f"Product not found with ID: {campaign['product_id']}")
        
        # Generate optimization suggestions
        system_message = "You are an expert affiliate marketer who optimizes campaigns for maximum conversions."
        
        performance = campaign["performance"]
        conversion_rate = performance["conversions"] / performance["clicks"] if performance["clicks"] > 0 else 0
        
        prompt = f"""
        Optimize an affiliate marketing campaign with the following details:
        
        Product: {product['name']}
        Description: {product['description']}
        Price: ${product['price']}
        Platform: {campaign['platform']}
        Content Type: {campaign['content_type']}
        
        Current Performance:
        - Clicks: {performance['clicks']}
        - Conversions: {performance['conversions']}
        - Revenue: ${performance['revenue']:.2f}
        - Conversion Rate: {conversion_rate:.2%}
        
        Provide specific optimization suggestions to improve:
        1. Click-through rate
        2. Conversion rate
        3. Average order value
        
        For each suggestion:
        - Explain the rationale
        - Provide specific implementation steps
        - Estimate the potential impact
        
        Also suggest A/B testing ideas to validate the optimizations.
        """
        
        optimization_suggestions = self.openai_generator.generate_content(prompt, system_message, max_tokens=1000)
        
        # Generate optimized content
        optimized_content = self._generate_campaign_content(product, campaign["platform"], campaign["content_type"])
        
        # Update the campaign with optimized content
        self.affiliate_data["campaigns"][campaign_index]["content"] = optimized_content
        self.affiliate_data["campaigns"][campaign_index]["optimization_suggestions"] = optimization_suggestions.strip() if optimization_suggestions else ""
        self.affiliate_data["campaigns"][campaign_index]["last_optimized"] = datetime.now().isoformat()
        
        self._save_data()
        
        return {
            "campaign_id": campaign_id,
            "optimized_content": optimized_content,
            "optimization_suggestions": optimization_suggestions.strip() if optimization_suggestions else "",
            "last_optimized": self.affiliate_data["campaigns"][campaign_index]["last_optimized"]
        }
