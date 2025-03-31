# MoneyPrinter V2 - Enhanced Features Documentation

## Overview

This document provides information about the new features added to the MoneyPrinter V2 project:

1. **Chuu Shorts Generator** - Create YouTube Shorts with subtitles, TTS, and AI-generated images
2. **Blog Post Generator** - Generate and publish blog posts with AI-generated content and images
3. **Google Sheets Integration** - Manage content creation through spreadsheets

## 1. Chuu Shorts Generator

The Chuu Shorts Generator creates engaging YouTube Shorts with subtitles, text-to-speech (TTS), and AI-generated images. It supports two types of shorts:

### Story-based Shorts
- Features anime-style AI-generated images
- Includes subtitles synchronized with TTS audio
- Shows channel name and video title overlays
- Creates engaging narrative content

### Knowledge-based Shorts
- Features informative AI-generated images
- Includes subtitles synchronized with TTS audio
- Shows channel name and video title overlays
- Creates educational content explaining curious facts

### How to Use

1. From the main dashboard, click "Generate Content"
2. Select "Chuu Shorts" as the platform
3. Enter a topic or use the "Generate Random Topic" button
4. Choose between "Story-based Short" or "Knowledge-based Short"
5. Click "Generate Content"
6. Review the generated script and metadata
7. Click "Create Short" to produce the final video

## 2. Blog Post Generator

The Blog Post Generator creates comprehensive blog posts with AI-generated content and featured images.

### Features
- Generates SEO-friendly blog titles
- Creates structured blog content with HTML formatting
- Generates high-quality featured images using DALL-E
- Supports different content lengths (short, medium, long)
- Saves blog posts as HTML files with images

### How to Use

1. From the main dashboard, click "Generate Content"
2. Select "Blog Post" as the platform
3. Enter a topic or use the "Generate Random Topic" button
4. Choose the desired blog length
5. Click "Generate Content"
6. Review the generated blog post and featured image
7. Click "Publish Blog Post" to save and publish

## 3. Google Sheets Integration

The Google Sheets integration allows you to manage content creation through spreadsheets, enabling batch processing and tracking of content.

### Features
- Connect to existing Google Sheets
- Create template spreadsheets for content management
- Add content items to be processed
- Process pending content items in batch
- Track content status and results

### How to Use

1. From the main dashboard, click "Google Sheets"
2. Connect to an existing spreadsheet or create a new template
3. Add content items with topics, types, and optional scripts
4. Click "Process Pending" to generate all pending content
5. View results and status updates in the spreadsheet

### Spreadsheet Structure

The template spreadsheet includes the following columns:
- Topic: The main topic for content generation
- Type: Content type (shorts, blog)
- Script: Optional pre-written script
- Title: Generated title (filled automatically)
- Description: Generated description (filled automatically)
- Keywords: Generated keywords (filled automatically)
- Status: Current status (pending, completed, failed)
- URL: URL to published content (filled automatically)
- Date Created: When the item was added
- Date Published: When the item was published

## Integration with Existing Features

All new features are fully integrated with the existing MoneyPrinter V2 system:

- The Chuu Shorts Generator uses the same OpenAI integration as other content types
- The Blog Post Generator leverages existing monetization options
- The Google Sheets integration works with all content types including original YouTube, Twitter, and Threads content

## Technical Requirements

- Python 3.6+
- OpenAI API key
- Google API credentials (for Sheets integration)
- FFmpeg (for video generation)
- Flask (for web interface)

## Configuration

Configure the new features in the Settings page:

1. OpenAI API key for content and image generation
2. Google API credentials path for Sheets integration
3. Spreadsheet ID or name for automatic connection

## Troubleshooting

- If shorts generation fails, check that FFmpeg is properly installed
- For Google Sheets integration issues, verify your credentials and permissions
- If image generation fails, check your OpenAI API key and quota
