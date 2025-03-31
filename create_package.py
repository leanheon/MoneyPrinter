#!/usr/bin/env python3

import os
import sys
import argparse
import json

def create_requirements_file():
    """Create requirements.txt file"""
    requirements = [
        "requests>=2.25.1",
        "beautifulsoup4>=4.9.3",
        "feedparser>=6.0.8",
        "tweepy>=4.10.0",
        "facebook-sdk>=3.1.0",
        "schedule>=1.1.0",
        "python-dateutil>=2.8.2"
    ]
    
    with open("requirements.txt", "w") as f:
        f.write("\n".join(requirements))
    
    return "requirements.txt"

def create_readme():
    """Create README.md file"""
    readme = """# News SNS Uploader

A comprehensive system for automatically crawling the internet for news articles, extracting their content, and posting them to various social networking services (SNS).

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

3. Configure the system by running the setup:

```bash
python news_sns_uploader.py --setup
```

## Quick Start

```bash
# Run once with default settings
python news_sns_uploader.py

# Run with specific categories and platforms
python news_sns_uploader.py --categories technology,business --platforms twitter,facebook

# Run as a scheduler
python news_sns_uploader.py --schedule --interval 30

# Get trending topics
python news_sns_uploader.py --trending

# Search for news
python news_sns_uploader.py --search "artificial intelligence"
```

## Documentation

For detailed documentation, see the `docs` directory:

- [News SNS Uploader Documentation](docs/news_sns_uploader.md)
- [Shorts Generator Documentation](docs/shorts_generator.md)
- [Ebook Generator Documentation](docs/ebook_generator.md)
- [Monetization Modules Documentation](docs/monetization_modules.md)
- [Automation Manager Documentation](docs/automation_manager.md)
- [Integration Components Documentation](docs/integration_components.md)

## License

This project is licensed under the MIT License - see the LICENSE file for details.
"""
    
    with open("README.md", "w") as f:
        f.write(readme)
    
    return "README.md"

def create_license():
    """Create LICENSE file"""
    license_text = """MIT License

Copyright (c) 2025 MoneyPrinter Enhanced

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
    
    with open("LICENSE", "w") as f:
        f.write(license_text)
    
    return "LICENSE"

def main():
    """Main function to create package files"""
    parser = argparse.ArgumentParser(description='Create package files for News SNS Uploader')
    parser.add_argument('--dir', type=str, default='.', help='Directory to create files in')
    
    args = parser.parse_args()
    
    # Change to specified directory
    os.chdir(args.dir)
    
    # Create files
    requirements_file = create_requirements_file()
    readme_file = create_readme()
    license_file = create_license()
    
    print(f"Created {requirements_file}")
    print(f"Created {readme_file}")
    print(f"Created {license_file}")
    
    # Create directories if they don't exist
    os.makedirs("logs", exist_ok=True)
    os.makedirs("images", exist_ok=True)
    
    print("Created logs directory")
    print("Created images directory")
    
    # Create default config if it doesn't exist
    if not os.path.exists("config.json"):
        default_config = {
            "general": {
                "run_interval_minutes": 60,
                "posts_per_run": 2,
                "categories": ["technology", "business", "politics", "health", "science", "sports", "entertainment", "world"],
                "preferred_categories": ["technology", "business"],
                "min_article_age_minutes": 10,
                "max_article_age_hours": 24,
                "auto_schedule": True
            },
            "crawler": {
                "max_sources_per_run": 3,
                "max_articles_per_source": 5,
                "cache_expiry_hours": 1,
                "news_sources": [
                    {
                        "name": "BBC News",
                        "rss_url": "http://feeds.bbci.co.uk/news/rss.xml",
                        "type": "rss"
                    },
                    {
                        "name": "CNN",
                        "rss_url": "http://rss.cnn.com/rss/edition.rss",
                        "type": "rss"
                    },
                    {
                        "name": "Reuters",
                        "rss_url": "http://feeds.reuters.com/reuters/topNews",
                        "type": "rss"
                    }
                ]
            },
            "extractor": {
                "min_article_length": 200,
                "extract_images": True,
                "summarize_content": True
            },
            "poster": {
                "platforms": ["twitter"],
                "max_posts_per_day": 10,
                "min_interval_minutes": 30,
                "include_image": True,
                "platforms_config": {
                    "twitter": {
                        "enabled": True,
                        "api_key": "",
                        "api_secret": "",
                        "access_token": "",
                        "token_secret": ""
                    },
                    "facebook": {
                        "enabled": False,
                        "page_id": "",
                        "access_token": ""
                    }
                }
            },
            "scheduling": {
                "active_hours_start": "08:00",
                "active_hours_end": "22:00",
                "best_posting_times": ["08:00", "12:00", "17:00", "20:00"],
                "weekend_schedule": ["10:00", "14:00", "18:00"]
            }
        }
        
        with open("config.json", "w") as f:
            json.dump(default_config, f, indent=2)
        
        print("Created default config.json")
    
    print("\nPackage files created successfully!")

if __name__ == "__main__":
    main()
