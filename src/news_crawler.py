import os
import json
import time
import requests
import feedparser
import hashlib
import logging
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
import re

class NewsCrawler:
    """
    Class for crawling news from various sources.
    """
    def __init__(self, config_path=None):
        """
        Initialize the NewsCrawler.
        
        Args:
            config_path (str): Path to configuration file
        """
        self.config = self._load_config(config_path)
        self.cache_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".cache")
        os.makedirs(self.cache_dir, exist_ok=True)
        
        # Set up logging
        self.logger = self._setup_logging()
        
        # Initialize cache
        self.cache_file = os.path.join(self.cache_dir, "news_cache.json")
        self.cache = self._load_cache()
        
        # Initialize trending topics
        self.trending_file = os.path.join(self.cache_dir, "trending_topics.json")
        self.trending = self._load_trending()
    
    def _setup_logging(self):
        """
        Set up logging for the NewsCrawler.
        
        Returns:
            logging.Logger: Configured logger
        """
        logger = logging.getLogger("NewsCrawler")
        logger.setLevel(logging.INFO)
        
        # Create file handler
        log_file = os.path.join(self.cache_dir, "news_crawler.log")
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
            "crawler": {
                "max_sources_per_run": 5,
                "max_articles_per_source": 10,
                "request_timeout": 10,
                "request_delay": 1,
                "user_agents": [
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
                    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36"
                ],
                "cache_expiry_hours": 24,
                "news_sources": [
                    {
                        "name": "BBC News",
                        "rss_url": "http://feeds.bbci.co.uk/news/rss.xml",
                        "type": "rss",
                        "categories": ["general", "world"]
                    },
                    {
                        "name": "CNN",
                        "rss_url": "http://rss.cnn.com/rss/edition.rss",
                        "type": "rss",
                        "categories": ["general", "world"]
                    },
                    {
                        "name": "Reuters Technology",
                        "rss_url": "http://feeds.reuters.com/reuters/technologyNews",
                        "type": "rss",
                        "categories": ["technology"]
                    },
                    {
                        "name": "TechCrunch",
                        "rss_url": "https://techcrunch.com/feed/",
                        "type": "rss",
                        "categories": ["technology"]
                    },
                    {
                        "name": "BBC Business",
                        "rss_url": "http://feeds.bbci.co.uk/news/business/rss.xml",
                        "type": "rss",
                        "categories": ["business"]
                    }
                ]
            },
            "categories": {
                "technology": ["tech", "technology", "digital", "software", "hardware", "ai", "artificial intelligence", "gadgets"],
                "business": ["business", "economy", "finance", "market", "stock", "investment"],
                "politics": ["politics", "government", "election", "policy", "political"],
                "health": ["health", "medical", "medicine", "disease", "healthcare", "wellness"],
                "science": ["science", "research", "scientific", "discovery", "space", "physics"],
                "sports": ["sports", "sport", "football", "soccer", "basketball", "baseball", "tennis"],
                "entertainment": ["entertainment", "movie", "film", "music", "celebrity", "tv", "television"],
                "world": ["world", "international", "global", "foreign"]
            },
            "trending": {
                "update_interval_hours": 6,
                "min_mentions": 3,
                "decay_factor": 0.9,
                "max_topics": 20
            }
        }
        
        if config_path and os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    user_config = json.load(f)
                    # Merge user config with defaults
                    if "crawler" in user_config:
                        for key, value in user_config["crawler"].items():
                            default_config["crawler"][key] = value
                    if "categories" in user_config:
                        for key, value in user_config["categories"].items():
                            default_config["categories"][key] = value
                    if "trending" in user_config:
                        for key, value in user_config["trending"].items():
                            default_config["trending"][key] = value
            except Exception as e:
                self.logger.error(f"Error loading config file: {e}")
                
        return default_config
    
    def _load_cache(self):
        """
        Load cache from file.
        
        Returns:
            dict: Cache dictionary
        """
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                self.logger.error(f"Error loading cache: {e}")
                
        return {"articles": {}, "last_updated": datetime.now().isoformat()}
    
    def _save_cache(self):
        """
        Save cache to file.
        """
        try:
            with open(self.cache_file, 'w') as f:
                json.dump(self.cache, f, indent=2)
        except Exception as e:
            self.logger.error(f"Error saving cache: {e}")
    
    def _load_trending(self):
        """
        Load trending topics from file.
        
        Returns:
            dict: Trending topics dictionary
        """
        if os.path.exists(self.trending_file):
            try:
                with open(self.trending_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                self.logger.error(f"Error loading trending topics: {e}")
                
        return {"topics": {}, "last_updated": datetime.now().isoformat()}
    
    def _save_trending(self):
        """
        Save trending topics to file.
        """
        try:
            with open(self.trending_file, 'w') as f:
                json.dump(self.trending, f, indent=2)
        except Exception as e:
            self.logger.error(f"Error saving trending topics: {e}")
    
    def _clean_cache(self):
        """
        Clean expired items from cache.
        """
        now = datetime.now()
        expiry_hours = self.config["crawler"]["cache_expiry_hours"]
        expiry_time = now - timedelta(hours=expiry_hours)
        
        # Convert to ISO format for comparison
        expiry_time_iso = expiry_time.isoformat()
        
        # Filter out expired articles
        expired_keys = []
        for key, article in self.cache["articles"].items():
            if article["timestamp"] < expiry_time_iso:
                expired_keys.append(key)
        
        # Remove expired articles
        for key in expired_keys:
            del self.cache["articles"][key]
        
        # Update last updated timestamp
        self.cache["last_updated"] = now.isoformat()
        
        # Save updated cache
        self._save_cache()
        
        self.logger.info(f"Cleaned {len(expired_keys)} expired items from cache")
    
    def _update_trending_topics(self, articles):
        """
        Update trending topics based on new articles.
        
        Args:
            articles (list): List of article dictionaries
        """
        now = datetime.now()
        last_updated = datetime.fromisoformat(self.trending["last_updated"])
        update_interval = self.config["trending"]["update_interval_hours"]
        
        # Check if it's time to update trending topics
        if (now - last_updated).total_seconds() / 3600 < update_interval and self.trending["topics"]:
            return
        
        # Apply decay factor to existing topics
        decay_factor = self.config["trending"]["decay_factor"]
        for topic, data in self.trending["topics"].items():
            data["score"] *= decay_factor
        
        # Extract topics from articles
        for article in articles:
            # Extract topics from title and description
            title = article.get("title", "")
            description = article.get("description", "")
            
            # Combine title and description for topic extraction
            text = f"{title} {description}"
            
            # Extract potential topics (simple approach)
            words = re.findall(r'\b[A-Z][a-z]+\b', text)  # Capitalized words
            phrases = re.findall(r'\b[A-Z][a-z]+ [A-Z][a-z]+\b', text)  # Capitalized phrases
            
            # Process words
            for word in words:
                if len(word) < 4:  # Skip short words
                    continue
                    
                if word.lower() in ["this", "that", "these", "those", "there", "their", "about", "would", "should", "could"]:
                    continue  # Skip common words
                
                # Add or update topic
                if word in self.trending["topics"]:
                    self.trending["topics"][word]["count"] += 1
                    self.trending["topics"][word]["score"] += 1
                else:
                    self.trending["topics"][word] = {
                        "count": 1,
                        "score": 1,
                        "first_seen": now.isoformat()
                    }
            
            # Process phrases (weighted higher)
            for phrase in phrases:
                # Add or update topic
                if phrase in self.trending["topics"]:
                    self.trending["topics"][phrase]["count"] += 1
                    self.trending["topics"][phrase]["score"] += 2  # Higher weight for phrases
                else:
                    self.trending["topics"][phrase] = {
                        "count": 1,
                        "score": 2,  # Higher initial score for phrases
                        "first_seen": now.isoformat()
                    }
            
            # Extract categories as topics
            if "categories" in article:
                for category in article["categories"]:
                    if category in self.trending["topics"]:
                        self.trending["topics"][category]["count"] += 1
                        self.trending["topics"][category]["score"] += 0.5  # Lower weight for categories
                    else:
                        self.trending["topics"][category] = {
                            "count": 1,
                            "score": 0.5,  # Lower initial score for categories
                            "first_seen": now.isoformat()
                        }
        
        # Remove topics with low counts
        min_mentions = self.config["trending"]["min_mentions"]
        low_count_topics = [topic for topic, data in self.trending["topics"].items() if data["count"] < min_mentions]
        for topic in low_count_topics:
            del self.trending["topics"][topic]
        
        # Update last updated timestamp
        self.trending["last_updated"] = now.isoformat()
        
        # Save updated trending topics
        self._save_trending()
        
        self.logger.info(f"Updated trending topics with {len(self.trending['topics'])} topics")
    
    def _get_random_user_agent(self):
        """
        Get a random user agent from the configured list.
        
        Returns:
            str: User agent string
        """
        user_agents = self.config["crawler"]["user_agents"]
        return user_agents[hash(datetime.now().isoformat()) % len(user_agents)]
    
    def _parse_rss_feed(self, source):
        """
        Parse an RSS feed and extract articles.
        
        Args:
            source (dict): Source dictionary with RSS URL
            
        Returns:
            list: List of article dictionaries
        """
        articles = []
        
        try:
            # Parse the RSS feed
            feed = feedparser.parse(source["rss_url"])
            
            # Extract articles
            for entry in feed.entries:
                # Create article ID
                article_id = hashlib.md5(entry.link.encode()).hexdigest()
                
                # Skip if already in cache
                if article_id in self.cache["articles"]:
                    continue
                
                # Extract publication date
                published = None
                if hasattr(entry, "published_parsed"):
                    published = datetime(*entry.published_parsed[:6]).isoformat()
                elif hasattr(entry, "updated_parsed"):
                    published = datetime(*entry.updated_parsed[:6]).isoformat()
                
                # Extract categories
                categories = []
                if hasattr(entry, "tags"):
                    categories = [tag.term for tag in entry.tags] if hasattr(entry, "tags") else []
                
                # Add source categories
                if "categories" in source:
                    categories.extend(source["categories"])
                
                # Remove duplicates
                categories = list(set(categories))
                
                # Create article dictionary
                article = {
                    "id": article_id,
                    "title": entry.title,
                    "description": entry.summary if hasattr(entry, "summary") else "",
                    "url": entry.link,
                    "published": published,
                    "source": source["name"],
                    "categories": categories,
                    "timestamp": datetime.now().isoformat()
                }
                
                # Add to articles list
                articles.append(article)
                
                # Add to cache
                self.cache["articles"][article_id] = article
        
        except Exception as e:
            self.logger.error(f"Error parsing RSS feed {source['rss_url']}: {e}")
        
        return articles
    
    def _categorize_article(self, article):
        """
        Categorize an article based on its content.
        
        Args:
            article (dict): Article dictionary
            
        Returns:
            list: List of categories
        """
        # If article already has categories, use those
        if "categories" in article and article["categories"]:
            return article["categories"]
        
        # Extract text for categorization
        text = f"{article.get('title', '')} {article.get('description', '')}"
        text = text.lower()
        
        # Check each category
        categories = []
        for category, keywords in self.config["categories"].items():
            for keyword in keywords:
                if keyword.lower() in text:
                    categories.append(category)
                    break
        
        return list(set(categories))
    
    def crawl_news(self, categories=None, max_articles=None):
        """
        Crawl news from configured sources.
        
        Args:
            categories (list): Optional list of categories to filter by
            max_articles (int): Maximum number of articles to return
            
        Returns:
            list: List of article dictionaries
        """
        # Clean expired items from cache
        self._clean_cache()
        
        # Use default values if not specified
        if max_articles is None:
            max_articles = self.config["crawler"]["max_sources_per_run"] * self.config["crawler"]["max_articles_per_source"]
        
        # Get sources to crawl
        sources = self.config["crawler"]["news_sources"]
        
        # Filter sources by category if specified
        if categories:
            filtered_sources = []
            for source in sources:
                source_categories = source.get("categories", [])
                if any(category in categories for category in source_categories):
                    filtered_sources.append(source)
            sources = filtered_sources
        
        # Limit number of sources
        max_sources = self.config["crawler"]["max_sources_per_run"]
        sources = sources[:max_sources]
        
        # Crawl each source
        all_articles = []
        for source in sources:
            self.logger.info(f"Crawling source: {source['name']}")
            
            # Parse based on source type
            if source["type"] == "rss":
                articles = self._parse_rss_feed(source)
            else:
                self.logger.warning(f"Unsupported source type: {source['type']}")
                continue
            
            # Add to all articles
            all_articles.extend(articles)
            
            # Delay between requests
            time.sleep(self.config["crawler"]["request_delay"])
        
        # Save updated cache
        self._save_cache()
        
        # Update trending topics
        self._update_trending_topics(all_articles)
        
        # Filter by category if specified
        if categories:
            filtered_articles = []
            for article in all_articles:
                article_categories = self._categorize_article(article)
                if any(category in categories for category in article_categories):
                    filtered_articles.append(article)
            all_articles = filtered_articles
        
        # Sort by publication date (newest first)
        all_articles.sort(key=lambda x: x.get("published", ""), reverse=True)
        
        # Limit number of articles
        all_articles = all_articles[:max_articles]
        
        return all_articles
    
    def get_trending_topics(self, count=10):
        """
        Get trending topics.
        
        Args:
            count (int): Number of topics to return
            
        Returns:
            list: List of trending topic dictionaries
        """
        # Sort topics by score
        sorted_topics = sorted(self.trending["topics"].items(), key=lambda x: x[1]["score"], reverse=True)
        
        # Limit to requested count
        max_topics = min(count, self.config["trending"]["max_topics"])
        top_topics = sorted_topics[:max_topics]
        
        # Format results
        results = []
        for topic, data in top_topics:
            results.append({
                "topic": topic,
                "count": data["count"],
                "score": data["score"],
                "first_seen": data["first_seen"]
            })
        
        return results
    
    def search_news(self, query, max_articles=10):
        """
        Search for news articles.
        
        Args:
            query (str): Search query
            max_articles (int): Maximum number of articles to return
            
        Returns:
            list: List of article dictionaries
        """
        query = query.lower()
        results = []
        
        # Search in cache
        for article_id, article in self.cache["articles"].items():
            title = article.get("title", "").lower()
            description = article.get("description", "").lower()
            
            if query in title or query in description:
                results.append(article)
        
        # Sort by relevance (simple approach: query in title is more relevant)
        def relevance_score(article):
            title = article.get("title", "").lower()
            description = article.get("description", "").lower()
            
            score = 0
            if query in title:
                score += 2
            if query in description:
                score += 1
                
            # Boost recent articles
            if "published" in article:
                try:
                    published = datetime.fromisoformat(article["published"])
                    now = datetime.now()
                    hours_ago = (now - published).total_seconds() / 3600
                    if hours_ago < 24:
                        score += 1
                    elif hours_ago < 48:
                        score += 0.5
                except:
                    pass
            
            return score
        
        results.sort(key=relevance_score, reverse=True)
        
        # Limit to requested count
        results = results[:max_articles]
        
        return results


# Example usage
if __name__ == "__main__":
    # Create a news crawler
    crawler = NewsCrawler()
    
    # Crawl news
    articles = crawler.crawl_news(categories=["technology"], max_articles=5)
    
    # Print articles
    for article in articles:
        print(f"Title: {article['title']}")
        print(f"Source: {article['source']}")
        print(f"URL: {article['url']}")
        print(f"Published: {article['published']}")
        print(f"Categories: {article['categories']}")
        print()
    
    # Get trending topics
    trending = crawler.get_trending_topics(5)
    print("Trending Topics:")
    for topic in trending:
        print(f"{topic['topic']} (Score: {topic['score']:.2f}, Count: {topic['count']})")
    
    # Search for news
    results = crawler.search_news("technology", 3)
    print("\nSearch Results:")
    for article in results:
        print(f"Title: {article['title']}")
        print(f"URL: {article['url']}")
        print()
