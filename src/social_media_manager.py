import os
import json
import requests
from src.openai_generator import OpenAIGenerator
from src.card_news_generator import CardNewsGenerator
from src.constants import ROOT_DIR

class SocialMediaManager:
    """
    Class for managing social media posts across different platforms (X/Twitter, Threads, Instagram).
    """
    def __init__(self):
        """
        Initialize the SocialMediaManager.
        """
        self.openai_generator = OpenAIGenerator()
        self.card_news_generator = CardNewsGenerator()
        self.output_dir = os.path.join(ROOT_DIR, ".mp", "social_media")
        os.makedirs(self.output_dir, exist_ok=True)
        
    def generate_x_post(self, topic, with_image=False):
        """
        Generate a post for X (Twitter).
        
        Args:
            topic (str): The topic for the post
            with_image (bool): Whether to include an image
            
        Returns:
            dict: Generated post data
        """
        system_message = "You are a professional social media content creator for X (Twitter)."
        
        prompt = f"""
        Create an engaging, informative post for X (Twitter) about:
        
        {topic}
        
        The post should:
        - Be attention-grabbing and shareable
        - Include relevant hashtags
        - Be within the 280 character limit
        - Have a conversational, authentic tone
        
        Just provide the post text with no additional explanation.
        """
        
        post_text = self.openai_generator.generate_content(prompt, system_message, max_tokens=300)
        
        result = {
            "platform": "x",
            "topic": topic,
            "text": post_text.strip() if post_text else f"Check out this information about {topic}! #trending",
            "image_path": None
        }
        
        # Generate image if requested
        if with_image:
            image_prompt = self._generate_image_prompt(topic)
            image_path = self.openai_generator.generate_image(image_prompt)
            
            if image_path:
                result["image_path"] = image_path
        
        return result
    
    def generate_threads_post(self, topic, num_posts=3, with_images=False):
        """
        Generate a thread of posts for Threads.
        
        Args:
            topic (str): The topic for the thread
            num_posts (int): Number of posts in the thread
            with_images (bool): Whether to include images
            
        Returns:
            dict: Generated thread data
        """
        system_message = "You are a professional social media content creator for Threads."
        
        output_structure = {
            "thread": [
                {
                    "text": "First post in thread"
                }
            ]
        }
        
        prompt = f"""
        Create an engaging thread of {num_posts} posts for Threads about:
        
        {topic}
        
        Each post should:
        - Be engaging and informative
        - Flow naturally from one to the next
        - Be within the 500 character limit
        - Have a conversational, authentic tone
        
        Format your response as a JSON object with an array of posts, each with a text field.
        """
        
        try:
            response = self.openai_generator.generate_structured_content(
                prompt, 
                system_message,
                output_structure=output_structure
            )
            
            thread_posts = []
            
            if response and "thread" in response:
                thread_posts = response["thread"]
            else:
                # Fallback if structured content generation fails
                for i in range(num_posts):
                    if i == 0:
                        thread_posts.append({"text": f"Let's talk about {topic}! (1/{num_posts}) #threads"})
                    else:
                        thread_posts.append({"text": f"More about {topic}... ({i+1}/{num_posts}) #threads"})
            
            # Generate images if requested
            if with_images:
                for i, post in enumerate(thread_posts):
                    if i < len(thread_posts):  # Only generate images for existing posts
                        image_prompt = self._generate_image_prompt(topic, post.get("text", ""))
                        image_path = self.openai_generator.generate_image(image_prompt)
                        
                        if image_path:
                            post["image_path"] = image_path
            
            return {
                "platform": "threads",
                "topic": topic,
                "posts": thread_posts,
                "count": len(thread_posts)
            }
                
        except Exception as e:
            print(f"Error generating thread: {e}")
            # Fallback
            thread_posts = []
            for i in range(num_posts):
                if i == 0:
                    thread_posts.append({
                        "text": f"Let's talk about {topic}! (1/{num_posts}) #threads",
                        "image_path": None
                    })
                else:
                    thread_posts.append({
                        "text": f"More about {topic}... ({i+1}/{num_posts}) #threads",
                        "image_path": None
                    })
            
            return {
                "platform": "threads",
                "topic": topic,
                "posts": thread_posts,
                "count": len(thread_posts)
            }
    
    def generate_instagram_post(self, topic, post_type="carousel"):
        """
        Generate a post for Instagram.
        
        Args:
            topic (str): The topic for the post
            post_type (str): Type of post (single, carousel, story)
            
        Returns:
            dict: Generated post data
        """
        system_message = "You are a professional social media content creator for Instagram."
        
        # Generate caption
        prompt = f"""
        Create an engaging Instagram caption about:
        
        {topic}
        
        The caption should:
        - Be attention-grabbing and shareable
        - Include relevant hashtags (5-10)
        - Be between 100-200 characters
        - Have a conversational, authentic tone
        
        Just provide the caption text with no additional explanation.
        """
        
        caption = self.openai_generator.generate_content(prompt, system_message, max_tokens=300)
        
        result = {
            "platform": "instagram",
            "topic": topic,
            "caption": caption.strip() if caption else f"Check out this information about {topic}! #instagram",
            "type": post_type,
            "images": []
        }
        
        # Generate card news for carousel or single post
        if post_type == "carousel":
            card_news = self.card_news_generator.generate_card_news(topic, num_cards=5, style="modern")
            if card_news and "cards" in card_news:
                result["images"] = [card["path"] for card in card_news["cards"]]
        elif post_type == "single":
            card_news = self.card_news_generator.generate_card_news(topic, num_cards=1, style="colorful")
            if card_news and "cards" in card_news and len(card_news["cards"]) > 0:
                result["images"] = [card_news["cards"][0]["path"]]
        elif post_type == "story":
            card_news = self.card_news_generator.generate_card_news(topic, num_cards=1, style="minimal")
            if card_news and "cards" in card_news and len(card_news["cards"]) > 0:
                result["images"] = [card_news["cards"][0]["path"]]
        
        return result
    
    def _generate_image_prompt(self, topic, text=None):
        """
        Generate an optimized prompt for social media image.
        
        Args:
            topic (str): The main topic
            text (str): Optional text content for context
            
        Returns:
            str: Optimized image generation prompt
        """
        system_message = "You are a professional prompt engineer who creates detailed, effective prompts for DALL-E image generation."
        
        prompt_text = f"""
        Create a detailed, descriptive prompt for DALL-E to generate a high-quality image for social media about:
        
        Topic: {topic}
        """
        
        if text:
            prompt_text += f"\nContext: {text}"
            
        prompt_text += """
        
        The prompt should:
        - Be detailed and specific about visual elements
        - Include style guidance (photorealistic, illustration, etc.)
        - Mention lighting, perspective, and mood
        - Be between 50-100 words
        - NOT include any text overlays or words to appear in the image
        
        Just provide the prompt text with no additional explanation or formatting.
        """
        
        image_prompt = self.openai_generator.generate_content(prompt_text, system_message, max_tokens=200)
        return image_prompt.strip() if image_prompt else f"A high-quality image representing {topic}"
    
    def create_information_card_series(self, topic, num_cards=5):
        """
        Create a series of information cards for social media.
        
        Args:
            topic (str): The topic for the cards
            num_cards (int): Number of cards to create
            
        Returns:
            dict: Generated card series data
        """
        return self.card_news_generator.generate_card_news(topic, num_cards, style="modern")
    
    def save_post_data(self, post_data, filename=None):
        """
        Save post data to a JSON file.
        
        Args:
            post_data (dict): The post data to save
            filename (str): Optional filename
            
        Returns:
            str: Path to the saved file
        """
        if not filename:
            platform = post_data.get("platform", "social")
            topic_slug = post_data.get("topic", "post").lower().replace(" ", "_")
            filename = f"{platform}_{topic_slug}_{os.urandom(4).hex()}.json"
            
        file_path = os.path.join(self.output_dir, filename)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(post_data, f, indent=2)
            
        return file_path
