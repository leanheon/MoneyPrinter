import os
import json
import requests
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from src.openai_generator import OpenAIGenerator
from src.constants import ROOT_DIR

class CardNewsGenerator:
    """
    Class for generating card news images for social media platforms.
    """
    def __init__(self):
        """
        Initialize the CardNewsGenerator.
        """
        self.openai_generator = OpenAIGenerator()
        self.output_dir = os.path.join(ROOT_DIR, ".mp", "card_news")
        os.makedirs(self.output_dir, exist_ok=True)
        
    def generate_card_news(self, topic, num_cards=5, style="modern"):
        """
        Generate a series of card news images for a topic.
        
        Args:
            topic (str): The topic for the card news
            num_cards (int): Number of cards to generate
            style (str): Style of the cards (modern, minimal, colorful)
            
        Returns:
            dict: Generated card news data including paths to images
        """
        # Generate content for the cards
        card_content = self._generate_card_content(topic, num_cards)
        
        # Generate images for each card
        card_images = []
        for i, content in enumerate(card_content):
            # Generate image for this card
            image_prompt = self._generate_image_prompt(topic, content["text"])
            image_path = self.openai_generator.generate_image(image_prompt)
            
            if image_path:
                # Create the card with the generated image and text
                card_path = self._create_card(
                    image_path, 
                    content["text"], 
                    content["title"], 
                    f"card_{i+1}.png",
                    style
                )
                
                if card_path:
                    card_images.append({
                        "path": card_path,
                        "title": content["title"],
                        "text": content["text"]
                    })
        
        return {
            "topic": topic,
            "style": style,
            "cards": card_images,
            "count": len(card_images)
        }
    
    def _generate_card_content(self, topic, num_cards):
        """
        Generate content for card news.
        
        Args:
            topic (str): The topic for the card news
            num_cards (int): Number of cards to generate
            
        Returns:
            list: List of card content dictionaries
        """
        system_message = "You are a professional content creator for social media card news."
        
        output_structure = {
            "cards": [
                {
                    "title": "Card title",
                    "text": "Card content text"
                }
            ]
        }
        
        prompt = f"""
        Create content for {num_cards} card news images about:
        
        {topic}
        
        For each card:
        1. Create a short, attention-grabbing title (max 10 words)
        2. Write concise, informative text (max 50 words)
        
        The cards should flow logically from one to the next, telling a complete story or explaining a concept.
        
        Format your response as a JSON object with an array of cards, each with title and text fields.
        """
        
        try:
            response = self.openai_generator.generate_structured_content(
                prompt, 
                system_message,
                output_structure=output_structure
            )
            
            if response and "cards" in response:
                return response["cards"]
            else:
                # Fallback if structured content generation fails
                return [{"title": f"{topic} - Part {i+1}", "text": f"Information about {topic}, part {i+1}."} for i in range(num_cards)]
                
        except Exception as e:
            print(f"Error generating card content: {e}")
            return [{"title": f"{topic} - Part {i+1}", "text": f"Information about {topic}, part {i+1}."} for i in range(num_cards)]
    
    def _generate_image_prompt(self, topic, text):
        """
        Generate an optimized prompt for card image.
        
        Args:
            topic (str): The main topic
            text (str): The text content for this card
            
        Returns:
            str: Optimized image generation prompt
        """
        system_message = "You are a professional prompt engineer who creates detailed, effective prompts for DALL-E image generation."
        
        prompt = f"""
        Create a detailed, descriptive prompt for DALL-E to generate a high-quality image for a social media card about:
        
        Topic: {topic}
        Card text: {text}
        
        The prompt should:
        - Be detailed and specific about visual elements
        - Include style guidance (photorealistic, illustration, etc.)
        - Mention lighting, perspective, and mood
        - Be between 50-100 words
        - NOT include any text overlays or words to appear in the image
        
        Just provide the prompt text with no additional explanation or formatting.
        """
        
        image_prompt = self.openai_generator.generate_content(prompt, system_message, max_tokens=200)
        return image_prompt.strip() if image_prompt else f"A high-quality image representing {topic}"
    
    def _create_card(self, image_path, text, title, output_filename, style="modern"):
        """
        Create a card news image with text overlay.
        
        Args:
            image_path (str): Path to the background image
            text (str): Text content for the card
            title (str): Title for the card
            output_filename (str): Filename for the output card
            style (str): Style of the card (modern, minimal, colorful)
            
        Returns:
            str: Path to the created card image
        """
        try:
            # Load the background image
            img = Image.open(image_path)
            
            # Resize to standard card size (1080x1080 for Instagram)
            img = img.resize((1080, 1080))
            
            # Create a drawing context
            draw = ImageDraw.Draw(img)
            
            # Set style parameters
            if style == "modern":
                title_color = (255, 255, 255)
                text_color = (255, 255, 255)
                overlay_color = (0, 0, 0, 128)
                font_name = "Arial.ttf"
            elif style == "minimal":
                title_color = (0, 0, 0)
                text_color = (0, 0, 0)
                overlay_color = (255, 255, 255, 180)
                font_name = "Arial.ttf"
            elif style == "colorful":
                title_color = (255, 255, 0)
                text_color = (255, 255, 255)
                overlay_color = (128, 0, 128, 150)
                font_name = "Arial.ttf"
            else:
                title_color = (255, 255, 255)
                text_color = (255, 255, 255)
                overlay_color = (0, 0, 0, 128)
                font_name = "Arial.ttf"
            
            # Try to load fonts, use default if not available
            try:
                title_font = ImageFont.truetype(font_name, 48)
                text_font = ImageFont.truetype(font_name, 36)
            except:
                title_font = ImageFont.load_default()
                text_font = ImageFont.load_default()
            
            # Add semi-transparent overlay
            overlay = Image.new('RGBA', img.size, overlay_color)
            img = Image.alpha_composite(img.convert('RGBA'), overlay)
            
            # Add title
            title_position = (40, 40)
            draw = ImageDraw.Draw(img)
            draw.text(title_position, title, title_color, font=title_font)
            
            # Add text (with word wrapping)
            text_position = (40, 120)
            text_width = img.width - 80
            
            # Simple word wrap
            words = text.split()
            lines = []
            current_line = []
            
            for word in words:
                current_line.append(word)
                test_line = ' '.join(current_line)
                text_size = draw.textbbox((0, 0), test_line, font=text_font)
                if text_size[2] - text_size[0] > text_width:
                    current_line.pop()
                    lines.append(' '.join(current_line))
                    current_line = [word]
            
            if current_line:
                lines.append(' '.join(current_line))
            
            # Draw wrapped text
            y_position = text_position[1]
            for line in lines:
                draw.text((text_position[0], y_position), line, text_color, font=text_font)
                y_position += text_font.size + 10
            
            # Save the card
            output_path = os.path.join(self.output_dir, output_filename)
            img = img.convert('RGB')
            img.save(output_path)
            
            return output_path
            
        except Exception as e:
            print(f"Error creating card: {e}")
            return None
