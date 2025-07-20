# MoneyPrinter - Automated Content Creation System

## Overview

MoneyPrinter is a comprehensive automated content creation system designed to help content creators, marketers, and entrepreneurs generate and monetize content across multiple platforms. The system leverages AI to create high-quality content including YouTube shorts, blog posts, social media content, and more.

## Key Features

### Content Generation

- **YouTube Shorts Generator**: Create engaging YouTube shorts with AI-generated images, subtitles, and text-to-speech
  - Story-based shorts with narrative content
  - Knowledge-based shorts with educational content
  - Custom shorts with user-provided images

- **Blog Post Generator**: Create comprehensive blog posts with AI-generated content and featured images
  - Multiple length options (short, medium, long)
  - SEO-friendly titles and content
  - Featured image generation

- **Social Media Content**:
  - X (Twitter) posts with optional images
  - Threads posts with multi-post threads
  - Instagram posts (single images, carousels, stories)
  - Card news format for information delivery

### Integration & Automation

- **Google Sheets Integration**: Manage content creation through spreadsheets
  - Template creation for content management
  - Batch processing of content items
  - Status tracking and reporting

- **Dropbox Integration**: Automatically upload generated content
  - Upload shorts videos to Dropbox
  - Upload images and card news to Dropbox
  - Generate and store shareable links

- **Control Center**: Centralized dashboard for managing all content creation
  - Monitor content creation status
  - Track performance metrics
  - Manage settings and configurations

### Monetization

- **Affiliate Marketing**: Integrate affiliate links into content
- **Sponsorships**: Add sponsorship content to videos and posts
- **Digital Products**: Create and sell digital products
- **Ebook Generation**: Convert content into ebooks for sale

## Getting Started

### Installation

1. Clone the repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
   This will install Flask and all other required packages.
3. Set up API keys in the configuration file

### Configuration

1. OpenAI API Key: Required for content generation and image creation
2. Google API Credentials: Required for Google Sheets integration
3. Dropbox API Token: Required for Dropbox integration

### Usage

#### Web Interface

1. Start the web server:
   ```
   python app.py
   ```
2. Access the web interface at `http://localhost:5000`
3. Navigate to the desired content generation tool

#### Command Line

Basic content generation:
```
python -m src.cli generate --type shorts --topic "Interesting Facts About Space"
```

Process pending items from Google Sheets:
```
python -m src.cli process_pending
```

## Content Types

### YouTube Shorts

MoneyPrinter supports three methods of shorts creation:

1. **Story-based Shorts**: Creates engaging narrative shorts with AI-generated anime-style images, subtitles, and TTS audio. Perfect for storytelling and entertainment content.

2. **Knowledge-based Shorts**: Creates educational shorts with informative images, subtitles, and TTS audio. Ideal for explaining curious facts and educational content.

3. **Custom Shorts**: Uses user-provided images with generated script, subtitles, and TTS audio. Gives you more control over the visual elements while automating the rest.

All shorts include:
- Channel name and video title overlays
- Synchronized subtitles with TTS audio
- Background music
- Automatic metadata generation (title, description, tags)
- Optional Dropbox upload

### Blog Posts

The blog post generator creates comprehensive articles with:
- SEO-optimized titles and headings
- Well-structured content with introduction, body, and conclusion
- AI-generated featured images
- HTML formatting for easy publishing
- Multiple length options

### Social Media Content

#### X (Twitter)
- Text posts with optional images
- Optimized for engagement and shareability
- Hashtag suggestions

#### Threads
- Multi-post threads for longer content
- Image support for each post
- Narrative flow across posts

#### Instagram
- Single image posts with captions
- Carousel posts with multiple images
- Story format posts
- Card news format for information delivery

### Card News Generator

The card news generator creates visual information cards for social media:
- Multiple cards that flow together to tell a story
- Various style options (modern, minimal, colorful)
- Text overlay on high-quality images
- Perfect for Instagram, Facebook, and other visual platforms

## Google Sheets Integration

The KyuGle spreadsheet integration allows you to:
1. Create template spreadsheets for content management
2. Add content items with topics, types, and optional scripts
3. Process pending content items in batch
4. Track content status and results

### Spreadsheet Structure

The template spreadsheet includes:
- Topic: The main topic for content generation
- Type: Content type (shorts, blog, social, etc.)
- Method: Method for shorts (story, knowledge, custom)
- Script: Optional pre-written script
- Title: Generated title (filled automatically)
- Description: Generated description (filled automatically)
- Keywords: Generated keywords (filled automatically)
- Status: Current status (pending, completed, failed)
- URL: URL to published content (filled automatically)
- Dropbox Link: Link to uploaded content (filled automatically)
- Date Created: When the item was added
- Date Published: When the item was published

## Dropbox Integration

All generated content can be automatically uploaded to Dropbox:
- Videos are uploaded to appropriate folders based on content type
- Images and card news are organized in their own folders
- Shareable links are generated and stored in the spreadsheet
- Folder structure is automatically created

## Control Center

The control center provides a centralized dashboard for:
- Monitoring content creation status
- Tracking performance metrics
- Managing settings and configurations
- Viewing and editing content items
- Processing pending content

## Extending MoneyPrinter

MoneyPrinter is designed to be modular and extensible:
1. Add new content types by creating new generator classes
2. Integrate with additional platforms by extending the social media manager
3. Add new monetization methods by creating new monetization classes
4. Customize the web interface to suit your needs

## Requirements

- Python 3.6+
- Install Python packages from `requirements.txt`
- OpenAI API key
- FFmpeg (for video generation)
- Google API credentials (for Sheets integration)
- Dropbox API token (for Dropbox integration)
- Flask (for web interface)

## License

This project is licensed under the MIT License - see the LICENSE file for details.
