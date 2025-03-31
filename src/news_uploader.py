import os
import json
import time
import logging
import argparse
from datetime import datetime, timedelta
import schedule

from news_crawler import NewsCrawler
from news_extractor import NewsExtractor
from sns_poster import SNSPoster

class NewsUploader:
    """
    Main class for crawling news and uploading to social networks.
    Integrates the NewsCrawler, NewsExtractor, and SNSPoster components.
    """
    def __init__(self, config_path=None):
        """
        Initialize the NewsUploader.
        
        Args:
            config_path (str): Path to configuration file
        """
        self.config_path = config_path
        self.config = self._load_config(config_path)
        
        # Set up logging
        self.logger = self._setup_logging()
        
        # Initialize components
        self.news_crawler = NewsCrawler(config_path)
        self.news_extractor = NewsExtractor(config_path)
        self.sns_poster = SNSPoster(config_path)
        
        # Create data directory
        self.data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".news_uploader")
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Initialize stats
        self.stats_file = os.path.join(self.data_dir, "uploader_stats.json")
        self.stats = self._load_stats()
    
    def _setup_logging(self):
        """
        Set up logging for the NewsUploader.
        
        Returns:
            logging.Logger: Configured logger
        """
        logger = logging.getLogger("NewsUploader")
        logger.setLevel(logging.INFO)
        
        # Create file handler
        log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".logs")
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, "news_uploader.log")
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.INFO)
        
        # Create console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Create formatter
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # Add handlers to logger
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
        return logger
    
    def _load_config(self, config_path):
        """
        Load configuration from file or use defaults.
        
        Args:
            config_path (str): Path to configuration file
            
        Returns:
            dict: Configuration dictionary
        """
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
                "cache_expiry_hours": 1
            },
            "extractor": {
                "min_article_length": 200,
                "extract_images": True,
                "summarize_content": True
            },
            "poster": {
                "platforms": ["twitter", "facebook"],
                "max_posts_per_day": 10,
                "min_interval_minutes": 30,
                "include_image": True
            },
            "scheduling": {
                "active_hours_start": "08:00",
                "active_hours_end": "22:00",
                "best_posting_times": ["08:00", "12:00", "17:00", "20:00"],
                "weekend_schedule": ["10:00", "14:00", "18:00"]
            }
        }
        
        if config_path and os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    user_config = json.load(f)
                    # Merge user config with defaults
                    for key, value in user_config.items():
                        if key in default_config and isinstance(value, dict):
                            default_config[key].update(value)
                        else:
                            default_config[key] = value
            except Exception as e:
                print(f"Error loading config file: {e}")
                
        return default_config
    
    def _load_stats(self):
        """
        Load statistics from file.
        
        Returns:
            dict: Statistics dictionary
        """
        if os.path.exists(self.stats_file):
            try:
                with open(self.stats_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                self.logger.error(f"Error loading stats: {e}")
                
        return {
            "total_articles_crawled": 0,
            "total_articles_extracted": 0,
            "total_posts": 0,
            "posts_by_platform": {},
            "posts_by_category": {},
            "last_run": None,
            "last_post": None,
            "runs": []
        }
    
    def _save_stats(self):
        """
        Save statistics to file.
        """
        try:
            with open(self.stats_file, 'w') as f:
                json.dump(self.stats, f, indent=2)
        except Exception as e:
            self.logger.error(f"Error saving stats: {e}")
    
    def _update_stats(self, run_stats):
        """
        Update statistics with results from a run.
        
        Args:
            run_stats (dict): Statistics from a run
        """
        # Update total counts
        self.stats["total_articles_crawled"] += run_stats.get("articles_crawled", 0)
        self.stats["total_articles_extracted"] += run_stats.get("articles_extracted", 0)
        self.stats["total_posts"] += run_stats.get("posts_successful", 0)
        
        # Update platform counts
        for platform, count in run_stats.get("posts_by_platform", {}).items():
            if platform in self.stats["posts_by_platform"]:
                self.stats["posts_by_platform"][platform] += count
            else:
                self.stats["posts_by_platform"][platform] = count
        
        # Update category counts
        for category, count in run_stats.get("posts_by_category", {}).items():
            if category in self.stats["posts_by_category"]:
                self.stats["posts_by_category"][category] += count
            else:
                self.stats["posts_by_category"][category] = count
        
        # Update timestamps
        self.stats["last_run"] = datetime.now().isoformat()
        if run_stats.get("posts_successful", 0) > 0:
            self.stats["last_post"] = datetime.now().isoformat()
        
        # Add run to history
        self.stats["runs"].append({
            "timestamp": datetime.now().isoformat(),
            "articles_crawled": run_stats.get("articles_crawled", 0),
            "articles_extracted": run_stats.get("articles_extracted", 0),
            "posts_successful": run_stats.get("posts_successful", 0),
            "posts_failed": run_stats.get("posts_failed", 0)
        })
        
        # Keep only the last 100 runs
        if len(self.stats["runs"]) > 100:
            self.stats["runs"] = self.stats["runs"][-100:]
        
        # Save updated stats
        self._save_stats()
    
    def crawl_and_post(self, categories=None, count=None, platforms=None):
        """
        Crawl news, extract content, and post to social networks.
        
        Args:
            categories (list): Optional list of categories to filter by
            count (int): Number of articles to post
            platforms (list): List of platforms to post to
            
        Returns:
            dict: Results dictionary
        """
        run_start_time = datetime.now()
        
        # Use configured values if not specified
        if categories is None:
            categories = self.config["general"]["categories"]
        
        if count is None:
            count = self.config["general"]["posts_per_run"]
        
        if platforms is None:
            platforms = self.config["poster"]["platforms"]
        
        # Initialize run statistics
        run_stats = {
            "articles_crawled": 0,
            "articles_extracted": 0,
            "posts_successful": 0,
            "posts_failed": 0,
            "posts_by_platform": {},
            "posts_by_category": {}
        }
        
        # Step 1: Crawl news articles
        self.logger.info(f"Crawling news for categories: {categories}")
        articles = self.news_crawler.crawl_news(categories=categories, max_articles=count*3)  # Get more than needed
        run_stats["articles_crawled"] = len(articles)
        
        if not articles:
            self.logger.warning("No articles found during crawling")
            self._update_stats(run_stats)
            return {
                "success": False,
                "error": "No articles found",
                "stats": run_stats
            }
        
        self.logger.info(f"Found {len(articles)} articles during crawling")
        
        # Step 2: Extract full content for each article
        extracted_articles = []
        for article in articles:
            # Skip articles that are too new or too old
            if "published" in article:
                try:
                    published_time = datetime.fromisoformat(article["published"])
                    now = datetime.now()
                    
                    # Check if article is too new
                    min_age_minutes = self.config["general"]["min_article_age_minutes"]
                    article_age_minutes = (now - published_time).total_seconds() / 60
                    if article_age_minutes < min_age_minutes:
                        self.logger.info(f"Skipping article that is too new: {article['title']} ({article_age_minutes:.1f} minutes old)")
                        continue
                    
                    # Check if article is too old
                    max_age_hours = self.config["general"]["max_article_age_hours"]
                    article_age_hours = article_age_minutes / 60
                    if article_age_hours > max_age_hours:
                        self.logger.info(f"Skipping article that is too old: {article['title']} ({article_age_hours:.1f} hours old)")
                        continue
                except Exception as e:
                    self.logger.error(f"Error parsing article date: {e}")
            
            # Extract full content
            self.logger.info(f"Extracting content for: {article['title']}")
            extracted_article = self.news_extractor.extract_article_content(article["url"])
            
            if extracted_article:
                # Merge the crawled article data with the extracted content
                for key, value in article.items():
                    if key not in extracted_article:
                        extracted_article[key] = value
                
                extracted_articles.append(extracted_article)
                run_stats["articles_extracted"] += 1
                
                # Stop if we have enough articles
                if len(extracted_articles) >= count:
                    break
        
        if not extracted_articles:
            self.logger.warning("No articles successfully extracted")
            self._update_stats(run_stats)
            return {
                "success": False,
                "error": "No articles successfully extracted",
                "stats": run_stats
            }
        
        self.logger.info(f"Successfully extracted content for {len(extracted_articles)} articles")
        
        # Step 3: Post articles to social networks
        post_results = []
        for article in extracted_articles[:count]:  # Limit to requested count
            self.logger.info(f"Posting article: {article['title']}")
            result = self.sns_poster.post_article(article, platforms)
            
            # Track statistics
            success = any(r.get("success", False) for r in result.values())
            if success:
                run_stats["posts_successful"] += 1
                
                # Track by platform
                for platform, platform_result in result.items():
                    if platform_result.get("success", False):
                        if platform in run_stats["posts_by_platform"]:
                            run_stats["posts_by_platform"][platform] += 1
                        else:
                            run_stats["posts_by_platform"][platform] = 1
                
                # Track by category
                if "categories" in article:
                    for category in article["categories"]:
                        if category in run_stats["posts_by_category"]:
                            run_stats["posts_by_category"][category] += 1
                        else:
                            run_stats["posts_by_category"][category] = 1
            else:
                run_stats["posts_failed"] += 1
            
            post_results.append({
                "article": {
                    "id": article.get("id", ""),
                    "title": article["title"],
                    "url": article["url"]
                },
                "results": result,
                "success": success
            })
        
        # Update statistics
        self._update_stats(run_stats)
        
        # Calculate run duration
        run_duration = (datetime.now() - run_start_time).total_seconds()
        
        return {
            "success": run_stats["posts_successful"] > 0,
            "articles_crawled": run_stats["articles_crawled"],
            "articles_extracted": run_stats["articles_extracted"],
            "posts_successful": run_stats["posts_successful"],
            "posts_failed": run_stats["posts_failed"],
            "post_results": post_results,
            "run_duration_seconds": run_duration
        }
    
    def schedule_daily_posts(self, categories=None, posts_per_day=None, platforms=None):
        """
        Schedule posts throughout the day.
        
        Args:
            categories (list): Optional list of categories to filter by
            posts_per_day (int): Number of posts to schedule per day
            platforms (list): List of platforms to post to
            
        Returns:
            dict: Schedule dictionary
        """
        # Use configured values if not specified
        if categories is None:
            categories = self.config["general"]["categories"]
        
        if posts_per_day is None:
            posts_per_day = self.config["poster"]["max_posts_per_day"]
        
        if platforms is None:
            platforms = self.config["poster"]["platforms"]
        
        # Step 1: Crawl news articles
        self.logger.info(f"Crawling news for scheduling, categories: {categories}")
        articles = self.news_crawler.crawl_news(categories=categories, max_articles=posts_per_day*2)
        
        if not articles:
            self.logger.warning("No articles found for scheduling")
            return {
                "success": False,
                "error": "No articles found",
                "schedule": None
            }
        
        self.logger.info(f"Found {len(articles)} articles for scheduling")
        
        # Step 2: Extract full content for each article
        extracted_articles = []
        for article in articles:
            # Extract full content
            self.logger.info(f"Extracting content for scheduling: {article['title']}")
            extracted_article = self.news_extractor.extract_article_content(article["url"])
            
            if extracted_article:
                # Merge the crawled article data with the extracted content
                for key, value in article.items():
                    if key not in extracted_article:
                        extracted_article[key] = value
                
                extracted_articles.append(extracted_article)
                
                # Stop if we have enough articles
                if len(extracted_articles) >= posts_per_day:
                    break
        
        if not extracted_articles:
            self.logger.warning("No articles successfully extracted for scheduling")
            return {
                "success": False,
                "error": "No articles successfully extracted",
                "schedule": None
            }
        
        self.logger.info(f"Successfully extracted content for {len(extracted_articles)} articles for scheduling")
        
        # Step 3: Create schedule
        schedule = self.sns_poster.schedule_posts(extracted_articles, platforms)
        
        return {
            "success": True,
            "schedule": schedule
        }
    
    def run_scheduled_posting(self):
        """
        Run scheduled posting based on the current schedule.
        
        Returns:
            dict: Results dictionary
        """
        # Get the current schedule
        schedule_result = self.schedule_daily_posts()
        
        if not schedule_result["success"]:
            self.logger.warning("Failed to create schedule for posting")
            return {
                "success": False,
                "error": "Failed to create schedule",
                "results": None
            }
        
        schedule = schedule_result["schedule"]
        
        # Run the scheduled posting
        self.logger.info(f"Running scheduled posting with {len(schedule['posts'])} posts")
        results = self.sns_poster.run_scheduled_posting(schedule)
        
        # Update statistics
        run_stats = {
            "articles_crawled": len(schedule["posts"]),
            "articles_extracted": len(schedule["posts"]),
            "posts_successful": results["posted"],
            "posts_failed": results["failed"],
            "posts_by_platform": {},
            "posts_by_category": {}
        }
        
        # Track by platform
        for post_result in results["posts"]:
            if post_result["success"]:
                for platform in post_result.get("results", {}).keys():
                    if platform in run_stats["posts_by_platform"]:
                        run_stats["posts_by_platform"][platform] += 1
                    else:
                        run_stats["posts_by_platform"][platform] = 1
        
        self._update_stats(run_stats)
        
        return {
            "success": results["posted"] > 0,
            "results": results
        }
    
    def get_trending_topics(self, count=5):
        """
        Get trending topics from news.
        
        Args:
            count (int): Number of trending topics to return
            
        Returns:
            list: List of trending topic dictionaries
        """
        return self.news_crawler.get_trending_topics(count)
    
    def search_news(self, query, max_articles=10):
        """
        Search for news articles.
        
        Args:
            query (str): Search query
            max_articles (int): Maximum number of articles to return
            
        Returns:
            list: List of article dictionaries
        """
        return self.news_crawler.search_news(query, max_articles)
    
    def get_stats(self):
        """
        Get uploader statistics.
        
        Returns:
            dict: Statistics dictionary
        """
        return self.stats
    
    def get_all_component_stats(self):
        """
        Get statistics from all components.
        
        Returns:
            dict: Combined statistics dictionary
        """
        return {
            "uploader": self.stats,
            "crawler": self.news_crawler.get_trending_topics(3),  # As a sample of crawler data
            "extractor": self.news_extractor.get_extraction_stats(),
            "poster": self.sns_poster.get_posting_stats()
        }
    
    def start_scheduler(self, interval_minutes=None):
        """
        Start the scheduler to run at regular intervals.
        
        Args:
            interval_minutes (int): Interval between runs in minutes
            
        Returns:
            None
        """
        if interval_minutes is None:
            interval_minutes = self.config["general"]["run_interval_minutes"]
        
        self.logger.info(f"Starting scheduler with {interval_minutes} minute intervals")
        
        # Schedule the job
        schedule.every(interval_minutes).minutes.do(self.crawl_and_post)
        
        # Run the scheduler
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
        except KeyboardInterrupt:
            self.logger.info("Scheduler stopped by user")
        except Exception as e:
            self.logger.error(f"Error in scheduler: {e}")


def main():
    """
    Main function to run the NewsUploader from command line.
    """
    parser = argparse.ArgumentParser(description='News Uploader - Crawl news and post to social networks')
    parser.add_argument('--config', type=str, help='Path to configuration file')
    parser.add_argument('--run', action='store_true', help='Run once and exit')
    parser.add_argument('--schedule', action='store_true', help='Run scheduler')
    parser.add_argument('--interval', type=int, help='Interval between runs in minutes')
    parser.add_argument('--categories', type=str, help='Comma-separated list of categories')
    parser.add_argument('--count', type=int, help='Number of articles to post')
    parser.add_argument('--platforms', type=str, help='Comma-separated list of platforms')
    parser.add_argument('--trending', action='store_true', help='Get trending topics')
    parser.add_argument('--search', type=str, help='Search query')
    parser.add_argument('--stats', action='store_true', help='Get statistics')
    
    args = parser.parse_args()
    
    # Create uploader
    uploader = NewsUploader(args.config)
    
    # Parse arguments
    categories = args.categories.split(',') if args.categories else None
    platforms = args.platforms.split(',') if args.platforms else None
    
    # Run requested action
    if args.run:
        results = uploader.crawl_and_post(categories, args.count, platforms)
        print(json.dumps(results, indent=2))
    elif args.schedule:
        uploader.start_scheduler(args.interval)
    elif args.trending:
        trending = uploader.get_trending_topics(5)
        print(json.dumps(trending, indent=2))
    elif args.search:
        articles = uploader.search_news(args.search, 10)
        print(json.dumps(articles, indent=2))
    elif args.stats:
        stats = uploader.get_all_component_stats()
        print(json.dumps(stats, indent=2))
    else:
        # Default: run once
        results = uploader.crawl_and_post(categories, args.count, platforms)
        print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
