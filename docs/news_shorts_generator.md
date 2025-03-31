# News-Based Shorts Generator

This document provides detailed information about the News-Based Shorts Generator functionality that has been added to the MoneyPrinter Enhanced project. This feature allows you to automatically create short-form videos from current news articles.

## Overview

The News-Based Shorts Generator extends the existing ShortsGenerator system to create engaging short-form videos from news content. It automatically:

1. Fetches news articles from various sources
2. Extracts and processes article content
3. Generates scripts tailored to different news categories
4. Creates appropriate visuals and audio
5. Produces complete short-form videos ready for posting

## Key Components

The system consists of several integrated components:

### 1. News Crawler (`news_crawler.py`)
- Fetches news from RSS feeds and other sources
- Categorizes articles by topic
- Tracks trending news topics
- Provides search functionality for specific news

### 2. News Extractor (`news_extractor.py`)
- Extracts full content from news articles
- Processes text, images, and metadata
- Summarizes content for short-form video scripts
- Handles different news site formats

### 3. News Shorts Template System (`news_shorts_template.py`)
- Provides templates for different news categories
- Customizes presentation based on news type
- Includes specialized templates for:
  - Breaking news
  - Tech news
  - Business news
  - Entertainment
  - Sports
  - Feature stories
  - Explainer content

### 4. News Shorts Generator (`NewsShortsGenerator.py`)
- Extends the base ShortsGenerator class
- Integrates all components
- Generates complete news-based shorts
- Supports various customization options

### 5. Command-Line Interface (`generate_news_shorts.py`)
- User-friendly interface for generating news shorts
- Supports various command-line options
- Provides helpful information and feedback

## Usage

You can generate news-based shorts using the command-line interface:

```bash
python generate_news_shorts.py [options]
```

### Options

- `--topic TEXT`: Specify a news topic to search for
- `--category TEXT`: Specify a news category (technology, business, sports, etc.)
- `--template TEXT`: Specify a template type (breaking_news, tech_news, etc.)
- `--url TEXT`: Use a specific news article URL
- `--trending`: Use a trending news topic
- `--list-categories`: List available news categories
- `--list-templates`: List available template types

### Examples

Generate a short about technology news:
```bash
python generate_news_shorts.py --category technology
```

Generate a short using a trending topic:
```bash
python generate_news_shorts.py --trending
```

Generate a short about a specific topic using the breaking news template:
```bash
python generate_news_shorts.py --topic "climate change" --template breaking_news
```

Generate a short from a specific news article:
```bash
python generate_news_shorts.py --url "https://example.com/news-article"
```

## Template Types

The system supports various template types for different kinds of news:

1. **Breaking News**: Urgent, time-sensitive news with emphasis on immediacy
2. **Explainer**: Educational content that breaks down complex topics
3. **Feature Story**: Human interest stories with narrative focus
4. **Tech News**: Technology news with focus on innovation and impact
5. **Business News**: Business and financial news with relevant data
6. **Entertainment**: Celebrity and entertainment news with engaging presentation
7. **Sports**: Sports news with dynamic, action-oriented presentation

## News Categories

The system supports various news categories:

1. **Technology**: Tech news, innovations, digital trends
2. **Business**: Business, economy, finance, markets
3. **Politics**: Political news, government, elections
4. **Health**: Health and medical news
5. **Science**: Scientific discoveries and research
6. **Sports**: Sports news and events
7. **Entertainment**: Entertainment and celebrity news
8. **World**: International and global news

## Technical Details

### Integration with Existing System

The News-Based Shorts Generator is fully integrated with the existing ShortsGenerator system. It extends the base ShortsGenerator class and inherits all its functionality while adding news-specific features.

### Customization

The system is highly customizable through configuration files. You can modify:

- News sources and RSS feeds
- Template styles and formats
- Visual presentation for different news types
- Script generation parameters
- Content extraction settings

### Performance

The system is designed to be efficient and can generate a complete news-based short in a few minutes, depending on the complexity of the content and the quality of the generated images.

## Troubleshooting

If you encounter issues:

1. Check the logs in the `logs` directory
2. Ensure you have internet connectivity for fetching news
3. Verify that all dependencies are installed
4. Try using a different news category or template

## Future Enhancements

Potential future enhancements include:

1. Support for more news sources
2. Additional template types
3. Enhanced visual effects for news presentation
4. Automated posting to social media platforms
5. Scheduled news shorts generation

## Conclusion

The News-Based Shorts Generator provides a powerful way to create engaging short-form videos from current news content. It's fully integrated with the existing ShortsGenerator system and offers a wide range of customization options to suit different needs and preferences.
