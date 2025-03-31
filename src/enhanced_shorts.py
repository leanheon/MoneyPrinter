import os
import json
import time
from src.classes.ShortsGenerator import ShortsGenerator
from src.openai_generator import OpenAIGenerator
from src.dropbox_uploader import DropboxUploader

class EnhancedShorts:
    """
    Enhanced Shorts Generator with multiple production methods.
    Supports story-based shorts, knowledge-based shorts, and custom shorts.
    Includes Dropbox integration for uploading generated videos.
    """
    def __init__(self, dropbox_token=None):
        """
        Initialize the Enhanced Shorts Generator.
        
        Args:
            dropbox_token (str): Optional Dropbox access token for uploading videos
        """
        self.openai_generator = OpenAIGenerator()
        self.dropbox_uploader = DropboxUploader(dropbox_token)
        
    def create_story_short(self, topic, script=None, upload_to_dropbox=False):
        """
        Create a story-based short with AI-generated drawings.
        
        Args:
            topic (str): The topic for the short
            script (str): Optional pre-written script
            upload_to_dropbox (bool): Whether to upload the video to Dropbox
            
        Returns:
            dict: Result data including video path and Dropbox link if uploaded
        """
        # Create ShortsGenerator instance for story-based short
        generator = ShortsGenerator(topic, is_knowledge_short=False)
        
        # Use provided script or generate new one
        if script and script.strip():
            generator.script = script.strip()
        else:
            generator.generate_script()
            
        # Generate metadata
        generator.generate_metadata()
        
        # Create the short
        video_path = generator.create_short()
        
        result = {
            "type": "story_short",
            "topic": topic,
            "title": generator.title,
            "description": generator.description,
            "script": generator.script,
            "video_path": video_path,
            "dropbox_link": None
        }
        
        # Upload to Dropbox if requested and video was created successfully
        if upload_to_dropbox and video_path and self.dropbox_uploader.dbx:
            dropbox_path = f"/shorts/story/{os.path.basename(video_path)}"
            upload_result = self.dropbox_uploader.upload_file(video_path, dropbox_path)
            
            if upload_result.get("success"):
                result["dropbox_link"] = upload_result.get("shared_link")
                result["dropbox_path"] = upload_result.get("path")
        
        return result
    
    def create_knowledge_short(self, topic, script=None, upload_to_dropbox=False):
        """
        Create a knowledge-based short with educational content.
        
        Args:
            topic (str): The topic for the short
            script (str): Optional pre-written script
            upload_to_dropbox (bool): Whether to upload the video to Dropbox
            
        Returns:
            dict: Result data including video path and Dropbox link if uploaded
        """
        # Create ShortsGenerator instance for knowledge-based short
        generator = ShortsGenerator(topic, is_knowledge_short=True)
        
        # Use provided script or generate new one
        if script and script.strip():
            generator.script = script.strip()
        else:
            generator.generate_script()
            
        # Generate metadata
        generator.generate_metadata()
        
        # Create the short
        video_path = generator.create_short()
        
        result = {
            "type": "knowledge_short",
            "topic": topic,
            "title": generator.title,
            "description": generator.description,
            "script": generator.script,
            "video_path": video_path,
            "dropbox_link": None
        }
        
        # Upload to Dropbox if requested and video was created successfully
        if upload_to_dropbox and video_path and self.dropbox_uploader.dbx:
            dropbox_path = f"/shorts/knowledge/{os.path.basename(video_path)}"
            upload_result = self.dropbox_uploader.upload_file(video_path, dropbox_path)
            
            if upload_result.get("success"):
                result["dropbox_link"] = upload_result.get("shared_link")
                result["dropbox_path"] = upload_result.get("path")
        
        return result
    
    def create_custom_short(self, topic, custom_images, script=None, upload_to_dropbox=False):
        """
        Create a custom short with user-provided images.
        
        Args:
            topic (str): The topic for the short
            custom_images (list): List of paths to custom images
            script (str): Optional pre-written script
            upload_to_dropbox (bool): Whether to upload the video to Dropbox
            
        Returns:
            dict: Result data including video path and Dropbox link if uploaded
        """
        # Create ShortsGenerator instance
        generator = ShortsGenerator(topic, is_knowledge_short=False)
        
        # Use provided script or generate new one
        if script and script.strip():
            generator.script = script.strip()
        else:
            generator.generate_script()
            
        # Generate metadata
        generator.generate_metadata()
        
        # Override the images with custom images
        generator.images = custom_images
        
        # Create the short
        video_path = generator.create_short()
        
        result = {
            "type": "custom_short",
            "topic": topic,
            "title": generator.title,
            "description": generator.description,
            "script": generator.script,
            "video_path": video_path,
            "dropbox_link": None
        }
        
        # Upload to Dropbox if requested and video was created successfully
        if upload_to_dropbox and video_path and self.dropbox_uploader.dbx:
            dropbox_path = f"/shorts/custom/{os.path.basename(video_path)}"
            upload_result = self.dropbox_uploader.upload_file(video_path, dropbox_path)
            
            if upload_result.get("success"):
                result["dropbox_link"] = upload_result.get("shared_link")
                result["dropbox_path"] = upload_result.get("path")
        
        return result
    
    def create_short_by_method(self, method, topic, script=None, custom_images=None, upload_to_dropbox=False):
        """
        Create a short using the specified method.
        
        Args:
            method (str): The method to use (story, knowledge, custom)
            topic (str): The topic for the short
            script (str): Optional pre-written script
            custom_images (list): List of paths to custom images (for custom method)
            upload_to_dropbox (bool): Whether to upload the video to Dropbox
            
        Returns:
            dict: Result data including video path and Dropbox link if uploaded
        """
        if method.lower() == "story":
            return self.create_story_short(topic, script, upload_to_dropbox)
        elif method.lower() == "knowledge":
            return self.create_knowledge_short(topic, script, upload_to_dropbox)
        elif method.lower() == "custom" and custom_images:
            return self.create_custom_short(topic, custom_images, script, upload_to_dropbox)
        else:
            raise ValueError(f"Invalid method: {method}. Must be 'story', 'knowledge', or 'custom' (with custom_images provided).")
