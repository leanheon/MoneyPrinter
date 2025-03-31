import re
import os
import json
import time
import random
import requests
import subprocess
from uuid import uuid4
from datetime import datetime

from src.config import get_config
from src.constants import ROOT_DIR
from src.cache import get_accounts, add_post
from src.status import get_verbose
from src.openai_generator import OpenAIGenerator
from src.classes.Tts import TTS

class YouTube:
    """
    Class for the YouTube Bot, that creates and uploads YouTube Shorts.
    """
    def __init__(self, account_uuid: str, account_nickname: str, topic: str) -> None:
        """
        Initializes the YouTube Bot.

        Args:
            account_uuid (str): The account UUID
            account_nickname (str): The account nickname
            topic (str): The topic to create a video about
        """
        self.account_uuid = account_uuid
        self.account_nickname = account_nickname
        self.topic = topic
        
        # Get account config from cache
        cached_accounts = get_accounts("youtube")
        self.account_config = None
        
        for account in cached_accounts:
            if account["id"] == self._account_uuid:
                self.account_config = account
                break
                
        if not self.account_config:
            raise Exception("Account configuration not found")
            
        # Initialize OpenAI generator
        self.openai_generator = OpenAIGenerator()
        
        # Initialize empty lists for images and audio paths
        self.images = []
        self.image_prompts = []
        self.audio_paths = []
        
    def generate_topic(self):
        """
        Generate a topic for a YouTube Short
        
        Returns:
            str: Generated topic
        """
        system_message = f"You are a creative content strategist for {self.account_config.get('niche', 'general')} YouTube Shorts."
        prompt = f"Generate a viral, engaging topic for a YouTube Short about {self.account_config.get('niche', 'general')}. The topic should be trendy, interesting, and have potential to go viral. Just provide the topic, no additional text."
        
        topic = self.openai_generator.generate_content(prompt, system_message, max_tokens=50)
        
        if self.get_verbose():
            print(f" => Generated Topic: {topic}")
            
        return topic.strip()
        
    def generate_script(self, topic):
        """
        Generate a script for a YouTube Short based on the topic
        
        Args:
            topic (str): The topic to create a script for
            
        Returns:
            str: Generated script
        """
        system_message = (
            f"You are a professional script writer for {self.account_config.get('niche', 'general')} YouTube Shorts. "
            f"Create engaging, concise scripts that capture attention in the first 3 seconds. "
            f"Use simple language, short sentences, and conversational tone. "
            f"Each sentence should be on a new line. "
            f"The total script should be between {self.account_config.get('script_sentence_length', 10)} and {self.account_config.get('script_sentence_length', 10) + 2} sentences."
        )
        
        prompt = f"Write an engaging script for a YouTube Short about: {topic}"
        
        script = self.openai_generator.generate_content(prompt, system_message, max_tokens=500)
        
        if self.get_verbose():
            print(f" => Generated Script: \n{script}\n")
            
        return script.strip()
        
    def generate_metadata(self, topic, script):
        """
        Generate metadata (title, description) for a YouTube Short
        
        Args:
            topic (str): The topic of the video
            script (str): The script of the video
            
        Returns:
            dict: Dictionary containing title and description
        """
        system_message = "You are a YouTube SEO expert who creates optimized metadata for short-form videos."
        
        output_structure = {
            "title": "Attention-grabbing title (max 60 chars)",
            "description": "Compelling description with hashtags (max 200 chars)"
        }
        
        prompt = f"""
        Based on the following topic and script for a YouTube Short, generate:
        1. An attention-grabbing title (max 60 characters)
        2. A compelling description with relevant hashtags (max 200 characters)
        
        Topic: {topic}
        
        Script:
        {script}
        """
        
        metadata = self.openai_generator.generate_structured_content(
            prompt, 
            system_message, 
            max_tokens=300,
            output_structure=output_structure
        )
        
        if not metadata:
            # Fallback if structured content generation fails
            metadata = {
                "title": topic,
                "description": f"{topic} #shorts #trending #{self.account_config.get('niche', 'content').replace(' ', '')}"
            }
            
        if self.get_verbose():
            print(f" => Generated Metadata: {metadata}")
            
        return metadata
        
    def generate_prompts(self):
        """
        Generate image prompts for the script
        
        Returns:
            list: List of image prompts
        """
        system_message = f"You are a creative prompt engineer for {self.account_config.get('niche', 'general')} content."
        
        prompt = f"""
        Create {self.account_config.get('script_sentence_length', 10)} detailed image prompts for DALL-E based on this topic:
        
        {self.topic}
        
        Each prompt should:
        - Be visually descriptive and detailed
        - Include style guidance (photorealistic, illustration, etc.)
        - Mention lighting, perspective, and mood
        - NOT include any text overlays or words to appear in the image
        
        Format your response as a JSON array of strings, with each string being a complete image prompt.
        """
        
        try:
            response = self.openai_generator.generate_structured_content(prompt, system_message)
            
            if isinstance(response, list):
                image_prompts = response
            elif isinstance(response, dict) and "prompts" in response:
                image_prompts = response["prompts"]
            else:
                # Try to extract a list from the response
                import re
                prompts_text = str(response)
                prompts_match = re.findall(r'"([^"]*)"', prompts_text)
                if prompts_match:
                    image_prompts = prompts_match
                else:
                    raise ValueError("Could not extract prompts from response")
                    
            # Limit to the number of sentences in the script
            n_prompts = min(len(image_prompts), self.account_config.get('script_sentence_length', 10))
            image_prompts = image_prompts[:n_prompts]
            
            if self.get_verbose():
                print(f" => Generated {len(image_prompts)} Image Prompts")
                
            self.image_prompts = image_prompts
            return image_prompts
            
        except Exception as e:
            if self.get_verbose():
                print(f"Failed to generate Image Prompts. Retrying... {e}")
            
            # Fallback to simpler approach
            image_prompts = []
            for i in range(self.account_config.get('script_sentence_length', 10)):
                prompt = f"A high-quality image related to {self.topic}, scene {i+1}"
                image_prompts.append(prompt)
                
            self.image_prompts = image_prompts
            return image_prompts
            
    def generate_images(self):
        """
        Generate images for the video using DALL-E
        
        Returns:
            list: List of image paths
        """
        if not self.image_prompts:
            self.generate_prompts()
            
        images = []
        
        for prompt in self.image_prompts:
            image_path = self.openai_generator.generate_image(prompt)
            
            if image_path:
                images.append(image_path)
                if self.get_verbose():
                    print(f" => Generated image: {image_path}")
            else:
                if self.get_verbose():
                    print(f"Failed to generate image for prompt: {prompt}")
                    
        self.images = images
        return images
        
    def generate_script_to_speech(self, tts_instance: TTS) -> str:
        """
        Converts the generated script into Speech using CoquiTTS and returns the path to the wav file.
        
        Args:
            tts_instance (TTS): Instance of TTS Class.
            
        Returns:
            str: Path to generated audio (WAV Format).
        """
        # Clean script, remove every character that is not a word character, a space, a period, a question mark, a comma, or an exclamation mark
        self.script = re.sub(r'[^\w\s.?,!]', '', self.script)
        
        path = os.path.join(ROOT_DIR, ".mp", f"{uuid4()}.wav")
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(path), exist_ok=True)
        
        # Split script into sentences
        sentences = self.script.split('\n')
        
        # Generate audio for each sentence
        audio_paths = []
        for i, sentence in enumerate(sentences):
            if not sentence.strip():
                continue
                
            sentence_path = os.path.join(ROOT_DIR, ".mp", f"{uuid4()}_{i}.wav")
            tts_instance.tts_to_file(sentence, sentence_path)
            audio_paths.append(sentence_path)
            
        self.audio_paths = audio_paths
        
        # Combine audio files if there are multiple sentences
        if len(audio_paths) > 1:
            from pydub import AudioSegment
            
            combined = AudioSegment.empty()
            for audio_path in audio_paths:
                segment = AudioSegment.from_wav(audio_path)
                combined += segment
                
            combined.export(path, format="wav")
        elif len(audio_paths) == 1:
            # Just copy the single file
            import shutil
            shutil.copy(audio_paths[0], path)
        else:
            if self.get_verbose():
                print("No audio generated - empty script")
            return None
            
        return path
        
    def create_video(self, audio_path, output_path=None):
        """
        Creates a video from the generated images and audio
        
        Args:
            audio_path (str): Path to the audio file
            output_path (str, optional): Path to save the output video
            
        Returns:
            str: Path to the created video
        """
        if not output_path:
            output_path = os.path.join(ROOT_DIR, ".mp", f"{uuid4()}.mp4")
            
        # Ensure directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        if not self.images:
            if self.get_verbose():
                print("No images generated - generating now")
            self.generate_images()
            
        if len(self.images) == 0:
            raise Exception("No images available for video creation")
            
        # Get audio duration
        from pydub import AudioSegment
        audio = AudioSegment.from_wav(audio_path)
        audio_duration = len(audio) / 1000  # Convert to seconds
        
        # Calculate duration per image
        image_duration = audio_duration / len(self.images)
        
        # Create temporary directory for processing
        import tempfile
        temp_dir = tempfile.mkdtemp()
        
        try:
            # Create a file with image durations
            duration_file = os.path.join(temp_dir, "durations.txt")
            with open(duration_file, "w") as f:
                for _ in self.images:
                    f.write(f"file '{_}'\n")
                    f.write(f"duration {image_duration}\n")
                    
            # Last image needs to be duplicated without duration to avoid ffmpeg warnings
            f.write(f"file '{self.images[-1]}'\n")
            
            # Use ffmpeg to create video
            ffmpeg_cmd = [
                "ffmpeg", "-y",
                "-f", "concat",
                "-safe", "0",
                "-i", duration_file,
                "-i", audio_path,
                "-c:v", "libx264",
                "-c:a", "aac",
                "-shortest",
                "-vf", "scale=1080:1920,fps=30",  # Vertical video format for shorts
                "-pix_fmt", "yuv420p",
                output_path
            ]
            
            subprocess.run(ffmpeg_cmd, check=True)
            
            if self.get_verbose():
                print(f" => Created video: {output_path}")
                
            return output_path
            
        except Exception as e:
            if self.get_verbose():
                print(f"Error creating video: {e}")
            return None
            
        finally:
            # Clean up temporary directory
            import shutil
            shutil.rmtree(temp_dir)
            
    def upload_video(self, video_path, title, description):
        """
        Uploads a video to YouTube
        
        Args:
            video_path (str): Path to the video file
            title (str): Title of the video
            description (str): Description of the video
            
        Returns:
            bool: True if upload was successful, False otherwise
        """
        # This is a placeholder for the actual upload functionality
        # In a real implementation, this would use the YouTube API or browser automation
        
        if self.get_verbose():
            print(f" => Uploading video: {title}")
            print(f" => Description: {description}")
            print(f" => Video path: {video_path}")
            
        # Add post to cache
        add_post({
            "content": title,
            "date": datetime.now().strftime("%m/%d/%Y, %H:%M:%S"),
            "platform": "youtube",
            "account_id": self.account_uuid
        })
        
        return True
        
    def create_short(self):
        """
        Creates a YouTube Short from start to finish
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Generate topic if not provided
            if not self.topic:
                self.topic = self.generate_topic()
                
            # Generate script
            self.script = self.generate_script(self.topic)
            
            # Generate metadata
            metadata = self.generate_metadata(self.topic, self.script)
            
            # Generate image prompts
            self.generate_prompts()
            
            # Generate images
            self.generate_images()
            
            # Generate speech
            tts_instance = TTS()
            audio_path = self.generate_script_to_speech(tts_instance)
            
            if not audio_path:
                if self.get_verbose():
                    print("Failed to generate audio")
                return False
                
            # Create video
            video_path = self.create_video(audio_path)
            
            if not video_path:
                if self.get_verbose():
                    print("Failed to create video")
                return False
                
            # Upload video
            upload_success = self.upload_video(
                video_path,
                metadata["title"],
                metadata["description"]
            )
            
            return upload_success
            
        except Exception as e:
            if self.get_verbose():
                print(f"Error creating short: {e}")
            return False
            
    def get_verbose(self):
        """
        Returns whether verbose mode is enabled
        
        Returns:
            bool: True if verbose mode is enabled, False otherwise
        """
        return get_verbose()
