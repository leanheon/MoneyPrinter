#!/usr/bin/env python3

import os
import sys
import json
import argparse
import logging
from datetime import datetime

# Import required components
try:
    from src.news_crawler import NewsCrawler
    from src.news_extractor import NewsExtractor
    from src.sns_poster import SNSPoster
    from src.news_uploader import NewsUploader
except ImportError:
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from src.news_crawler import NewsCrawler
    from src.news_extractor import NewsExtractor
    from src.sns_poster import SNSPoster
    from src.news_uploader import NewsUploader

def setup_logging():
    """Set up logging configuration"""
    log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
    os.makedirs(log_dir, exist_ok=True)
    
    log_file = os.path.join(log_dir, f"news_sns_{datetime.now().strftime('%Y%m%d')}.log")
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    
    return logging.getLogger("news_sns_main")

def create_default_config():
    """Create default configuration file if it doesn't exist"""
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")
    
    if not os.path.exists(config_path):
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
        
        with open(config_path, 'w') as f:
            json.dump(default_config, f, indent=2)
        
        return config_path
    
    return config_path

def main():
    """Main function to run the News SNS Uploader"""
    logger = setup_logging()
    logger.info("Starting News SNS Uploader")
    
    # Create default config if it doesn't exist
    default_config_path = create_default_config()
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='News SNS Uploader - Crawl news and post to social networks')
    parser.add_argument('--config', type=str, default=default_config_path, help='Path to configuration file')
    parser.add_argument('--run', action='store_true', help='Run once and exit')
    parser.add_argument('--schedule', action='store_true', help='Run scheduler')
    parser.add_argument('--interval', type=int, help='Interval between runs in minutes')
    parser.add_argument('--categories', type=str, help='Comma-separated list of categories')
    parser.add_argument('--count', type=int, help='Number of articles to post')
    parser.add_argument('--platforms', type=str, help='Comma-separated list of platforms')
    parser.add_argument('--trending', action='store_true', help='Get trending topics')
    parser.add_argument('--search', type=str, help='Search query')
    parser.add_argument('--stats', action='store_true', help='Get statistics')
    parser.add_argument('--setup', action='store_true', help='Run interactive setup')
    
    args = parser.parse_args()
    
    # Run interactive setup if requested
    if args.setup:
        logger.info("Running interactive setup")
        print("\n=== News SNS Uploader Setup ===\n")
        print("This will help you configure the News SNS Uploader.")
        print("Press Enter to accept default values shown in [brackets].\n")
        
        # Load existing config if available
        config = {}
        if os.path.exists(args.config):
            try:
                with open(args.config, 'r') as f:
                    config = json.load(f)
            except Exception as e:
                logger.error(f"Error loading config file: {e}")
                config = {}
        
        # General settings
        print("\n== General Settings ==")
        interval = input(f"Run interval in minutes [{config.get('general', {}).get('run_interval_minutes', 60)}]: ")
        if interval:
            config.setdefault('general', {})['run_interval_minutes'] = int(interval)
        
        posts_per_run = input(f"Posts per run [{config.get('general', {}).get('posts_per_run', 2)}]: ")
        if posts_per_run:
            config.setdefault('general', {})['posts_per_run'] = int(posts_per_run)
        
        # Twitter settings
        print("\n== Twitter Settings ==")
        twitter_enabled = input("Enable Twitter posting? (y/n) [n]: ").lower() == 'y'
        
        if twitter_enabled:
            config.setdefault('poster', {}).setdefault('platforms_config', {}).setdefault('twitter', {})['enabled'] = True
            
            api_key = input("Twitter API Key: ")
            if api_key:
                config['poster']['platforms_config']['twitter']['api_key'] = api_key
            
            api_secret = input("Twitter API Secret: ")
            if api_secret:
                config['poster']['platforms_config']['twitter']['api_secret'] = api_secret
            
            access_token = input("Twitter Access Token: ")
            if access_token:
                config['poster']['platforms_config']['twitter']['access_token'] = access_token
            
            token_secret = input("Twitter Token Secret: ")
            if token_secret:
                config['poster']['platforms_config']['twitter']['token_secret'] = token_secret
            
            # Update platforms list
            if 'twitter' not in config.setdefault('poster', {}).setdefault('platforms', []):
                config['poster']['platforms'].append('twitter')
        
        # Facebook settings
        print("\n== Facebook Settings ==")
        facebook_enabled = input("Enable Facebook posting? (y/n) [n]: ").lower() == 'y'
        
        if facebook_enabled:
            config.setdefault('poster', {}).setdefault('platforms_config', {}).setdefault('facebook', {})['enabled'] = True
            
            page_id = input("Facebook Page ID: ")
            if page_id:
                config['poster']['platforms_config']['facebook']['page_id'] = page_id
            
            access_token = input("Facebook Access Token: ")
            if access_token:
                config['poster']['platforms_config']['facebook']['access_token'] = access_token
            
            # Update platforms list
            if 'facebook' not in config.setdefault('poster', {}).setdefault('platforms', []):
                config['poster']['platforms'].append('facebook')
        
        # Save config
        try:
            with open(args.config, 'w') as f:
                json.dump(config, f, indent=2)
            print(f"\nConfiguration saved to {args.config}")
        except Exception as e:
            logger.error(f"Error saving config file: {e}")
            print(f"\nError saving configuration: {e}")
        
        print("\nSetup complete. You can now run the News SNS Uploader.")
        return
    
    # Create uploader
    try:
        uploader = NewsUploader(args.config)
    except Exception as e:
        logger.error(f"Error creating uploader: {e}")
        print(f"Error: {e}")
        print("Run with --setup to configure the uploader.")
        return
    
    # Parse arguments
    categories = args.categories.split(',') if args.categories else None
    platforms = args.platforms.split(',') if args.platforms else None
    
    # Run requested action
    try:
        if args.run:
            logger.info("Running once with command line arguments")
            results = uploader.crawl_and_post(categories, args.count, platforms)
            print(json.dumps(results, indent=2))
        elif args.schedule:
            logger.info(f"Starting scheduler with interval {args.interval or uploader.config['general']['run_interval_minutes']} minutes")
            uploader.start_scheduler(args.interval)
        elif args.trending:
            logger.info("Getting trending topics")
            trending = uploader.get_trending_topics(5)
            print(json.dumps(trending, indent=2))
        elif args.search:
            logger.info(f"Searching for: {args.search}")
            articles = uploader.search_news(args.search, 10)
            print(json.dumps(articles, indent=2))
        elif args.stats:
            logger.info("Getting statistics")
            stats = uploader.get_all_component_stats()
            print(json.dumps(stats, indent=2))
        else:
            # Default: run once
            logger.info("Running once with default settings")
            results = uploader.crawl_and_post(categories, args.count, platforms)
            print(json.dumps(results, indent=2))
    except Exception as e:
        logger.error(f"Error running uploader: {e}")
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
