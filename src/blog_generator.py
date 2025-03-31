import os
import json
import requests
from uuid import uuid4
from datetime import datetime
from src.openai_generator import OpenAIGenerator
from src.constants import ROOT_DIR

class BlogGenerator:
    """
    Class for generating and posting blog content with AI-generated images.
    """
    def __init__(self):
        """
        Initialize the BlogGenerator.
        """
        self.openai_generator = OpenAIGenerator()
        self.blog_posts = []
        
    def generate_blog_post(self, topic, length="medium"):
        """
        Generate a complete blog post with title, content, and featured image.
        
        Args:
            topic (str): The topic to write about
            length (str): Length of the blog post (short, medium, long)
            
        Returns:
            dict: Blog post data including title, content, and image path
        """
        # Determine word count based on length
        word_counts = {
            "short": 500,
            "medium": 1000,
            "long": 2000
        }
        target_words = word_counts.get(length, 1000)
        
        # Generate blog title
        title = self._generate_blog_title(topic)
        
        # Generate blog content
        content = self._generate_blog_content(topic, title, target_words)
        
        # Generate featured image
        image_prompt = self._generate_image_prompt(topic, title)
        image_path = self.openai_generator.generate_image(image_prompt, size="1024x1024")
        
        # Create blog post object
        blog_post = {
            "title": title,
            "content": content,
            "topic": topic,
            "image_path": image_path,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "word_count": len(content.split())
        }
        
        self.blog_posts.append(blog_post)
        return blog_post
    
    def _generate_blog_title(self, topic):
        """
        Generate an engaging blog post title.
        
        Args:
            topic (str): The topic to generate a title for
            
        Returns:
            str: Generated blog title
        """
        system_message = "You are a professional blog writer who creates engaging, SEO-friendly titles."
        
        prompt = f"""
        Create an engaging, click-worthy blog post title about:
        
        {topic}
        
        The title should:
        - Be attention-grabbing and compelling
        - Include keywords for SEO
        - Be between 40-60 characters
        - Not use clickbait tactics
        
        Just provide the title text with no additional explanation or formatting.
        """
        
        title = self.openai_generator.generate_content(prompt, system_message, max_tokens=100)
        return title.strip() if title else f"Blog Post About {topic}"
    
    def _generate_blog_content(self, topic, title, target_words):
        """
        Generate comprehensive blog post content.
        
        Args:
            topic (str): The main topic
            title (str): The blog post title
            target_words (int): Target word count
            
        Returns:
            str: Generated blog content in HTML format
        """
        system_message = f"""
        You are a professional blog writer who creates engaging, informative content.
        Write in a conversational yet authoritative tone.
        Use proper HTML formatting with h2, h3, p, ul, ol, and other appropriate tags.
        Include a proper introduction and conclusion.
        Target approximately {target_words} words.
        """
        
        prompt = f"""
        Write a comprehensive blog post with the title:
        
        "{title}"
        
        About the topic:
        
        {topic}
        
        The blog post should:
        - Start with an engaging introduction
        - Include 3-5 main sections with subheadings
        - Use a mix of paragraphs, lists, and quotes
        - Include a conclusion with key takeaways
        - Be formatted in proper HTML
        - Be approximately {target_words} words
        
        Format the entire post in HTML, using appropriate tags (h2, h3, p, ul, ol, blockquote, etc.).
        """
        
        content = self.openai_generator.generate_content(prompt, system_message, max_tokens=4000)
        
        # Ensure content has proper HTML structure
        if content and not content.strip().startswith("<"):
            content = f"<p>{content.replace('\\n\\n', '</p><p>').replace('\\n', '<br>')}</p>"
            
        return content
    
    def _generate_image_prompt(self, topic, title):
        """
        Generate an optimized prompt for blog featured image.
        
        Args:
            topic (str): The main topic
            title (str): The blog post title
            
        Returns:
            str: Optimized image generation prompt
        """
        system_message = "You are a professional prompt engineer who creates detailed, effective prompts for DALL-E image generation."
        
        prompt = f"""
        Create a detailed, descriptive prompt for DALL-E to generate a high-quality featured image for a blog post:
        
        Blog title: {title}
        Topic: {topic}
        
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
    
    def post_to_blog(self, blog_post, platform="wordpress"):
        """
        Post the generated blog content to a blog platform.
        
        Args:
            blog_post (dict): The blog post data
            platform (str): The blog platform to post to
            
        Returns:
            dict: Response data including URL of the published post
        """
        # This is a placeholder for actual blog posting functionality
        # In a real implementation, this would use the WordPress API or other blog platform APIs
        
        print(f"Posting blog '{blog_post['title']}' to {platform}")
        print(f"Content length: {blog_post['word_count']} words")
        print(f"Featured image: {blog_post['image_path']}")
        
        # Simulate posting to blog
        post_url = f"https://example.com/blog/{blog_post['title'].lower().replace(' ', '-')}"
        
        return {
            "success": True,
            "url": post_url,
            "platform": platform,
            "post_id": str(uuid4()),
            "date_published": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    
    def save_blog_post(self, blog_post, output_dir=None):
        """
        Save the blog post content and image to files.
        
        Args:
            blog_post (dict): The blog post data
            output_dir (str): Directory to save the files
            
        Returns:
            dict: Paths to the saved files
        """
        if not output_dir:
            output_dir = os.path.join(ROOT_DIR, ".mp", "blog_posts")
            
        # Ensure directory exists
        os.makedirs(output_dir, exist_ok=True)
        
        # Create a safe filename from the title
        safe_title = blog_post["title"].lower().replace(' ', '_').replace('?', '').replace('!', '').replace(',', '').replace('.', '')
        
        # Save HTML content
        html_path = os.path.join(output_dir, f"{safe_title}.html")
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(f"<!DOCTYPE html>\n<html>\n<head>\n<title>{blog_post['title']}</title>\n</head>\n<body>\n")
            f.write(f"<h1>{blog_post['title']}</h1>\n")
            
            # Add featured image if available
            if blog_post.get("image_path"):
                image_filename = os.path.basename(blog_post["image_path"])
                f.write(f'<img src="{image_filename}" alt="{blog_post["title"]}" style="max-width:100%;height:auto;">\n')
            
            f.write(blog_post["content"])
            f.write("\n</body>\n</html>")
        
        # Copy image if available
        image_path = None
        if blog_post.get("image_path") and os.path.exists(blog_post["image_path"]):
            import shutil
            image_filename = os.path.basename(blog_post["image_path"])
            image_path = os.path.join(output_dir, image_filename)
            shutil.copy(blog_post["image_path"], image_path)
        
        # Save metadata
        meta_path = os.path.join(output_dir, f"{safe_title}_meta.json")
        meta_data = {
            "title": blog_post["title"],
            "topic": blog_post["topic"],
            "date": blog_post["date"],
            "word_count": blog_post["word_count"],
            "html_file": os.path.basename(html_path),
            "image_file": os.path.basename(image_path) if image_path else None
        }
        
        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump(meta_data, f, indent=2)
        
        return {
            "html_path": html_path,
            "image_path": image_path,
            "meta_path": meta_path
        }
