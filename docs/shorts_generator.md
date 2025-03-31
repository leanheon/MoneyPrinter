# Shorts Generator Documentation

## Overview

The Shorts Generator is a comprehensive system for creating engaging short-form video content with AI-generated scripts, visuals, and audio. It's designed to automate the creation of viral-style short videos for platforms like YouTube Shorts, TikTok, and Instagram Reels.

## Architecture

The Shorts Generator consists of two main components:

1. **ShortsGenerator Class** (`src/classes/ShortsGenerator.py`): The core class that handles script generation, metadata creation, and basic short video assembly.

2. **EnhancedShorts Class** (`src/enhanced_shorts.py`): An extended implementation that adds advanced features like multiple creation methods, custom image integration, and platform-specific optimizations.

## ShortsGenerator Class

### Key Features

- Script generation based on topic
- Metadata creation (title, description, tags)
- Basic short video assembly
- Support for knowledge-based and story-based shorts

### Class Structure

```python
class ShortsGenerator:
    def __init__(self, topic, is_knowledge=False):
        # Initialize with topic and content type
        
    def generate_script(self):
        # Generate script based on topic and type
        
    def generate_metadata(self):
        # Generate title, description, and tags
        
    def create_short(self):
        # Create the short video
        
    def generate_images(self):
        # Generate images for the short
        
    def create_audio(self):
        # Create audio for the short
        
    def assemble_video(self):
        # Assemble the final video
```

### Workflow

1. Initialize with a topic and content type (knowledge or story)
2. Generate a script using AI
3. Generate metadata (title, description, tags)
4. Generate images based on the script
5. Create audio narration from the script
6. Assemble the final video

### Example Usage

```python
from src.classes.ShortsGenerator import ShortsGenerator

# Create a story-based short
shorts_generator = ShortsGenerator("productivity tips", is_knowledge=False)
shorts_generator.generate_script()
shorts_generator.generate_metadata()
video_path = shorts_generator.create_short()

print(f"Video created at: {video_path}")
print(f"Title: {shorts_generator.title}")
print(f"Description: {shorts_generator.description}")
```

## EnhancedShorts Class

### Key Features

- Multiple creation methods (story, knowledge, review, custom)
- Integration with Dropbox for sharing
- Advanced image generation and selection
- Enhanced metadata optimization
- Platform-specific formatting

### Class Structure

```python
class EnhancedShorts:
    def __init__(self, dropbox_token=None):
        # Initialize with optional Dropbox token
        
    def create_short_by_method(self, method, topic, script=None, custom_images=None, upload_to_dropbox=False):
        # Create a short using the specified method
        
    def _create_story_short(self, topic, script=None, custom_images=None):
        # Create a narrative-driven short
        
    def _create_knowledge_short(self, topic, script=None, custom_images=None):
        # Create an educational short
        
    def _create_review_short(self, topic, script=None, custom_images=None):
        # Create a product/service review short
        
    def _create_custom_short(self, topic, script, custom_images=None):
        # Create a short with custom script and optional images
        
    def upload_to_dropbox(self, file_path):
        # Upload the video to Dropbox and return a sharing link
```

### Creation Methods

1. **Story Method**: Creates narrative-driven shorts with a beginning, middle, and end. Ideal for emotional or inspirational content.

2. **Knowledge Method**: Creates educational shorts that explain concepts or share facts. Optimized for clear information delivery.

3. **Review Method**: Creates product or service review shorts with pros and cons. Structured for comparison and evaluation.

4. **Custom Method**: Creates shorts based on custom scripts and images. Provides maximum flexibility.

### Workflow

1. Choose a creation method based on content goals
2. Provide a topic and optional custom script/images
3. The system generates any missing components (script, images)
4. The short is assembled with method-specific optimizations
5. Optionally upload to Dropbox for sharing

### Example Usage

```python
from src.enhanced_shorts import EnhancedShorts

# Initialize with Dropbox token (optional)
enhanced_shorts = EnhancedShorts(dropbox_token="your_dropbox_token")

# Create a knowledge-based short
result = enhanced_shorts.create_short_by_method(
    method="knowledge",
    topic="how blockchain works",
    script=None,  # Auto-generate script
    custom_images=None,  # Auto-generate images
    upload_to_dropbox=True
)

print(f"Video created at: {result['video_path']}")
print(f"Title: {result['title']}")
print(f"Dropbox link: {result['dropbox_link']}")
```

## Integration with Other Components

The Shorts Generator integrates with several other components in the MoneyPrinter system:

1. **Content Manager**: Uses the Shorts Generator to create content based on spreadsheet data.

2. **Channel Manager**: Leverages the Shorts Generator to create channel-specific content with consistent branding.

3. **Integrated Content Manager**: Combines the Shorts Generator with other content types for comprehensive content strategies.

4. **Automation Manager**: Schedules and automates the creation of shorts based on configured schedules.

## Technical Details

### Script Generation

Scripts are generated using OpenAI's GPT models with carefully crafted prompts that vary based on the content type:

- **Story scripts** focus on narrative structure with a hook, development, and conclusion
- **Knowledge scripts** prioritize clear explanation with an introduction, main points, and summary
- **Review scripts** follow a structured format with introduction, pros, cons, and recommendation

### Image Generation

Images are created using either:
- AI image generation (DALL-E or similar models)
- Selection from a curated image library
- Custom images provided by the user

### Audio Creation

Audio narration is created using:
- Text-to-speech technology
- Background music selection based on content mood
- Audio mixing for professional quality

### Video Assembly

Videos are assembled using:
- FFmpeg for video processing
- Image-to-video conversion with transitions
- Audio-visual synchronization
- Platform-specific aspect ratios and formatting

## Performance Considerations

- Script generation typically takes 5-15 seconds
- Image generation can take 10-30 seconds per image
- Audio creation takes 5-20 seconds depending on length
- Video assembly takes 15-60 seconds depending on complexity
- Total process typically completes in 1-3 minutes

## Best Practices

1. **Topics**: Use specific, trending topics for better engagement
2. **Scripts**: Keep scripts concise (60-90 seconds when narrated)
3. **Hooks**: Ensure the first 3 seconds are attention-grabbing
4. **Visuals**: Use high-contrast, emotionally engaging images
5. **Calls to Action**: Include clear CTAs at the end of videos
6. **Metadata**: Use keyword-rich titles and descriptions

## Troubleshooting

### Common Issues

1. **Script Generation Failures**
   - Check OpenAI API status
   - Verify topic is appropriate and specific
   - Try a different creation method

2. **Image Generation Issues**
   - Check image API status
   - Provide more specific image descriptions
   - Use custom images as a fallback

3. **Video Assembly Problems**
   - Verify FFmpeg installation
   - Check disk space
   - Ensure all dependencies are installed

## Future Enhancements

Planned enhancements for future versions:

1. Additional creation methods (e.g., tutorial, reaction)
2. More platform-specific optimizations
3. Enhanced analytics integration
4. A/B testing for script and visual variations
5. Automated content repurposing

---

*This documentation was last updated on March 31, 2025*
