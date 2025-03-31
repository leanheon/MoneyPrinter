import os
import json
import requests
from uuid import uuid4
from datetime import datetime
from src.config import get_config
from src.constants import ROOT_DIR
from src.openai_generator import OpenAIGenerator

class DigitalProductManager:
    """
    Class for managing digital product creation and sales
    """
    def __init__(self):
        """
        Initialize the DigitalProductManager with configuration settings
        """
        config = get_config()
        self.product_config = config.get("monetization", {}).get("digital_products", {})
        self.openai_generator = OpenAIGenerator()
        
        # Create digital products directory if it doesn't exist
        self.products_dir = os.path.join(ROOT_DIR, ".mp", "digital_products")
        os.makedirs(self.products_dir, exist_ok=True)
        
        # Load product catalog
        self.products = self._load_products()
        
    def _load_products(self):
        """
        Load product catalog from storage or create default
        
        Returns:
            dict: Dictionary of products and their details
        """
        products_file = os.path.join(self.products_dir, "catalog.json")
        
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
            
    def add_product(self, name, description, price, category, file_path=None, preview_image=None):
        """
        Add a new digital product to the catalog
        
        Args:
            name (str): Product name
            description (str): Product description
            price (float): Product price
            category (str): Product category
            file_path (str, optional): Path to the product file
            preview_image (str, optional): Path to preview image
            
        Returns:
            str: Product ID if successful, None otherwise
        """
        try:
            product_id = f"product_{uuid4().hex[:8]}"
            
            self.products[product_id] = {
                "name": name,
                "description": description,
                "price": price,
                "category": category,
                "file_path": file_path,
                "preview_image": preview_image,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "sales_count": 0,
                "status": "active"
            }
            
            # Save updated products
            products_file = os.path.join(self.products_dir, "catalog.json")
            with open(products_file, 'w') as f:
                json.dump(self.products, f, indent=2)
                
            return product_id
        except Exception as e:
            print(f"Error adding product: {e}")
            return None
            
    def get_products(self, category=None, status="active"):
        """
        Get products, optionally filtered by category and status
        
        Args:
            category (str, optional): Filter by category
            status (str, optional): Filter by status
            
        Returns:
            list: List of product dictionaries
        """
        filtered_products = []
        
        for product_id, product in self.products.items():
            # Skip if status doesn't match
            if status and product.get("status") != status:
                continue
                
            # Skip if category is specified and doesn't match
            if category and product.get("category") != category:
                continue
                
            # Add product ID to the product dictionary
            product_with_id = product.copy()
            product_with_id["product_id"] = product_id
            filtered_products.append(product_with_id)
                
        return filtered_products
        
    def generate_digital_product(self, topic, product_type):
        """
        Generate a digital product based on a topic and product type
        
        Args:
            topic (str): The topic for the digital product
            product_type (str): Type of product (ebook, guide, template, etc.)
            
        Returns:
            dict: Generated product information
        """
        if product_type == "ebook":
            return self.generate_ebook(topic)
        elif product_type == "guide":
            return self.generate_guide(topic)
        elif product_type == "template":
            return self.generate_template(topic)
        elif product_type == "checklist":
            return self.generate_checklist(topic)
        else:
            print(f"Unsupported product type: {product_type}")
            return None
            
    def generate_ebook(self, topic):
        """
        Generate an ebook on a given topic
        
        Args:
            topic (str): The topic for the ebook
            
        Returns:
            dict: Generated ebook information
        """
        system_message = "You are a professional ebook author and content creator."
        
        # Generate ebook title and outline
        outline_prompt = f"""
        Create a compelling ebook title and detailed chapter outline for an ebook about:
        
        Topic: {topic}
        
        The ebook should:
        1. Be comprehensive and valuable to the reader
        2. Cover key aspects of the topic
        3. Include practical advice and actionable tips
        4. Be structured in a logical flow
        
        Format your response as a JSON object with 'title' and 'chapters' fields.
        Each chapter should have a 'title' and 'sections' array with section titles.
        """
        
        try:
            outline = self.openai_generator.generate_structured_content(
                outline_prompt, 
                system_message,
                output_structure={
                    "title": "Ebook Title",
                    "chapters": [
                        {
                            "title": "Chapter Title",
                            "sections": ["Section 1", "Section 2"]
                        }
                    ]
                }
            )
            
            if not outline:
                return None
                
            # Generate ebook content chapter by chapter
            ebook_content = f"# {outline['title']}\n\n"
            
            for chapter_idx, chapter in enumerate(outline['chapters']):
                chapter_title = chapter['title']
                ebook_content += f"## Chapter {chapter_idx + 1}: {chapter_title}\n\n"
                
                # Generate content for each section
                for section_idx, section in enumerate(chapter['sections']):
                    section_prompt = f"""
                    Write detailed content for the following section of an ebook:
                    
                    Ebook: {outline['title']}
                    Chapter: {chapter_title}
                    Section: {section}
                    
                    The content should:
                    1. Be informative and valuable
                    2. Include examples and explanations
                    3. Be written in an engaging style
                    4. Be approximately 500 words
                    
                    Just provide the section content without any additional formatting or headers.
                    """
                    
                    section_content = self.openai_generator.generate_content(
                        section_prompt, 
                        system_message,
                        max_tokens=1000
                    )
                    
                    if section_content:
                        ebook_content += f"### {section}\n\n{section_content}\n\n"
                        
            # Save ebook content to file
            ebook_filename = f"{outline['title'].replace(' ', '_').lower()}.md"
            ebook_path = os.path.join(self.products_dir, ebook_filename)
            
            with open(ebook_path, 'w') as f:
                f.write(ebook_content)
                
            # Generate a description for the ebook
            description_prompt = f"""
            Write a compelling marketing description for the following ebook:
            
            Title: {outline['title']}
            Topics covered: {', '.join([chapter['title'] for chapter in outline['chapters']])}
            
            The description should:
            1. Highlight the value and benefits
            2. Mention the target audience
            3. Include key selling points
            4. Be approximately 150-200 words
            
            Just provide the description text without any additional formatting.
            """
            
            description = self.openai_generator.generate_content(
                description_prompt, 
                system_message,
                max_tokens=300
            )
            
            # Add the product to the catalog
            product_id = self.add_product(
                name=outline['title'],
                description=description,
                price=9.99,  # Default price
                category="ebook",
                file_path=ebook_path
            )
            
            if product_id:
                return {
                    "product_id": product_id,
                    "name": outline['title'],
                    "description": description,
                    "price": 9.99,
                    "category": "ebook",
                    "file_path": ebook_path
                }
            else:
                return None
                
        except Exception as e:
            print(f"Error generating ebook: {e}")
            return None
            
    def generate_guide(self, topic):
        """
        Generate a practical guide on a given topic
        
        Args:
            topic (str): The topic for the guide
            
        Returns:
            dict: Generated guide information
        """
        system_message = "You are a professional guide creator specializing in practical, actionable content."
        
        # Generate guide title and outline
        outline_prompt = f"""
        Create a compelling title and detailed outline for a practical guide about:
        
        Topic: {topic}
        
        The guide should:
        1. Focus on practical, actionable advice
        2. Include step-by-step instructions
        3. Cover essential aspects of the topic
        4. Be structured for easy reference
        
        Format your response as a JSON object with 'title' and 'sections' fields.
        Each section should have a 'title' and 'subsections' array.
        """
        
        try:
            outline = self.openai_generator.generate_structured_content(
                outline_prompt, 
                system_message,
                output_structure={
                    "title": "Guide Title",
                    "sections": [
                        {
                            "title": "Section Title",
                            "subsections": ["Subsection 1", "Subsection 2"]
                        }
                    ]
                }
            )
            
            if not outline:
                return None
                
            # Generate guide content section by section
            guide_content = f"# {outline['title']}\n\n"
            
            for section_idx, section in enumerate(outline['sections']):
                section_title = section['title']
                guide_content += f"## {section_title}\n\n"
                
                # Generate content for each subsection
                for subsection in section['subsections']:
                    subsection_prompt = f"""
                    Write detailed content for the following subsection of a practical guide:
                    
                    Guide: {outline['title']}
                    Section: {section_title}
                    Subsection: {subsection}
                    
                    The content should:
                    1. Be practical and actionable
                    2. Include specific steps or instructions
                    3. Use clear, concise language
                    4. Be approximately 300-400 words
                    
                    Just provide the subsection content without any additional formatting or headers.
                    """
                    
                    subsection_content = self.openai_generator.generate_content(
                        subsection_prompt, 
                        system_message,
                        max_tokens=800
                    )
                    
                    if subsection_content:
                        guide_content += f"### {subsection}\n\n{subsection_content}\n\n"
                        
            # Save guide content to file
            guide_filename = f"{outline['title'].replace(' ', '_').lower()}_guide.md"
            guide_path = os.path.join(self.products_dir, guide_filename)
            
            with open(guide_path, 'w') as f:
                f.write(guide_content)
                
            # Generate a description for the guide
            description_prompt = f"""
            Write a compelling marketing description for the following practical guide:
            
            Title: {outline['title']}
            Topics covered: {', '.join([section['title'] for section in outline['sections']])}
            
            The description should:
            1. Highlight the practical value
            2. Mention the target audience
            3. Emphasize the actionable nature of the content
            4. Be approximately 150-200 words
            
            Just provide the description text without any additional formatting.
            """
            
            description = self.openai_generator.generate_content(
                description_prompt, 
                system_message,
                max_tokens=300
            )
            
            # Add the product to the catalog
            product_id = self.add_product(
                name=outline['title'],
                description=description,
                price=7.99,  # Default price
                category="guide",
                file_path=guide_path
            )
            
            if product_id:
                return {
                    "product_id": product_id,
                    "name": outline['title'],
                    "description": description,
                    "price": 7.99,
                    "category": "guide",
                    "file_path": guide_path
                }
            else:
                return None
                
        except Exception as e:
            print(f"Error generating guide: {e}")
            return None
            
    def generate_template(self, topic):
        """
        Generate a template on a given topic
        
        Args:
            topic (str): The topic for the template
            
        Returns:
            dict: Generated template information
        """
        system_message = "You are a professional template designer specializing in practical, reusable content."
        
        # Generate template title and structure
        structure_prompt = f"""
        Create a title and structure for a professional template about:
        
        Topic: {topic}
        
        The template should:
        1. Be practical and reusable
        2. Include all necessary sections
        3. Provide clear instructions for use
        4. Be structured for easy customization
        
        Format your response as a JSON object with 'title', 'description', and 'sections' fields.
        Each section should have a 'title', 'instructions', and 'template_text'.
        """
        
        try:
            structure = self.openai_generator.generate_structured_content(
                structure_prompt, 
                system_message,
                output_structure={
                    "title": "Template Title",
                    "description": "Brief description of the template",
                    "sections": [
                        {
                            "title": "Section Title",
                            "instructions": "How to use this section",
                            "template_text": "Template text with [placeholders]"
                        }
                    ]
                }
            )
            
            if not structure:
                return None
                
            # Generate template content
            template_content = f"# {structure['title']}\n\n"
            template_content += f"{structure['description']}\n\n"
            template_content += "## How to Use This Template\n\n"
            template_content += "1. Read the instructions for each section\n"
            template_content += "2. Replace the [placeholders] with your specific information\n"
            template_content += "3. Customize the content to match your needs\n"
            template_content += "4. Delete any sections that aren't relevant\n\n"
            
            for section_idx, section in enumerate(structure['sections']):
                template_content += f"## {section['title']}\n\n"
                template_content += f"**Instructions:** {section['instructions']}\n\n"
                template_content += f"```\n{section['template_text']}\n```\n\n"
                        
            # Save template content to file
            template_filename = f"{structure['title'].replace(' ', '_').lower()}_template.md"
            template_path = os.path.join(self.products_dir, template_filename)
            
            with open(template_path, 'w') as f:
                f.write(template_content)
                
            # Generate a marketing description for the template
            description_prompt = f"""
            Write a compelling marketing description for the following template:
            
            Title: {structure['title']}
            Description: {structure['description']}
            Sections: {', '.join([section['title'] for section in structure['sections']])}
            
            The description should:
            1. Highlight the time-saving value
            2. Mention the target audience
            3. Emphasize the professional quality
            4. Be approximately 150-200 words
            
            Just provide the description text without any additional formatting.
            """
            
            marketing_description = self.openai_generator.generate_content(
                description_prompt, 
                system_message,
                max_tokens=300
            )
            
            # Add the product to the catalog
            product_id = self.add_product(
                name=structure['title'],
                description=marketing_description,
                price=4.99,  # Default price
                category="template",
                file_path=template_path
            )
            
            if product_id:
                return {
                    "product_id": product_id,
                    "name": structure['title'],
                    "description": marketing_description,
                    "price": 4.99,
                    "category": "template",
                    "file_path": template_path
                }
            else:
                return None
                
        except Exception as e:
            print(f"Error generating template: {e}")
            return None
            
    def generate_checklist(self, topic):
        """
        Generate a checklist on a given topic
        
        Args:
            topic (str): The topic for the checklist
            
        Returns:
            dict: Generated checklist information
        """
        system_message = "You are a professional checklist creator specializing in comprehensive, actionable content."
        
        # Generate checklist title and items
        checklist_prompt = f"""
        Create a comprehensive checklist about:
        
        Topic: {topic}
        
        The checklist should:
        1. Be thorough and comprehensive
        2. Include all important items
        3. Be organized in logical categories
        4. Include brief explanations for each item
        
        Format your response as a JSON object with 'title', 'description', and 'categories' fields.
        Each category should have a 'name' and 'items' array.
        Each item should have a 'text' and 'explanation'.
        """
        
        try:
            checklist = self.openai_generator.generate_structured_content(
                checklist_prompt, 
                system_message,
                output_structure={
                    "title": "Checklist Title",
                    "description": "Brief description of the checklist",
                    "categories": [
                        {
                            "name": "Category Name",
                            "items": [
                                {
                                    "text": "Checklist item",
                                    "explanation": "Brief explanation"
                                }
                            ]
                        }
                    ]
                }
            )
            
            if not checklist:
                return None
                
            # Generate checklist content
            checklist_content = f"# {checklist['title']}\n\n"
            checklist_content += f"{checklist['description']}\n\n"
            
            for category_idx, category in enumerate(checklist['categories']):
                checklist_content += f"## {category['name']}\n\n"
                
                for item_idx, item in enumerate(category['items']):
                    checklist_content += f"- [ ] {item['text']}\n"
                    checklist_content += f"  - *{item['explanation']}*\n\n"
                        
            # Save checklist content to file
            checklist_filename = f"{checklist['title'].replace(' ', '_').lower()}_checklist.md"
            checklist_path = os.path.join(self.products_dir, checklist_filename)
            
            with open(checklist_path, 'w') as f:
                f.write(checklist_content)
                
            # Generate a marketing description for the checklist
            description_prompt = f"""
            Write a compelling marketing description for the following checklist:
            
            Title: {checklist['title']}
            Description: {checklist['description']}
            Categories: {', '.join([category['name'] for category in checklist['categories']])}
            
            The description should:
            1. Highlight the comprehensive nature
            2. Mention the target audience
            3. Emphasize the practical value
            4. Be approximately 150-200 words
            
            Just provide the description text without any additional formatting.
            """
            
            marketing_description = self.openai_generator.generate_content(
                description_prompt, 
                system_message,
                max_tokens=300
            )
            
            # Add the product to the catalog
            product_id = self.add_product(
                name=checklist['title'],
                description=marketing_description,
                price=3.99,  # Default price
                category="checklist",
                file_path=checklist_path
            )
            
            if product_id:
                return {
                    "product_id": product_id,
                    "name": checklist['title'],
                    "description": marketing_description,
                    "price": 3.99,
                    "category": "checklist",
                    "file_path": checklist_path
                }
            else:
                return None
                
        except Exception as e:
            print(f"Error generating checklist: {e}")
            return None
            
    def generate_product_promotion(self, product_id, platform):
        """
        Generate promotional content for a digital product
        
        Args:
            product_id (str): ID of the product to promote
            platform (str): Platform for promotion (youtube, twitter, threads)
            
        Returns:
            dict: Generated promotional content
        """
        if product_id not in self.products:
            print(f"Product {product_id} not found")
            return None
            
        product = self.products[product_id]
        
        # Generate content based on platform
        if platform == "youtube":
            return self.generate_youtube_product_promotion(product, product_id)
        elif platform == "twitter":
            return self.generate_twitter_product_promotion(product, product_id)
        elif platform == "threads":
            return self.generate_threads_product_promotion(product, product_id)
        else:
            print(f"Unsupported platform: {platform}")
            return None
            
    def generate_youtube_product_promotion(self, product, product_id):
        """
        Generate YouTube promotional content for a digital product
        
        Args:
            product (dict): Product information
            product_id (str): Product ID
            
        Returns:
            dict: Generated promotional content
        """
        system_message = "You are a YouTube content creator who promotes digital products."
        
        prompt = f"""
        Create a YouTube video script and description to promote the following digital product:
        
        Product: {product['name']}
        Description: {product['description']}
        Category: {product['category']}
        Price: ${product['price']}
        
        The content should:
        1. Be engaging and valuable to the viewer
        2. Highlight the benefits of the product
        3. Include a clear call-to-action
        4. Not be overly salesy
        
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
                
            # Add product link to description
            description = response.get("description", "")
            description += f"\n\nGet the {product['name']} here: [PRODUCT_LINK]\n"
            response["description"] = description
            
            # Add product information to response
            response["product"] = {
                "product_id": product_id,
                "name": product['name'],
                "price": product['price'],
                "category": product['category']
            }
            
            return response
        except Exception as e:
            print(f"Error generating YouTube product promotion: {e}")
            return None
            
    def generate_twitter_product_promotion(self, product, product_id):
        """
        Generate Twitter/X promotional content for a digital product
        
        Args:
            product (dict): Product information
            product_id (str): Product ID
            
        Returns:
            dict: Generated promotional content
        """
        system_message = "You are a social media marketer who promotes digital products."
        
        prompt = f"""
        Create a Twitter/X post to promote the following digital product:
        
        Product: {product['name']}
        Description: {product['description']}
        Category: {product['category']}
        Price: ${product['price']}
        
        The post should:
        1. Be engaging and valuable
        2. Highlight a key benefit
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
                
            # Add product information to response
            response["product"] = {
                "product_id": product_id,
                "name": product['name'],
                "price": product['price'],
                "category": product['category']
            }
            
            return response
        except Exception as e:
            print(f"Error generating Twitter product promotion: {e}")
            return None
            
    def generate_threads_product_promotion(self, product, product_id):
        """
        Generate Threads promotional content for a digital product
        
        Args:
            product (dict): Product information
            product_id (str): Product ID
            
        Returns:
            dict: Generated promotional content
        """
        system_message = "You are a social media marketer who promotes digital products."
        
        prompt = f"""
        Create a Threads post to promote the following digital product:
        
        Product: {product['name']}
        Description: {product['description']}
        Category: {product['category']}
        Price: ${product['price']}
        
        The post should:
        1. Be engaging and valuable
        2. Highlight the key benefits
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
                
            # Add product information to response
            response["product"] = {
                "product_id": product_id,
                "name": product['name'],
                "price": product['price'],
                "category": product['category']
            }
            
            return response
        except Exception as e:
            print(f"Error generating Threads product promotion: {e}")
            return None
