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

class ShortsGenerator:
    """
    Class for the Shorts Generator, that creates YouTube Shorts with subtitles and AI-generated images.
    Supports both story-based shorts with AI drawings and knowledge-based shorts with informational content.
    """
    def __init__(self, topic: str, is_knowledge_short: bool = False) -> None:
        """
        Initializes the Shorts Generator.

        Args:
            topic (str): The topic to create a video about
            is_knowledge_short (bool): Whether this is a knowledge-based short (True) or story-based short (False)
        """
        self.topic = topic
        self.is_knowledge_short = is_knowledge_short
        self.script = None
        self.title = None
        self.description = None
        
        # Initialize OpenAI generator
        self.openai_generator = OpenAIGenerator()
        
        # Initialize empty lists for images and audio paths
        self.images = []
        self.image_prompts = []
        self.audio_paths = []
        self.subtitle_timings = []
        
        # Set default parameters
        self.script_sentence_length = 10
        self.channel_name = "셀레몬" if not is_knowledge_short else "강석주"
        
    def generate_script(self):
        """
        Generate a script for a Short based on the topic
        
        Returns:
            str: Generated script
        """
        if self.is_knowledge_short:
            system_message = (
                "You are a professional script writer for educational YouTube Shorts. "
                "Create engaging, informative scripts that explain curious knowledge or facts. "
                "Use simple language, short sentences, and conversational tone. "
                "Each sentence should be on a new line. "
                f"The total script should be between {self.script_sentence_length} and {self.script_sentence_length + 2} sentences."
            )
            
            prompt = f"Write an informative script for a YouTube Short explaining: {self.topic}"
        else:
            system_message = (
                "You are a professional script writer for story-based YouTube Shorts. "
                "Create engaging, narrative scripts that tell interesting stories. "
                "Use simple language, short sentences, and conversational tone. "
                "Each sentence should be on a new line. "
                f"The total script should be between {self.script_sentence_length} and {self.script_sentence_length + 2} sentences."
            )
            
            prompt = f"Write an engaging story script for a YouTube Short about: {self.topic}"
        
        script = self.openai_generator.generate_content(prompt, system_message, max_tokens=500)
        
        if get_verbose():
            print(f" => Generated Script: \n{script}\n")
            
        self.script = script.strip()
        return self.script
        
    def generate_metadata(self):
        """
        Generate metadata (title, description) for a Short
        
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
        
        Topic: {self.topic}
        
        Script:
        {self.script}
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
                "title": self.topic,
                "description": f"{self.topic} #shorts #trending"
            }
            
        if get_verbose():
            print(f" => Generated Metadata: {metadata}")
            
        self.title = metadata["title"]
        self.description = metadata["description"]
        return metadata
        
    def generate_image_prompts(self):
        """
        Generate image prompts for the script
        
        Returns:
            list: List of image prompts
        """
        if self.is_knowledge_short:
            system_message = "You are a creative prompt engineer for educational content."
            
            prompt = f"""
            Create {self.script_sentence_length} detailed image prompts for DALL-E based on this educational topic:
            
            {self.topic}
            
            Each prompt should:
            - Be visually descriptive and detailed
            - Focus on factual, informative imagery
            - Include style guidance (photorealistic, diagram, etc.)
            - NOT include any text overlays or words to appear in the image
            
            Format your response as a JSON array of strings, with each string being a complete image prompt.
            """
        else:
            system_message = "You are a creative prompt engineer for narrative content."
            
            prompt = f"""
            Create {self.script_sentence_length} detailed image prompts for DALL-E based on this story topic:
            
            {self.topic}
            
            Each prompt should:
            - Be visually descriptive and detailed
            - Include style guidance (anime-style, cute illustration, etc.)
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
            script_sentences = self.script.split('\n')
            n_prompts = min(len(image_prompts), len(script_sentences))
            image_prompts = image_prompts[:n_prompts]
            
            if get_verbose():
                print(f" => Generated {len(image_prompts)} Image Prompts")
                
            self.image_prompts = image_prompts
            return image_prompts
            
        except Exception as e:
            if get_verbose():
                print(f"Failed to generate Image Prompts. Retrying... {e}")
            
            # Fallback to simpler approach
            image_prompts = []
            script_sentences = self.script.split('\n')
            for i, sentence in enumerate(script_sentences):
                if not sentence.strip():
                    continue
                prompt = f"A high-quality {'educational image' if self.is_knowledge_short else 'anime-style illustration'} related to {self.topic}, scene: {sentence}"
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
            self.generate_image_prompts()
            
        images = []
        
        for prompt in self.image_prompts:
            image_path = self.openai_generator.generate_image(prompt)
            
            if image_path:
                images.append(image_path)
                if get_verbose():
                    print(f" => Generated image: {image_path}")
            else:
                if get_verbose():
                    print(f"Failed to generate image for prompt: {prompt}")
                    
        self.images = images
        return images
        
    def generate_script_to_speech(self, tts_instance: TTS):
        """
        Converts the generated script into Speech using TTS and returns the path to the wav file.
        Also generates subtitle timings.
        
        Args:
            tts_instance (TTS): Instance of TTS Class.
            
        Returns:
            str: Path to generated audio (WAV Format).
        """
        # Clean script, remove every character that is not a word character, a space, a period, a question mark, a comma, or an exclamation mark
        clean_script = re.sub(r'[^\w\s.?,!]', '', self.script)
        
        path = os.path.join(ROOT_DIR, ".mp", f"{uuid4()}.wav")
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(path), exist_ok=True)
        
        # Split script into sentences
        sentences = self.script.split('\n')
        
        # Generate audio for each sentence
        audio_paths = []
        subtitle_timings = []
        current_time = 0
        
        for i, sentence in enumerate(sentences):
            if not sentence.strip():
                continue
                
            sentence_path = os.path.join(ROOT_DIR, ".mp", f"{uuid4()}_{i}.wav")
            tts_instance.tts_to_file(sentence, sentence_path)
            audio_paths.append(sentence_path)
            
            # Calculate duration of this sentence's audio
            from pydub import AudioSegment
            audio_segment = AudioSegment.from_wav(sentence_path)
            duration = len(audio_segment) / 1000  # Convert to seconds
            
            # Add subtitle timing
            subtitle_timings.append({
                "text": sentence,
                "start": current_time,
                "end": current_time + duration
            })
            
            current_time += duration
            
        self.audio_paths = audio_paths
        self.subtitle_timings = subtitle_timings
        
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
            if get_verbose():
                print("No audio generated - empty script")
            return None
            
        return path
        
    def create_video_with_subtitles(self, audio_path, output_path=None):
        """
        Creates a video from the generated images, audio, and adds subtitles
        
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
            if get_verbose():
                print("No images generated - generating now")
            self.generate_images()
            
        if len(self.images) == 0:
            raise Exception("No images available for video creation")
            
        # Get audio duration
        from pydub import AudioSegment
        audio = AudioSegment.from_wav(audio_path)
        audio_duration = len(audio) / 1000  # Convert to seconds
        
        # Create temporary directory for processing
        import tempfile
        temp_dir = tempfile.mkdtemp()
        
        try:
            # Create a file with image durations
            duration_file = os.path.join(temp_dir, "durations.txt")
            with open(duration_file, "w") as f:
                for i, image_path in enumerate(self.images):
                    # Match image with corresponding subtitle timing
                    if i < len(self.subtitle_timings):
                        subtitle_duration = self.subtitle_timings[i]["end"] - self.subtitle_timings[i]["start"]
                        f.write(f"file '{image_path}'\n")
                        f.write(f"duration {subtitle_duration}\n")
                    else:
                        # If we have more images than subtitles, distribute remaining time
                        remaining_images = len(self.images) - i
                        remaining_time = audio_duration - (self.subtitle_timings[-1]["end"] if self.subtitle_timings else 0)
                        image_duration = remaining_time / remaining_images
                        f.write(f"file '{image_path}'\n")
                        f.write(f"duration {image_duration}\n")
                        
            # Last image needs to be duplicated without duration to avoid ffmpeg warnings
            f.write(f"file '{self.images[-1]}'\n")
            
            # Create subtitle file (SRT format)
            subtitle_file = os.path.join(temp_dir, "subtitles.srt")
            with open(subtitle_file, "w", encoding="utf-8") as f:
                for i, timing in enumerate(self.subtitle_timings):
                    start_time = self._format_time(timing["start"])
                    end_time = self._format_time(timing["end"])
                    f.write(f"{i+1}\n")
                    f.write(f"{start_time} --> {end_time}\n")
                    f.write(f"{timing['text']}\n\n")
            
            # Create channel name overlay image
            channel_overlay = os.path.join(temp_dir, "channel_overlay.png")
            self._create_channel_overlay(channel_overlay)
            
            # Create video title overlay image
            title_overlay = os.path.join(temp_dir, "title_overlay.png")
            self._create_title_overlay(title_overlay)
            
            # Use ffmpeg to create video with subtitles
            ffmpeg_cmd = [
                "ffmpeg", "-y",
                "-f", "concat",
                "-safe", "0",
                "-i", duration_file,
                "-i", audio_path,
                "-i", channel_overlay,
                "-i", title_overlay,
                "-filter_complex",
                f"[0:v]scale=1080:1920,fps=30[bg]; [bg][2:v]overlay=10:10[with_channel]; [with_channel][3:v]overlay=10:80[with_title]; [with_title]subtitles={subtitle_file}:force_style='FontSize=24,Alignment=10,BorderStyle=3,Outline=1,Shadow=0,MarginV=30'[v]",
                "-map", "[v]",
                "-map", "1:a",
                "-c:v", "libx264",
                "-c:a", "aac",
                "-shortest",
                "-pix_fmt", "yuv420p",
                output_path
            ]
            
            subprocess.run(ffmpeg_cmd, check=True)
            
            if get_verbose():
                print(f" => Created video with subtitles: {output_path}")
                
            return output_path
            
        except Exception as e:
            if get_verbose():
                print(f"Error creating video: {e}")
            return None
            
        finally:
            # Clean up temporary directory
            import shutil
            shutil.rmtree(temp_dir)
    
    def _format_time(self, seconds):
        """
        Format time in seconds to SRT format (HH:MM:SS,mmm)
        
        Args:
            seconds (float): Time in seconds
            
        Returns:
            str: Formatted time string
        """
        hours = int(seconds / 3600)
        minutes = int((seconds % 3600) / 60)
        seconds = seconds % 60
        milliseconds = int((seconds - int(seconds)) * 1000)
        return f"{hours:02d}:{minutes:02d}:{int(seconds):02d},{milliseconds:03d}"
    
    def _create_channel_overlay(self, output_path):
        """
        Create a channel name overlay image
        
        Args:
            output_path (str): Path to save the overlay image
        """
        # Use PIL to create a simple text overlay
        from PIL import Image, ImageDraw, ImageFont
        
        # Create a transparent image
        img = Image.new('RGBA', (500, 50), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Try to load a font, use default if not available
        try:
            font = ImageFont.truetype("Arial.ttf", 36)
        except:
            font = ImageFont.load_default()
        
        # Draw channel name with semi-transparent background
        draw.rectangle([(0, 0), (len(self.channel_name) * 20 + 20, 50)], fill=(0, 0, 0, 128))
        draw.text((10, 5), self.channel_name, fill=(255, 255, 255, 255), font=font)
        
        img.save(output_path)
    
    def _create_title_overlay(self, output_path):
        """
        Create a video title overlay image
        
        Args:
            output_path (str): Path to save the overlay image
        """
        # Use PIL to create a simple text overlay
        from PIL import Image, ImageDraw, ImageFont
        
        # Create a transparent image
        img = Image.new('RGBA', (1000, 50), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Try to load a font, use default if not available
        try:
            font = ImageFont.truetype("Arial.ttf", 28)
        except:
            font = ImageFont.load_default()
        
        # Draw title with semi-transparent background
        title_text = self.title if self.title else self.topic
        draw.rectangle([(0, 0), (len(title_text) * 15 + 20, 50)], fill=(0, 0, 0, 128))
        draw.text((10, 5), title_text, fill=(255, 255, 255, 255), font=font)
        
        img.save(output_path)
    
    def create_short(self):
        """
        Creates a Short from start to finish
        
        Returns:
            str: Path to the created video or None if failed
        """
        try:
            # Generate script if not already generated
            if not self.script:
                self.generate_script()
                
            # Generate metadata
            self.generate_metadata()
            
            # Generate image prompts
            self.generate_image_prompts()
            
            # Generate images
            self.generate_images()
            
            # Generate speech
            tts_instance = TTS()
            audio_path = self.generate_script_to_speech(tts_instance)
            
            if not audio_path:
                if get_verbose():
                    print("Failed to generate audio")
                return None
                
            # Create video with subtitles
            video_path = self.create_video_with_subtitles(audio_path)
            
            if not video_path:
                if get_verbose():
                    print("Failed to create video")
                return None
            
            return video_path
                
        except Exception as e:
            if get_verbose():
                print(f"Error creating short: {e}")
            return None
