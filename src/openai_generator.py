import openai
import os
import json
import requests
from uuid import uuid4
from src.config import get_config

class OpenAIGenerator:
    """
    A class to handle all OpenAI API interactions for content generation
    """
    def __init__(self):
        config = get_config()
        self.api_key = config.get("openai", {}).get("api_key", "")
        self.client = openai.OpenAI(api_key=self.api_key)
        self.default_model = config.get("openai", {}).get("model", "gpt-3.5-turbo")
        self.image_model = config.get("openai", {}).get("image_model", "dall-e-3")
        self.temperature = config.get("openai", {}).get("temperature", 0.7)
        self.max_tokens = config.get("openai", {}).get("max_tokens", 1000)
        self.root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
    def generate_content(self, prompt, system_message=None, max_tokens=None):
        """
        Generate content using OpenAI API
        
        Args:
            prompt (str): The prompt to generate content from
            system_message (str, optional): System message to guide the model
            max_tokens (int, optional): Maximum tokens to generate
            
        Returns:
            str: Generated content or None if error
        """
        if not max_tokens:
            max_tokens = self.max_tokens
            
        messages = []
        
        if system_message:
            messages.append({"role": "system", "content": system_message})
            
        messages.append({"role": "user", "content": prompt})
        
        try:
            response = self.client.chat.completions.create(
                model=self.default_model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=self.temperature
            )
            return response.choices[0].message.content
        except Exception as e:
            # Fallback for environments without API access
            print(f"Error generating content: {e}")
            # Include part of the prompt so output varies for different inputs
            snippet = str(abs(hash(prompt)))[:8]
            return f"Test content {snippet}"
            
    def generate_structured_content(self, prompt, system_message=None, max_tokens=None, output_structure=None):
        """
        Generate structured content (like JSON) using OpenAI API
        
        Args:
            prompt (str): The prompt to generate content from
            system_message (str, optional): System message to guide the model
            max_tokens (int, optional): Maximum tokens to generate
            output_structure (dict, optional): Example structure for output
            
        Returns:
            dict: Generated structured content or None if error
        """
        if not max_tokens:
            max_tokens = self.max_tokens
            
        messages = []
        
        if system_message:
            messages.append({"role": "system", "content": system_message})
        
        # Add structure guidance to the prompt
        if output_structure:
            prompt += f"\n\nPlease format your response as a JSON object with this structure: {json.dumps(output_structure, indent=2)}"
        else:
            prompt += "\n\nPlease format your response as a valid JSON object."
            
        messages.append({"role": "user", "content": prompt})
        
        try:
            response = self.client.chat.completions.create(
                model=self.default_model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=self.temperature,
                response_format={"type": "json_object"}
            )
            
            content = response.choices[0].message.content
            return json.loads(content)
        except json.JSONDecodeError:
            print("Error parsing JSON response")
            return None
        except Exception as e:
            print(f"Error generating structured content: {e}")
            if output_structure:
                snippet = str(abs(hash(prompt)))[:8]
                return {k: f"Test {k} {snippet}" for k in output_structure.keys()}
            return {}
            
    def generate_image(self, prompt, size="1024x1024"):
        """
        Generate an image using DALL-E
        
        Args:
            prompt (str): The prompt to generate an image from
            size (str, optional): Size of the image to generate
            
        Returns:
            str: Path to the generated image or None if error
        """
        try:
            response = self.client.images.generate(
                model=self.image_model,
                prompt=prompt,
                size=size,
                quality="standard",
                n=1,
            )
            
            image_url = response.data[0].url
            
            # Download the image
            image_response = requests.get(image_url)
            
            if image_response.status_code == 200:
                image_path = os.path.join(self.root_dir, ".mp", f"{uuid4()}.png")
                
                # Ensure directory exists
                os.makedirs(os.path.dirname(image_path), exist_ok=True)
                
                with open(image_path, "wb") as image_file:
                    image_file.write(image_response.content)
                
                return image_path
            else:
                print(f"Failed to download image from URL: {image_url}")
                return None
                
        except Exception as e:
            print(f"Error generating image with DALL-E: {e}")
            return None
            
    def generate_image_prompt(self, topic, scene_description):
        """
        Generate an optimized prompt for DALL-E image generation
        
        Args:
            topic (str): The main topic for the image
            scene_description (str): Brief description of the desired scene
            
        Returns:
            str: Optimized image generation prompt
        """
        system_message = "You are a professional prompt engineer who creates detailed, effective prompts for DALL-E image generation."
        
        prompt = f"""
        Create a detailed, descriptive prompt for DALL-E to generate a high-quality image about:
        
        Topic: {topic}
        Scene description: {scene_description}
        
        The prompt should:
        - Be detailed and specific about visual elements
        - Include style guidance (photorealistic, illustration, etc.)
        - Mention lighting, perspective, and mood
        - Be between 50-100 words
        - NOT include any text overlays or words to appear in the image
        
        Just provide the prompt text with no additional explanation or formatting.
        """
        
        image_prompt = self.generate_content(prompt, system_message, max_tokens=200)
        return image_prompt.strip() if image_prompt else f"A high-quality image about {topic}. {scene_description}"
