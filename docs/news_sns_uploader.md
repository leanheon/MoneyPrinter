# News SNS Uploader Documentation

## Overview

The News SNS Uploader is a comprehensive system for automatically crawling the internet for news articles, extracting their content, and posting them to various social networking services (SNS). This system enables automated news sharing across multiple platforms with minimal manual intervention.

## Architecture

The system consists of four main components:

1. **NewsUploader** (`news_uploader.py`): The main integration component that coordinates the entire process.

2. **NewsCrawler** (`news_crawler.py`): Responsible for finding and collecting news articles from various sources.

3. **NewsExtractor** (`news_extractor.py`): Extracts and processes the content from news articles.

4. **SNSPoster** (`sns_poster.py`): Handles posting content to social networking services.

## Features

- **Automated News Crawling**: Collects news from multiple sources including RSS feeds
- **Content Extraction**: Extracts article text, images, metadata, and performs NLP analysis
- **Multi-Platform Posting**: Supports Twitter, Facebook, LinkedIn, and Instagram
- **Scheduling**: Intelligent scheduling of posts at optimal times
- **Customizable Categories**: Filter news by categories of interest
- **Trending Topics**: Identifies and tracks trending news topics
- **Statistics Tracking**: Comprehensive statistics on crawling, extraction, and posting
- **Command-Line Interface**: Easy to use from the command line

## Installation

1. Clone the repository or extract the provided zip file
2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

This command installs Flask along with the rest of the dependencies.

3. Configure the system by creating a configuration file (see Configuration section)

## Configuration

The system uses a JSON configuration file with the following structure:

```json
{
  "general": {
    "run_interval_minutes": 60,
    "posts_per_run": 2,
    "categories": ["technology", "business", "politics", "health", "science", "sports", "entertainment", "world"],
    "preferred_categories": ["technology", "business"],
    "min_article_age_minutes": 10,
    "max_article_age_hours": 24,
    "auto_schedule": true
  },
  "crawler": {
    "max_sources_per_run": 3,
    "max_articles_per_source": 5,
    "cache_expiry_hours": 1
  },
  "extractor": {
    "min_article_length": 200,
    "extract_images": true,
    "summarize_content": true
  },
  "poster": {
    "platforms": ["twitter", "facebook"],
    "max_posts_per_day": 10,
    "min_interval_minutes": 30,
    "include_image": true
  },
  "scheduling": {
    "active_hours_start": "08:00",
    "active_hours_end": "22:00",
    "best_posting_times": ["08:00", "12:00", "17:00", "20:00"],
    "weekend_schedule": ["10:00", "14:00", "18:00"]
  }
}
```

### Platform-Specific Configuration

For each social media platform, you'll need to provide API credentials:

#### Twitter
```json
{
  "platforms": {
    "twitter": {
      "enabled": true,
      "api_key": "YOUR_API_KEY",
      "api_secret": "YOUR_API_SECRET",
      "access_token": "YOUR_ACCESS_TOKEN",
      "token_secret": "YOUR_TOKEN_SECRET"
    }
  }
}
```

#### Facebook
```json
{
  "platforms": {
    "facebook": {
      "enabled": true,
      "page_id": "YOUR_PAGE_ID",
      "access_token": "YOUR_ACCESS_TOKEN"
    }
  }
}
```

## Usage

### Command Line Interface

The system can be run from the command line with various options:

```bash
# Run once with default settings
python news_uploader.py

# Run with a specific configuration file
python news_uploader.py --config config.json

# Run with specific categories and platforms
python news_uploader.py --categories technology,business --platforms twitter,facebook

# Run as a scheduler
python news_uploader.py --schedule --interval 30

# Get trending topics
python news_uploader.py --trending

# Search for news
python news_uploader.py --search "artificial intelligence"

# Get statistics
python news_uploader.py --stats
```

### As a Python Module

You can also use the system as a Python module in your own code:

```python
from news_uploader import NewsUploader

# Create uploader with configuration
uploader = NewsUploader("config.json")

# Crawl news and post to social networks
results = uploader.crawl_and_post(
    categories=["technology", "business"],
    count=3,
    platforms=["twitter", "facebook"]
)

# Schedule posts throughout the day
schedule = uploader.schedule_daily_posts()

# Get trending topics
trending = uploader.get_trending_topics(count=5)

# Search for news
articles = uploader.search_news("artificial intelligence", max_articles=10)

# Get statistics
stats = uploader.get_stats()
```

## Component Details

### NewsUploader

The main integration component that coordinates the entire process:

- Initializes and manages all other components
- Provides high-level methods for crawling and posting
- Handles scheduling and statistics tracking
- Provides command-line interface

### NewsCrawler

Responsible for finding and collecting news articles:

- Crawls multiple news sources via RSS feeds
- Caches articles to avoid duplicates
- Filters articles by category
- Identifies trending topics
- Provides search functionality

### NewsExtractor

Extracts and processes content from news articles:

- Extracts article text, title, author, and publication date
- Cleans HTML content
- Extracts images and related links
- Generates article summaries
- Performs NLP processing (keywords, entities, sentiment)

### SNSPoster

Handles posting content to social networking services:

- Formats posts for different platforms
- Handles image uploading
- Manages posting schedules
- Tracks posting history
- Implements error handling and retries

## Workflow

1. **Crawling**: The system crawls configured news sources to find recent articles
2. **Filtering**: Articles are filtered by category, age, and relevance
3. **Extraction**: Full content is extracted from selected articles
4. **Formatting**: Content is formatted for each target platform
5. **Posting**: Formatted content is posted to social networks
6. **Tracking**: Results are tracked and statistics are updated

## Best Practices

1. **Posting Frequency**: Limit posts to 5-10 per day to avoid overwhelming followers
2. **Optimal Timing**: Schedule posts during peak engagement hours (typically 8-9am, 12-1pm, 5-6pm)
3. **Content Variety**: Include a mix of categories to maintain audience interest
4. **Image Inclusion**: Always include images when possible for higher engagement
5. **Attribution**: Always include source attribution for news articles
6. **Hashtags**: Use relevant hashtags but limit to 2-3 per post

## Troubleshooting

### Common Issues

1. **API Rate Limiting**
   - Reduce posting frequency
   - Increase min_interval_minutes in configuration
   - Check platform-specific rate limits

2. **Content Extraction Failures**
   - Check if the source website blocks scrapers
   - Try increasing request_delay in configuration
   - Rotate user agents more frequently

3. **Scheduling Issues**
   - Verify system time is correct
   - Check for conflicting scheduled tasks
   - Ensure best_posting_times are properly formatted

## Extending the System

### Adding New News Sources

To add new news sources, modify the `news_sources` section in the configuration:

```json
"news_sources": [
  {
    "name": "New Source Name",
    "rss_url": "https://example.com/feed.xml",
    "type": "rss"
  }
]
```

### Adding New Social Platforms

To add support for a new social platform:

1. Add platform configuration in the `platforms` section
2. Implement a new posting method in the SNSPoster class
3. Update the post_article method to use the new platform

## Monitoring and Maintenance

- Check the log files regularly for errors and warnings
- Monitor posting statistics to ensure the system is working correctly
- Update API credentials when necessary
- Periodically review and update news sources

## Future Enhancements

Planned enhancements for future versions:

1. AI-driven content selection based on engagement metrics
2. Enhanced image generation for posts without images
3. A/B testing of post formats and timing
4. Web interface for monitoring and configuration
5. Support for additional social platforms
6. Advanced analytics dashboard

---

*This documentation was last updated on March 31, 2025*
