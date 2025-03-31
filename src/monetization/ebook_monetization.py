import os
import json
import requests
from uuid import uuid4
from src.config import get_config
from src.constants import ROOT_DIR
from src.openai_generator import OpenAIGenerator
from src.ebook_generator import EbookGenerator

class EbookMonetizationManager:
    """
    Class for managing ebook monetization strategies including sales, 
    affiliate marketing, and subscription models
    """
    def __init__(self):
        """
        Initialize the EbookMonetizationManager with configuration settings
        """
        config = get_config()
        self.monetization_config = config.get("monetization", {})
        self.openai_generator = OpenAIGenerator()
        self.ebook_generator = EbookGenerator()
        
        # Create ebook monetization directory if it doesn't exist
        self.ebook_monetization_dir = os.path.join(ROOT_DIR, ".mp", "ebook_monetization")
        os.makedirs(self.ebook_monetization_dir, exist_ok=True)
        
        # Load ebook monetization data
        self.ebook_products = self._load_ebook_products()
        self.sales_data = self._load_sales_data()
        self.platforms = self._load_platforms()
        
    def _load_ebook_products(self):
        """
        Load ebook products from file or create default
        
        Returns:
            dict: Dictionary of ebook products
        """
        products_file = os.path.join(self.ebook_monetization_dir, "products.json")
        
        if os.path.exists(products_file):
            with open(products_file, 'r') as f:
                return json.load(f)
        else:
            # Create default empty products dictionary
            default_products = {}
            
            # Save default products
            with open(products_file, 'w') as f:
                json.dump(default_products, f, indent=2)
                
            return default_products
            
    def _load_sales_data(self):
        """
        Load sales data from file or create default
        
        Returns:
            dict: Dictionary of sales data
        """
        sales_file = os.path.join(self.ebook_monetization_dir, "sales.json")
        
        if os.path.exists(sales_file):
            with open(sales_file, 'r') as f:
                return json.load(f)
        else:
            # Create default empty sales data
            default_sales = {
                "total_revenue": 0,
                "total_sales": 0,
                "sales_by_product": {},
                "sales_by_platform": {},
                "monthly_sales": {}
            }
            
            # Save default sales data
            with open(sales_file, 'w') as f:
                json.dump(default_sales, f, indent=2)
                
            return default_sales
            
    def _load_platforms(self):
        """
        Load platform data from file or create default
        
        Returns:
            dict: Dictionary of platform data
        """
        platforms_file = os.path.join(self.ebook_monetization_dir, "platforms.json")
        
        if os.path.exists(platforms_file):
            with open(platforms_file, 'r') as f:
                return json.load(f)
        else:
            # Create default platforms
            default_platforms = {
                "amazon_kdp": {
                    "name": "Amazon Kindle Direct Publishing",
                    "url": "https://kdp.amazon.com",
                    "royalty_rate": "35-70%",
                    "file_formats": ["mobi", "epub"],
                    "enabled": True
                },
                "gumroad": {
                    "name": "Gumroad",
                    "url": "https://gumroad.com",
                    "royalty_rate": "91-94%",
                    "file_formats": ["pdf", "epub", "mobi"],
                    "enabled": True
                },
                "payhip": {
                    "name": "Payhip",
                    "url": "https://payhip.com",
                    "royalty_rate": "95%",
                    "file_formats": ["pdf", "epub", "mobi"],
                    "enabled": True
                }
            }
            
            # Save default platforms
            with open(platforms_file, 'w') as f:
                json.dump(default_platforms, f, indent=2)
                
            return default_platforms
            
    def create_ebook_product(self, topic, title=None, price=9.99, format="pdf", length="medium", chapters=5):
        """
        Create a new ebook product for monetization
        
        Args:
            topic (str): The main topic for the ebook
            title (str, optional): Custom title for the ebook
            price (float): Price for the ebook
            format (str): Output format (pdf, epub, mobi)
            length (str): Length of the ebook (short, medium, long)
            chapters (int): Number of chapters
            
        Returns:
            dict: Created ebook product data
        """
        # Generate the ebook
        ebook = self.ebook_generator.generate_ebook(topic, format, length, chapters)
        
        if not ebook:
            return None
            
        # Use provided title or generated title
        if title:
            ebook["title"] = title
            
        # Compile the ebook
        compiled_files = self.ebook_generator.compile_ebook(ebook)
        
        if not compiled_files:
            return None
            
        # Create a unique product ID
        product_id = f"ebook_{uuid4().hex[:8]}"
        
        # Create the product entry
        product = {
            "product_id": product_id,
            "title": ebook["title"],
            "topic": topic,
            "description": ebook.get("description", f"A comprehensive guide about {topic}"),
            "price": price,
            "format": format,
            "length": length,
            "word_count": ebook["word_count"],
            "chapters": len(ebook["chapters"]),
            "cover_path": ebook.get("cover_path"),
            "files": compiled_files,
            "created_date": ebook["date"],
            "platforms": {},
            "sales_count": 0,
            "revenue": 0.0
        }
        
        # Save the product
        self.ebook_products[product_id] = product
        
        # Save updated products
        products_file = os.path.join(self.ebook_monetization_dir, "products.json")
        with open(products_file, 'w') as f:
            json.dump(self.ebook_products, f, indent=2)
            
        return product
        
    def publish_to_platform(self, product_id, platform_id):
        """
        Publish an ebook to a specific platform
        
        Args:
            product_id (str): ID of the ebook product
            platform_id (str): ID of the platform
            
        Returns:
            dict: Publishing result data
        """
        if product_id not in self.ebook_products:
            print(f"Product {product_id} not found")
            return None
            
        if platform_id not in self.platforms:
            print(f"Platform {platform_id} not found")
            return None
            
        product = self.ebook_products[product_id]
        platform = self.platforms[platform_id]
        
        # Check if the product format is supported by the platform
        if product["format"] not in platform["file_formats"]:
            print(f"Format {product['format']} not supported by {platform['name']}")
            return None
            
        # Simulate publishing to platform
        # In a real implementation, this would use the platform's API
        
        print(f"Publishing '{product['title']}' to {platform['name']}")
        print(f"Format: {product['format']}, Price: ${product['price']}")
        
        # Generate a mock platform URL
        platform_url = f"{platform['url']}/ebook/{product_id}"
        
        # Update the product with platform data
        product["platforms"][platform_id] = {
            "url": platform_url,
            "published_date": self.ebook_generator.openai_generator._get_current_datetime(),
            "status": "active"
        }
        
        # Save updated products
        products_file = os.path.join(self.ebook_monetization_dir, "products.json")
        with open(products_file, 'w') as f:
            json.dump(self.ebook_products, f, indent=2)
            
        return {
            "success": True,
            "product_id": product_id,
            "platform_id": platform_id,
            "platform_name": platform["name"],
            "url": platform_url,
            "published_date": product["platforms"][platform_id]["published_date"]
        }
        
    def generate_sales_page(self, product_id):
        """
        Generate a sales page for an ebook product
        
        Args:
            product_id (str): ID of the ebook product
            
        Returns:
            dict: Sales page data
        """
        if product_id not in self.ebook_products:
            print(f"Product {product_id} not found")
            return None
            
        product = self.ebook_products[product_id]
        
        system_message = "You are a professional copywriter who specializes in creating high-converting sales pages for ebooks."
        
        prompt = f"""
        Create a compelling sales page for the following ebook:
        
        Title: {product['title']}
        Topic: {product['topic']}
        Description: {product['description']}
        Price: ${product['price']}
        Format: {product['format'].upper()}
        Length: {product['word_count']} words, {product['chapters']} chapters
        
        The sales page should include:
        1. A compelling headline
        2. An engaging introduction that hooks the reader
        3. 3-5 bullet points highlighting the key benefits
        4. A clear description of what the reader will learn
        5. A section addressing potential objections
        6. A strong call-to-action
        7. A money-back guarantee
        
        Format your response as HTML that can be used directly on a sales page.
        Include appropriate sections, headings, and formatting.
        """
        
        sales_page_html = self.openai_generator.generate_content(prompt, system_message, max_tokens=2000)
        
        if not sales_page_html:
            return None
            
        # Save the sales page
        safe_title = product["title"].lower().replace(' ', '_').replace('?', '').replace('!', '').replace(',', '').replace('.', '')
        sales_page_path = os.path.join(self.ebook_monetization_dir, f"{safe_title}_sales_page.html")
        
        with open(sales_page_path, "w", encoding="utf-8") as f:
            f.write(f"<!DOCTYPE html>\n<html>\n<head>\n<title>{product['title']} - Sales Page</title>\n")
            f.write("<meta charset=\"utf-8\">\n")
            f.write("<style>body{font-family:Arial,sans-serif; line-height:1.6; max-width:800px; margin:0 auto; padding:20px;}</style>\n")
            f.write("</head>\n<body>\n")
            f.write(sales_page_html)
            f.write("\n</body>\n</html>")
            
        return {
            "product_id": product_id,
            "sales_page_path": sales_page_path,
            "html": sales_page_html
        }
        
    def generate_email_sequence(self, product_id, num_emails=5):
        """
        Generate an email marketing sequence for an ebook product
        
        Args:
            product_id (str): ID of the ebook product
            num_emails (int): Number of emails in the sequence
            
        Returns:
            dict: Email sequence data
        """
        if product_id not in self.ebook_products:
            print(f"Product {product_id} not found")
            return None
            
        product = self.ebook_products[product_id]
        
        system_message = "You are an email marketing specialist who creates high-converting email sequences for digital products."
        
        prompt = f"""
        Create a {num_emails}-email marketing sequence to promote the following ebook:
        
        Title: {product['title']}
        Topic: {product['topic']}
        Description: {product['description']}
        Price: ${product['price']}
        
        The email sequence should include:
        1. An initial value-providing email that introduces the problem
        2. Follow-up emails that provide value while hinting at the solution
        3. A direct sales email with clear call-to-action
        4. A final reminder email with urgency/scarcity
        
        For each email, provide:
        - Subject line
        - Email body (with appropriate formatting)
        - Call-to-action
        
        Format your response as a JSON array where each object contains subject, body, and cta fields.
        """
        
        email_sequence = self.openai_generator.generate_structured_content(
            prompt, 
            system_message,
            output_structure=[{
                "subject": "Email subject line",
                "body": "Email body text",
                "cta": "Call to action text"
            }]
        )
        
        if not email_sequence or not isinstance(email_sequence, list):
            return None
            
        # Save the email sequence
        safe_title = product["title"].lower().replace(' ', '_').replace('?', '').replace('!', '').replace(',', '').replace('.', '')
        sequence_dir = os.path.join(self.ebook_monetization_dir, f"{safe_title}_email_sequence")
        os.makedirs(sequence_dir, exist_ok=True)
        
        # Save each email as a separate file
        email_files = []
        for i, email in enumerate(email_sequence):
            email_path = os.path.join(sequence_dir, f"email_{i+1}.html")
            
            with open(email_path, "w", encoding="utf-8") as f:
                f.write(f"<!DOCTYPE html>\n<html>\n<head>\n<title>{email['subject']}</title>\n")
                f.write("<meta charset=\"utf-8\">\n")
                f.write("<style>body{font-family:Arial,sans-serif; line-height:1.6; max-width:600px; margin:0 auto; padding:20px;}</style>\n")
                f.write("</head>\n<body>\n")
                f.write(f"<h2>{email['subject']}</h2>\n")
                f.write(f"<div>{email['body']}</div>\n")
                f.write(f"<div style=\"margin-top:20px; font-weight:bold;\">{email['cta']}</div>\n")
                f.write("\n</body>\n</html>")
                
            email_files.append(email_path)
            
        # Save the sequence metadata
        sequence_meta = {
            "product_id": product_id,
            "num_emails": len(email_sequence),
            "emails": email_sequence,
            "email_files": email_files
        }
        
        sequence_meta_path = os.path.join(sequence_dir, "sequence_meta.json")
        with open(sequence_meta_path, "w", encoding="utf-8") as f:
            json.dump(sequence_meta, f, indent=2)
            
        return sequence_meta
        
    def generate_social_promotion(self, product_id, platform):
        """
        Generate social media promotion content for an ebook
        
        Args:
            product_id (str): ID of the ebook product
            platform (str): Social media platform (twitter, instagram, facebook)
            
        Returns:
            dict: Social promotion content
        """
        if product_id not in self.ebook_products:
            print(f"Product {product_id} not found")
            return None
            
        product = self.ebook_products[product_id]
        
        system_message = "You are a social media marketer who specializes in promoting digital products."
        
        # Adjust content based on platform
        if platform.lower() == "twitter":
            max_length = 280
            prompt_specifics = "Keep the post under 280 characters. Include relevant hashtags."
        elif platform.lower() == "instagram":
            max_length = 2200
            prompt_specifics = "Create a longer post suitable for Instagram. Include a caption and relevant hashtags."
        elif platform.lower() == "facebook":
            max_length = 5000
            prompt_specifics = "Create a detailed post suitable for Facebook. Include engaging questions and a clear call-to-action."
        else:
            max_length = 1000
            prompt_specifics = "Create an engaging post suitable for social media. Include relevant hashtags."
            
        prompt = f"""
        Create a social media post promoting the following ebook:
        
        Title: {product['title']}
        Topic: {product['topic']}
        Description: {product['description']}
        Price: ${product['price']}
        
        The post should:
        1. Be attention-grabbing and engaging
        2. Highlight a key benefit or pain point the ebook addresses
        3. Include a clear call-to-action
        
        {prompt_specifics}
        
        Format your response as a JSON object with 'post' and 'hashtags' fields.
        """
        
        response = self.openai_generator.generate_structured_content(
            prompt, 
            system_message,
            output_structure={
                "post": "Social media post text",
                "hashtags": "Relevant hashtags"
            }
        )
        
        if not response:
            return None
            
        # Combine post and hashtags, ensuring we don't exceed platform limits
        post_text = response.get("post", "")
        hashtags = response.get("hashtags", "")
        
        # Ensure we don't exceed the platform's character limit
        if len(post_text) + len(hashtags) + 1 > max_length:
            # Truncate hashtags if needed
            available_space = max_length - len(post_text) - 1
            if available_space > 0:
                hashtags = hashtags[:available_space]
            else:
                # If no space for hashtags, truncate the post
                post_text = post_text[:max_length - 20] + "... "
                hashtags = "#ebook"
                
        combined_post = f"{post_text}\n\n{hashtags}"
        
        return {
            "product_id": product_id,
            "platform": platform,
            "post": post_text,
            "hashtags": hashtags,
            "combined_post": combined_post
        }
        
    def record_sale(self, product_id, platform_id=None, sale_price=None, date=None):
        """
        Record a sale of an ebook product
        
        Args:
            product_id (str): ID of the ebook product
            platform_id (str, optional): ID of the platform where the sale occurred
            sale_price (float, optional): Actual sale price (for discounts)
            date (str, optional): Date of the sale
            
        Returns:
            dict: Updated sales data
        """
        if product_id not in self.ebook_products:
            print(f"Product {product_id} not found")
            return None
            
        product = self.ebook_products[product_id]
        
        # Use provided values or defaults
        if not sale_price:
            sale_price = product["price"]
            
        if not date:
            date = self.ebook_generator.openai_generator._get_current_datetime()
            
        # Extract month for monthly tracking
        month = date.split(" ")[0].rsplit("-", 1)[0]  # Format: YYYY-MM
        
        # Update product sales data
        product["sales_count"] += 1
        product["revenue"] += sale_price
        
        # Update global sales data
        self.sales_data["total_sales"] += 1
        self.sales_data["total_revenue"] += sale_price
        
        # Update sales by product
        if product_id not in self.sales_data["sales_by_product"]:
            self.sales_data["sales_by_product"][product_id] = {
                "count": 0,
                "revenue": 0.0
            }
        self.sales_data["sales_by_product"][product_id]["count"] += 1
        self.sales_data["sales_by_product"][product_id]["revenue"] += sale_price
        
        # Update sales by platform
        if platform_id:
            if platform_id not in self.sales_data["sales_by_platform"]:
                self.sales_data["sales_by_platform"][platform_id] = {
                    "count": 0,
                    "revenue": 0.0
                }
            self.sales_data["sales_by_platform"][platform_id]["count"] += 1
            self.sales_data["sales_by_platform"][platform_id]["revenue"] += sale_price
            
        # Update monthly sales
        if month not in self.sales_data["monthly_sales"]:
            self.sales_data["monthly_sales"][month] = {
                "count": 0,
                "revenue": 0.0
            }
        self.sales_data["monthly_sales"][month]["count"] += 1
        self.sales_data["monthly_sales"][month]["revenue"] += sale_price
        
        # Save updated products
        products_file = os.path.join(self.ebook_monetization_dir, "products.json")
        with open(products_file, 'w') as f:
            json.dump(self.ebook_products, f, indent=2)
            
        # Save updated sales data
        sales_file = os.path.join(self.ebook_monetization_dir, "sales.json")
        with open(sales_file, 'w') as f:
            json.dump(self.sales_data, f, indent=2)
            
        return {
            "product_id": product_id,
            "platform_id": platform_id,
            "sale_price": sale_price,
            "date": date,
            "product_sales": product["sales_count"],
            "product_revenue": product["revenue"],
            "total_sales": self.sales_data["total_sales"],
            "total_revenue": self.sales_data["total_revenue"]
        }
        
    def get_sales_report(self, period="all", product_id=None, platform_id=None):
        """
        Generate a sales report for ebook products
        
        Args:
            period (str): Time period (all, monthly, yearly)
            product_id (str, optional): Filter by specific product
            platform_id (str, optional): Filter by specific platform
            
        Returns:
            dict: Sales report data
        """
        report = {
            "period": period,
            "total_sales": 0,
            "total_revenue": 0.0,
            "products": {},
            "platforms": {},
            "monthly_data": {}
        }
        
        # Filter by product if specified
        if product_id:
            if product_id in self.ebook_products:
                product = self.ebook_products[product_id]
                report["products"][product_id] = {
                    "title": product["title"],
                    "sales_count": product["sales_count"],
                    "revenue": product["revenue"]
                }
                report["total_sales"] = product["sales_count"]
                report["total_revenue"] = product["revenue"]
            return report
            
        # Filter by platform if specified
        if platform_id:
            if platform_id in self.sales_data["sales_by_platform"]:
                platform_sales = self.sales_data["sales_by_platform"][platform_id]
                report["platforms"][platform_id] = {
                    "name": self.platforms[platform_id]["name"] if platform_id in self.platforms else platform_id,
                    "sales_count": platform_sales["count"],
                    "revenue": platform_sales["revenue"]
                }
                report["total_sales"] = platform_sales["count"]
                report["total_revenue"] = platform_sales["revenue"]
            return report
            
        # No filters, return data based on period
        if period == "all":
            report["total_sales"] = self.sales_data["total_sales"]
            report["total_revenue"] = self.sales_data["total_revenue"]
            
            # Add product data
            for product_id, product_sales in self.sales_data["sales_by_product"].items():
                if product_id in self.ebook_products:
                    product = self.ebook_products[product_id]
                    report["products"][product_id] = {
                        "title": product["title"],
                        "sales_count": product_sales["count"],
                        "revenue": product_sales["revenue"]
                    }
                    
            # Add platform data
            for platform_id, platform_sales in self.sales_data["sales_by_platform"].items():
                report["platforms"][platform_id] = {
                    "name": self.platforms[platform_id]["name"] if platform_id in self.platforms else platform_id,
                    "sales_count": platform_sales["count"],
                    "revenue": platform_sales["revenue"]
                }
                
            # Add monthly data
            report["monthly_data"] = self.sales_data["monthly_sales"]
            
        elif period == "monthly" or period == "yearly":
            # Group by month or year
            grouped_data = {}
            
            for month, month_data in self.sales_data["monthly_sales"].items():
                if period == "yearly":
                    # Extract year from YYYY-MM
                    key = month.split("-")[0]
                else:
                    key = month
                    
                if key not in grouped_data:
                    grouped_data[key] = {
                        "count": 0,
                        "revenue": 0.0
                    }
                    
                grouped_data[key]["count"] += month_data["count"]
                grouped_data[key]["revenue"] += month_data["revenue"]
                
            report["monthly_data"] = grouped_data
            report["total_sales"] = self.sales_data["total_sales"]
            report["total_revenue"] = self.sales_data["total_revenue"]
            
        return report
        
    def generate_bundle(self, product_ids, bundle_name=None, discount_percentage=20):
        """
        Create a bundle of multiple ebooks with a discount
        
        Args:
            product_ids (list): List of product IDs to include in the bundle
            bundle_name (str, optional): Custom name for the bundle
            discount_percentage (int): Discount percentage for the bundle
            
        Returns:
            dict: Bundle data
        """
        # Validate product IDs
        valid_products = []
        total_price = 0.0
        
        for product_id in product_ids:
            if product_id in self.ebook_products:
                valid_products.append(self.ebook_products[product_id])
                total_price += self.ebook_products[product_id]["price"]
            else:
                print(f"Product {product_id} not found")
                
        if not valid_products:
            print("No valid products found for bundle")
            return None
            
        # Calculate discounted price
        discounted_price = total_price * (1 - discount_percentage / 100)
        discounted_price = round(discounted_price, 2)
        
        # Generate bundle name if not provided
        if not bundle_name:
            topics = [p["topic"] for p in valid_products]
            bundle_name = f"Ultimate {' & '.join(topics[:2])} Bundle"
            
        # Create bundle ID
        bundle_id = f"bundle_{uuid4().hex[:8]}"
        
        # Create bundle description
        system_message = "You are a marketing copywriter who creates compelling product descriptions."
        
        products_info = "\n".join([
            f"- {p['title']}: {p['description']}" for p in valid_products
        ])
        
        prompt = f"""
        Create a compelling description for a bundle of ebooks:
        
        Bundle Name: {bundle_name}
        Included Products:
        {products_info}
        
        Regular Price: ${total_price}
        Bundle Price: ${discounted_price} ({discount_percentage}% off)
        
        The description should:
        1. Highlight the value of getting all these resources together
        2. Emphasize the discount and savings
        3. Be concise but persuasive
        
        Just provide the description text with no additional formatting.
        """
        
        bundle_description = self.openai_generator.generate_content(prompt, system_message, max_tokens=500)
        
        if not bundle_description:
            bundle_description = f"Get {len(valid_products)} premium ebooks at {discount_percentage}% off the regular price. This bundle includes everything you need to master {', '.join(topics)}."
            
        # Create the bundle
        bundle = {
            "bundle_id": bundle_id,
            "name": bundle_name,
            "description": bundle_description,
            "products": [p["product_id"] for p in valid_products],
            "regular_price": total_price,
            "discount_percentage": discount_percentage,
            "price": discounted_price,
            "created_date": self.ebook_generator.openai_generator._get_current_datetime(),
            "sales_count": 0,
            "revenue": 0.0
        }
        
        # Save the bundle
        bundles_file = os.path.join(self.ebook_monetization_dir, "bundles.json")
        
        # Load existing bundles if file exists
        bundles = {}
        if os.path.exists(bundles_file):
            with open(bundles_file, 'r') as f:
                bundles = json.load(f)
                
        # Add new bundle
        bundles[bundle_id] = bundle
        
        # Save updated bundles
        with open(bundles_file, 'w') as f:
            json.dump(bundles, f, indent=2)
            
        return bundle
        
    def create_affiliate_program(self, product_id, commission_rate=50):
        """
        Create an affiliate program for an ebook product
        
        Args:
            product_id (str): ID of the ebook product
            commission_rate (int): Commission percentage for affiliates
            
        Returns:
            dict: Affiliate program data
        """
        if product_id not in self.ebook_products:
            print(f"Product {product_id} not found")
            return None
            
        product = self.ebook_products[product_id]
        
        # Create affiliate program ID
        program_id = f"aff_{product_id}"
        
        # Create affiliate program
        affiliate_program = {
            "program_id": program_id,
            "product_id": product_id,
            "product_name": product["title"],
            "commission_rate": commission_rate,
            "commission_amount": round(product["price"] * commission_rate / 100, 2),
            "affiliates": {},
            "total_sales": 0,
            "total_commissions": 0.0,
            "created_date": self.ebook_generator.openai_generator._get_current_datetime()
        }
        
        # Save the affiliate program
        affiliate_programs_file = os.path.join(self.ebook_monetization_dir, "affiliate_programs.json")
        
        # Load existing programs if file exists
        affiliate_programs = {}
        if os.path.exists(affiliate_programs_file):
            with open(affiliate_programs_file, 'r') as f:
                affiliate_programs = json.load(f)
                
        # Add new program
        affiliate_programs[program_id] = affiliate_program
        
        # Save updated programs
        with open(affiliate_programs_file, 'w') as f:
            json.dump(affiliate_programs, f, indent=2)
            
        # Generate affiliate marketing materials
        marketing_materials = self.generate_affiliate_materials(program_id)
        
        return {
            "affiliate_program": affiliate_program,
            "marketing_materials": marketing_materials
        }
        
    def generate_affiliate_materials(self, program_id):
        """
        Generate marketing materials for affiliates
        
        Args:
            program_id (str): ID of the affiliate program
            
        Returns:
            dict: Marketing materials
        """
        # Load affiliate programs
        affiliate_programs_file = os.path.join(self.ebook_monetization_dir, "affiliate_programs.json")
        
        if not os.path.exists(affiliate_programs_file):
            print("No affiliate programs found")
            return None
            
        with open(affiliate_programs_file, 'r') as f:
            affiliate_programs = json.load(f)
            
        if program_id not in affiliate_programs:
            print(f"Affiliate program {program_id} not found")
            return None
            
        program = affiliate_programs[program_id]
        product_id = program["product_id"]
        
        if product_id not in self.ebook_products:
            print(f"Product {product_id} not found")
            return None
            
        product = self.ebook_products[product_id]
        
        # Create directory for affiliate materials
        materials_dir = os.path.join(self.ebook_monetization_dir, f"affiliate_materials_{program_id}")
        os.makedirs(materials_dir, exist_ok=True)
        
        # Generate email swipe copy
        system_message = "You are an affiliate marketing specialist who creates high-converting promotional materials."
        
        prompt = f"""
        Create email swipe copy for affiliates to promote the following ebook:
        
        Title: {product['title']}
        Description: {product['description']}
        Price: ${product['price']}
        Commission: {program['commission_rate']}% (${program['commission_amount']} per sale)
        
        Create three different email templates:
        1. An educational email that provides value and soft-sells the product
        2. A direct promotional email with clear benefits and call-to-action
        3. A case study/testimonial style email
        
        For each email, provide:
        - Subject line
        - Email body (with appropriate formatting)
        - Call-to-action (with [AFFILIATE_LINK] placeholder)
        
        Format your response as a JSON array where each object contains subject, body, and cta fields.
        """
        
        email_templates = self.openai_generator.generate_structured_content(
            prompt, 
            system_message,
            output_structure=[{
                "subject": "Email subject line",
                "body": "Email body text",
                "cta": "Call to action text with [AFFILIATE_LINK] placeholder"
            }]
        )
        
        if not email_templates or not isinstance(email_templates, list):
            email_templates = []
            
        # Generate social media posts
        prompt = f"""
        Create social media posts for affiliates to promote the following ebook:
        
        Title: {product['title']}
        Description: {product['description']}
        Price: ${product['price']}
        Commission: {program['commission_rate']}% (${program['commission_amount']} per sale)
        
        Create three different posts for each platform:
        - Twitter (280 characters max)
        - Facebook
        - Instagram
        
        Each post should:
        1. Be engaging and attention-grabbing
        2. Highlight a key benefit of the ebook
        3. Include a call-to-action with [AFFILIATE_LINK] placeholder
        4. Include relevant hashtags
        
        Format your response as a JSON object with twitter_posts, facebook_posts, and instagram_posts arrays.
        """
        
        social_posts = self.openai_generator.generate_structured_content(
            prompt, 
            system_message,
            output_structure={
                "twitter_posts": ["Post text with [AFFILIATE_LINK] and hashtags"],
                "facebook_posts": ["Post text with [AFFILIATE_LINK] and hashtags"],
                "instagram_posts": ["Post text with [AFFILIATE_LINK] and hashtags"]
            }
        )
        
        if not social_posts:
            social_posts = {
                "twitter_posts": [],
                "facebook_posts": [],
                "instagram_posts": []
            }
            
        # Generate banner ad copy
        prompt = f"""
        Create copy for banner ads to promote the following ebook:
        
        Title: {product['title']}
        Description: {product['description']}
        Price: ${product['price']}
        
        Create three different banner ad copies with:
        1. Headline (short and attention-grabbing)
        2. Subheadline (supporting the main headline)
        3. Call-to-action button text
        
        Format your response as a JSON array where each object contains headline, subheadline, and cta fields.
        """
        
        banner_ads = self.openai_generator.generate_structured_content(
            prompt, 
            system_message,
            output_structure=[{
                "headline": "Main headline text",
                "subheadline": "Supporting subheadline text",
                "cta": "Call to action button text"
            }]
        )
        
        if not banner_ads or not isinstance(banner_ads, list):
            banner_ads = []
            
        # Save all materials
        materials = {
            "program_id": program_id,
            "product_id": product_id,
            "email_templates": email_templates,
            "social_posts": social_posts,
            "banner_ads": banner_ads
        }
        
        materials_path = os.path.join(materials_dir, "materials.json")
        with open(materials_path, "w", encoding="utf-8") as f:
            json.dump(materials, f, indent=2)
            
        # Create a README file for affiliates
        readme_path = os.path.join(materials_dir, "README.md")
        with open(readme_path, "w", encoding="utf-8") as f:
            f.write(f"# Affiliate Marketing Materials for {product['title']}\n\n")
            f.write(f"## Product Information\n\n")
            f.write(f"- **Title:** {product['title']}\n")
            f.write(f"- **Description:** {product['description']}\n")
            f.write(f"- **Price:** ${product['price']}\n")
            f.write(f"- **Commission:** {program['commission_rate']}% (${program['commission_amount']} per sale)\n\n")
            
            f.write(f"## Materials Included\n\n")
            f.write(f"- {len(email_templates)} Email Templates\n")
            f.write(f"- {len(social_posts.get('twitter_posts', []))} Twitter Posts\n")
            f.write(f"- {len(social_posts.get('facebook_posts', []))} Facebook Posts\n")
            f.write(f"- {len(social_posts.get('instagram_posts', []))} Instagram Posts\n")
            f.write(f"- {len(banner_ads)} Banner Ad Copies\n\n")
            
            f.write(f"## How to Use\n\n")
            f.write(f"1. Replace `[AFFILIATE_LINK]` with your unique affiliate link\n")
            f.write(f"2. Customize the materials to match your voice and audience\n")
            f.write(f"3. Schedule and publish the content on your platforms\n")
            f.write(f"4. Track your results and optimize your campaigns\n\n")
            
            f.write(f"## Contact\n\n")
            f.write(f"For questions or support, please contact the affiliate manager.\n")
            
        return {
            "materials": materials,
            "materials_dir": materials_dir,
            "readme_path": readme_path
        }
