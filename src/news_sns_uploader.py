import os
import json
import time
import requests
import feedparser
from bs4 import BeautifulSoup
from datetime import datetime
from urllib.parse import urlparse
import random
import hashlib
import re

class NewsCrawler:
    """
    Class for crawling the internet for news articles from various sources.
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
        
        # Initialize cache
        self.cache_file = os.path.join(self.cache_dir, "news_cache.json")
        self.cache = self._load_cache()
        
        # User agent rotation to avoid blocking
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36"
        ]
        
    def _load_config(self, config_path):
        """
        Load configuration from file or use defaults.
        
        Args:
            config_path (str): Path to configuration file
            
        Returns:
            dict: Configuration dictionary
        """
        default_config = {
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
                    "rss_url": "https://www.reutersagency.com/feed/",
                    "type": "rss"
                },
                {
                    "name": "New York Times",
                    "rss_url": "https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml",
                    "type": "rss"
                },
                {
                    "name": "The Guardian",
                    "rss_url": "https://www.theguardian.com/international/rss",
                    "type": "rss"
                }
            ],
            "categories": [
                "technology", "business", "politics", "health", 
                "science", "sports", "entertainment", "world"
            ],
            "max_articles_per_source": 5,
            "cache_expiry_hours": 1,
            "request_delay": 2,  # Delay between requests in seconds
            "extract_images": True,
            "min_article_length": 200,  # Minimum article length in characters
            "max_retries": 3,
            "timeout": 10  # Request timeout in seconds
        }
        
        if config_path and os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    user_config = json.load(f)
                    # Merge user config with defaults
                    for key, value in user_config.items():
                        default_config[key] = value
            except Exception as e:
                print(f"Error loading config file: {e}")
                
        return default_config
    
    def _load_cache(self):
        """
        Load the news cache from file.
        
        Returns:
            dict: Cache dictionary
        """
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading cache: {e}")
                
        return {"articles": {}, "last_updated": datetime.now().isoformat()}
    
    def _save_cache(self):
        """
        Save the news cache to file.
        """
        try:
            with open(self.cache_file, 'w') as f:
                json.dump(self.cache, f, indent=2)
        except Exception as e:
            print(f"Error saving cache: {e}")
    
    def _get_random_user_agent(self):
        """
        Get a random user agent to avoid detection.
        
        Returns:
            str: Random user agent string
        """
        return random.choice(self.user_agents)
    
    def _make_request(self, url, headers=None, retries=0):
        """
        Make an HTTP request with retry logic.
        
        Args:
            url (str): URL to request
            headers (dict): Optional headers
            retries (int): Current retry count
            
        Returns:
            requests.Response: Response object or None if failed
        """
        if retries >= self.config["max_retries"]:
            print(f"Max retries reached for {url}")
            return None
            
        if not headers:
            headers = {
                "User-Agent": self._get_random_user_agent(),
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1"
            }
            
        try:
            response = requests.get(url, headers=headers, timeout=self.config["timeout"])
            
            # Add delay to avoid rate limiting
            time.sleep(self.config["request_delay"])
            
            if response.status_code == 200:
                return response
            elif response.status_code in [429, 503]:  # Rate limited or service unavailable
                print(f"Rate limited or service unavailable for {url}. Retrying...")
                time.sleep(self.config["request_delay"] * 2)  # Longer delay for rate limiting
                return self._make_request(url, headers, retries + 1)
            else:
                print(f"Request failed with status code {response.status_code} for {url}")
                return None
                
        except requests.RequestException as e:
            print(f"Request error for {url}: {e}")
            return self._make_request(url, headers, retries + 1)
    
    def _parse_rss_feed(self, source):
        """
        Parse an RSS feed for news articles.
        
        Args:
            source (dict): Source configuration
            
        Returns:
            list: List of article dictionaries
        """
        articles = []
        
        try:
            feed = feedparser.parse(source["rss_url"])
            
            for entry in feed.entries[:self.config["max_articles_per_source"]]:
                # Create a unique ID for the article
                article_id = hashlib.md5(entry.link.encode()).hexdigest()
                
                # Check if article is already in cache
                if article_id in self.cache["articles"]:
                    # Check if the article was updated
                    if "published" in entry and entry.published == self.cache["articles"][article_id].get("published"):
                        articles.append(self.cache["articles"][article_id])
                        continue
                
                article = {
                    "id": article_id,
                    "title": entry.title,
                    "url": entry.link,
                    "source": source["name"],
                    "published": entry.get("published", datetime.now().isoformat()),
                    "summary": entry.get("summary", ""),
                    "categories": []
                }
                
                # Extract categories if available
                if "tags" in entry:
                    article["categories"] = [tag.term for tag in entry.tags]
                
                # Fetch full article content
                article_content = self._extract_article_content(entry.link)
                if article_content:
                    article.update(article_content)
                    
                    # Only add articles that meet minimum length
                    if len(article.get("content", "")) >= self.config["min_article_length"]:
                        articles.append(article)
                        # Update cache
                        self.cache["articles"][article_id] = article
                
        except Exception as e:
            print(f"Error parsing RSS feed {source['name']}: {e}")
            
        return articles
    
    def _extract_article_content(self, url):
        """
        Extract the full content of an article from its URL.
        
        Args:
            url (str): Article URL
            
        Returns:
            dict: Article content dictionary or None if extraction failed
        """
        response = self._make_request(url)
        if not response:
            return None
            
        try:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style", "nav", "footer", "header", "aside"]):
                script.decompose()
                
            # Extract main content
            # This is a simple approach and might need to be customized for different sites
            main_content = None
            
            # Try common content containers
            content_candidates = soup.select("article, .article, .content, .post, main, #content, .story, .entry-content")
            if content_candidates:
                main_content = content_candidates[0]
            else:
                # Fallback to largest div by content length
                divs = soup.find_all("div")
                if divs:
                    main_content = max(divs, key=lambda x: len(x.get_text()))
            
            if not main_content:
                return None
                
            # Extract text content
            paragraphs = main_content.find_all("p")
            content = "\n\n".join([p.get_text().strip() for p in paragraphs])
            
            # Extract main image if available
            image_url = None
            if self.config["extract_images"]:
                # Try meta tags first
                og_image = soup.find("meta", property="og:image")
                if og_image and og_image.get("content"):
                    image_url = og_image["content"]
                else:
                    # Try article images
                    images = main_content.find_all("img")
                    if images:
                        # Find largest image by checking width/height attributes
                        largest_image = None
                        max_size = 0
                        
                        for img in images:
                            width = img.get("width")
                            height = img.get("height")
                            
                            if width and height:
                                try:
                                    size = int(width) * int(height)
                                    if size > max_size:
                                        max_size = size
                                        largest_image = img
                                except ValueError:
                                    continue
                        
                        if not largest_image and images:
                            largest_image = images[0]
                            
                        if largest_image and largest_image.get("src"):
                            image_url = largest_image["src"]
                            
                            # Handle relative URLs
                            if image_url.startswith("/"):
                                parsed_url = urlparse(url)
                                image_url = f"{parsed_url.scheme}://{parsed_url.netloc}{image_url}"
            
            # Extract author if available
            author = None
            author_meta = soup.find("meta", property="article:author")
            if author_meta and author_meta.get("content"):
                author = author_meta["content"]
            else:
                author_elements = soup.select(".author, .byline, .meta-author")
                if author_elements:
                    author = author_elements[0].get_text().strip()
            
            return {
                "content": content,
                "image_url": image_url,
                "author": author
            }
            
        except Exception as e:
            print(f"Error extracting article content from {url}: {e}")
            return None
    
    def _clean_cache(self):
        """
        Clean expired entries from the cache.
        """
        now = datetime.now()
        expiry_hours = self.config["cache_expiry_hours"]
        
        # Filter out expired articles
        new_cache = {}
        for article_id, article in self.cache["articles"].items():
            try:
                published_date = datetime.fromisoformat(article["published"])
                hours_diff = (now - published_date).total_seconds() / 3600
                
                if hours_diff <= expiry_hours:
                    new_cache[article_id] = article
            except (ValueError, KeyError):
                # If we can't parse the date, keep the article for now
                new_cache[article_id] = article
        
        self.cache["articles"] = new_cache
        self.cache["last_updated"] = now.isoformat()
        self._save_cache()
    
    def crawl_news(self, categories=None, max_articles=20):
        """
        Crawl news from configured sources.
        
        Args:
            categories (list): Optional list of categories to filter by
            max_articles (int): Maximum number of articles to return
            
        Returns:
            list: List of article dictionaries
        """
        # Clean cache before crawling
        self._clean_cache()
        
        all_articles = []
        
        for source in self.config["news_sources"]:
            if source["type"] == "rss":
                articles = self._parse_rss_feed(source)
                all_articles.extend(articles)
        
        # Filter by categories if specified
        if categories:
            filtered_articles = []
            for article in all_articles:
                # Check if any of the article's categories match the requested categories
                if any(category.lower() in [c.lower() for c in article.get("categories", [])] for category in categories):
                    filtered_articles.append(article)
                # Also check if any category appears in the title or content
                elif any(category.lower() in article.get("title", "").lower() or 
                         category.lower() in article.get("content", "").lower() 
                         for category in categories):
                    filtered_articles.append(article)
            all_articles = filtered_articles
        
        # Sort by published date (newest first)
        all_articles.sort(key=lambda x: x.get("published", ""), reverse=True)
        
        # Save updated cache
        self._save_cache()
        
        return all_articles[:max_articles]
    
    def search_news(self, query, max_articles=10):
        """
        Search for news articles matching a query.
        
        Args:
            query (str): Search query
            max_articles (int): Maximum number of articles to return
            
        Returns:
            list: List of matching article dictionaries
        """
        # Get all recent news
        all_articles = self.crawl_news(max_articles=50)  # Get a larger pool to search from
        
        # Create search terms
        search_terms = query.lower().split()
        
        # Score and rank articles
        scored_articles = []
        for article in all_articles:
            score = 0
            
            # Check title
            title = article.get("title", "").lower()
            for term in search_terms:
                if term in title:
                    score += 10  # Higher weight for title matches
            
            # Check content
            content = article.get("content", "").lower()
            for term in search_terms:
                score += content.count(term)
            
            # Check summary
            summary = article.get("summary", "").lower()
            for term in search_terms:
                if term in summary:
                    score += 5  # Medium weight for summary matches
            
            if score > 0:
                scored_articles.append((score, article))
        
        # Sort by score (highest first)
        scored_articles.sort(reverse=True)
        
        # Return top articles
        return [article for _, article in scored_articles[:max_articles]]
    
    def get_trending_topics(self, count=5):
        """
        Identify trending topics from recent news.
        
        Args:
            count (int): Number of trending topics to return
            
        Returns:
            list: List of trending topic dictionaries
        """
        # Get recent news
        articles = self.crawl_news(max_articles=50)
        
        # Extract all text
        all_text = ""
        for article in articles:
            all_text += article.get("title", "") + " "
            all_text += article.get("summary", "") + " "
            all_text += article.get("content", "") + " "
        
        # Clean text
        all_text = all_text.lower()
        all_text = re.sub(r'[^\w\s]', '', all_text)
        
        # Remove common stop words
        stop_words = ["the", "and", "a", "to", "of", "in", "is", "it", "that", "for", "on", "with", "as", "was", "by", "at", "from", "be", "this", "have", "an", "are", "not", "or", "but", "what", "all", "were", "when", "we", "there", "been", "has", "would", "will", "more", "about", "which", "their", "they", "also", "had", "can", "his", "her", "she", "he", "they", "them", "said"]
        
        # Count word frequencies
        words = all_text.split()
        word_counts = {}
        
        for word in words:
            if len(word) > 3 and word not in stop_words:  # Ignore short words and stop words
                if word in word_counts:
                    word_counts[word] += 1
                else:
                    word_counts[word] = 1
        
        # Find phrases (bigrams and trigrams)
        phrases = []
        for i in range(len(words) - 1):
            if len(words[i]) > 3 and len(words[i+1]) > 3:
                phrase = f"{words[i]} {words[i+1]}"
                phrases.append(phrase)
        
        for i in range(len(words) - 2):
            if len(words[i]) > 3 and len(words[i+1]) > 3 and len(words[i+2]) > 3:
                phrase = f"{words[i]} {words[i+1]} {words[i+2]}"
                phrases.append(phrase)
        
        phrase_counts = {}
        for phrase in phrases:
            if phrase in phrase_counts:
                phrase_counts[phrase] += 1
            else:
                phrase_counts[phrase] = 1
        
        # Combine word and phrase counts
        all_counts = {}
        all_counts.update(word_counts)
        all_counts.update(phrase_counts)
        
        # Sort by frequency
        sorted_counts = sorted(all_counts.items(), key=lambda x: x[1], reverse=True)
        
        # Create trending topics
        trending = []
        for term, frequency in sorted_counts[:count*2]:  # Get more than needed to filter
            # Skip if term contains a stop word
            if any(stop in term.split() for stop in stop_words):
                continue
                
            # Find related articles
            related_articles = []
            for article in articles:
                title = article.get("title", "").lower()
                content = article.get("content", "").lower()
                
                if term in title or term in content:
                    related_articles.append({
                        "id": article["id"],
                        "title": article["title"],
                        "url": article["url"],
                        "source": article["source"]
                    })
            
            if related_articles:
                trending.append({
                    "topic": term,
                    "frequency": frequency,
                    "related_articles": related_articles[:3]  # Top 3 related articles
                })
            
            if len(trending) >= count:
                break
        
        return trending[:count]


class SNSUploader:
    """
    Class for uploading content to social networking services.
    """
    def __init__(self, config_path=None):
        """
        Initialize the SNSUploader.
        
        Args:
            config_path (str): Path to configuration file
        """
        self.config = self._load_config(config_path)
        self.data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".sns_data")
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Initialize history
        self.history_file = os.path.join(self.data_dir, "posting_history.json")
        self.history = self._load_history()
        
        # Initialize news crawler
        self.news_crawler = NewsCrawler(config_path)
    
    def _load_config(self, config_path):
        """
        Load configuration from file or use defaults.
        
        Args:
            config_path (str): Path to configuration file
            
        Returns:
            dict: Configuration dictionary
        """
        default_config = {
            "platforms": {
                "twitter": {
                    "enabled": True,
                    "api_key": "",
                    "api_secret": "",
                    "access_token": "",
                    "token_secret": "",
                    "max_length": 280,
                    "include_link": True,
                    "include_hashtags": True,
                    "max_hashtags": 3
                },
                "facebook": {
                    "enabled": False,
                    "page_id": "",
                    "access_token": "",
                    "include_image": True,
                    "include_link": True
                },
                "linkedin": {
                    "enabled": False,
                    "access_token": "",
                    "include_image": True,
                    "include_link": True
                },
                "instagram": {
                    "enabled": False,
                    "username": "",
                    "password": "",
                    "require_image": True
                }
            },
            "posting": {
                "max_posts_per_day": 10,
                "min_interval_minutes": 30,
                "best_times": ["8:00", "12:00", "17:00", "20:00"],
                "include_source_attribution": True,
                "add_utm_parameters": True
            },
            "content": {
                "title_formats": [
                    "Breaking: {title}",
                    "Just in: {title}",
                    "{title}",
                    "News: {title}"
                ],
                "hashtag_sources": ["categories", "trending", "custom"],
                "custom_hashtags": ["news", "update", "trending"],
                "max_title_length": 100,
                "include_summary": True,
                "max_summary_length": 100
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
    
    def _load_history(self):
        """
        Load posting history from file.
        
        Returns:
            dict: History dictionary
        """
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading history: {e}")
                
        return {"posts": [], "last_updated": datetime.now().isoformat()}
    
    def _save_history(self):
        """
        Save posting history to file.
        """
        try:
            with open(self.history_file, 'w') as f:
                json.dump(self.history, f, indent=2)
        except Exception as e:
            print(f"Error saving history: {e}")
    
    def _format_post_text(self, article, platform):
        """
        Format article data into post text for a specific platform.
        
        Args:
            article (dict): Article data
            platform (str): Platform name
            
        Returns:
            str: Formatted post text
        """
        platform_config = self.config["platforms"].get(platform, {})
        content_config = self.config["content"]
        
        # Select a random title format
        title_format = random.choice(content_config["title_formats"])
        formatted_title = title_format.format(title=article["title"])
        
        # Truncate title if needed
        if len(formatted_title) > content_config["max_title_length"]:
            formatted_title = formatted_title[:content_config["max_title_length"] - 3] + "..."
        
        # Start building the post
        post_text = formatted_title
        
        # Add summary if configured
        if content_config["include_summary"] and "summary" in article:
            summary = article["summary"]
            if len(summary) > content_config["max_summary_length"]:
                summary = summary[:content_config["max_summary_length"] - 3] + "..."
            post_text += f"\n\n{summary}"
        
        # Add source attribution if configured
        if self.config["posting"]["include_source_attribution"] and "source" in article:
            post_text += f"\n\nSource: {article['source']}"
        
        # Add link if configured
        if platform_config.get("include_link", True) and "url" in article:
            url = article["url"]
            
            # Add UTM parameters if configured
            if self.config["posting"]["add_utm_parameters"]:
                utm_params = f"utm_source={platform}&utm_medium=social&utm_campaign=news_bot"
                if "?" in url:
                    url += f"&{utm_params}"
                else:
                    url += f"?{utm_params}"
                    
            post_text += f"\n\n{url}"
        
        # Add hashtags if configured
        if platform_config.get("include_hashtags", False):
            hashtags = self._generate_hashtags(article)
            if hashtags:
                hashtag_text = " ".join(hashtags[:platform_config.get("max_hashtags", 3)])
                post_text += f"\n\n{hashtag_text}"
        
        # Truncate to platform limits
        max_length = platform_config.get("max_length", 5000)
        if len(post_text) > max_length:
            # Try to preserve the URL by truncating the text before it
            url_index = post_text.find("http")
            if url_index > 0 and url_index < max_length - 30:  # Ensure there's room for the URL
                truncated_text = post_text[:url_index].strip()
                if len(truncated_text) > max_length - 30 - 3:
                    truncated_text = truncated_text[:max_length - 30 - 3] + "..."
                post_text = truncated_text + "\n\n" + post_text[url_index:]
            else:
                post_text = post_text[:max_length - 3] + "..."
        
        return post_text
    
    def _generate_hashtags(self, article):
        """
        Generate hashtags for an article.
        
        Args:
            article (dict): Article data
            
        Returns:
            list: List of hashtags
        """
        hashtags = []
        hashtag_sources = self.config["content"]["hashtag_sources"]
        
        # Add from categories
        if "categories" in hashtag_sources and "categories" in article:
            for category in article["categories"]:
                # Clean and format category
                clean_category = re.sub(r'[^\w]', '', category)
                if clean_category:
                    hashtags.append(f"#{clean_category}")
        
        # Add from trending topics
        if "trending" in hashtag_sources:
            # Extract keywords from title and content
            title_words = article.get("title", "").lower().split()
            content_words = article.get("content", "").lower().split()
            
            # Get trending topics
            trending = self.news_crawler.get_trending_topics(count=5)
            for topic in trending:
                topic_words = topic["topic"].lower().split()
                
                # Check if topic is relevant to the article
                if any(word in title_words for word in topic_words) or any(word in content_words for word in topic_words):
                    # Clean and format topic
                    clean_topic = re.sub(r'[^\w]', '', topic["topic"].replace(" ", ""))
                    if clean_topic:
                        hashtags.append(f"#{clean_topic}")
        
        # Add custom hashtags
        if "custom" in hashtag_sources:
            custom_hashtags = self.config["content"]["custom_hashtags"]
            for tag in custom_hashtags:
                hashtags.append(f"#{tag}")
        
        # Remove duplicates and return
        return list(set(hashtags))
    
    def _can_post_now(self, platform):
        """
        Check if we can post to a platform now based on daily limits and intervals.
        
        Args:
            platform (str): Platform name
            
        Returns:
            bool: True if posting is allowed, False otherwise
        """
        now = datetime.now()
        today = now.strftime("%Y-%m-%d")
        
        # Count posts today for this platform
        posts_today = 0
        for post in self.history["posts"]:
            post_date = datetime.fromisoformat(post["timestamp"]).strftime("%Y-%m-%d")
            if post_date == today and post["platform"] == platform:
                posts_today += 1
        
        # Check daily limit
        if posts_today >= self.config["posting"]["max_posts_per_day"]:
            return False
        
        # Check interval
        if self.history["posts"]:
            last_post = None
            for post in reversed(self.history["posts"]):
                if post["platform"] == platform:
                    last_post = post
                    break
                    
            if last_post:
                last_post_time = datetime.fromisoformat(last_post["timestamp"])
                minutes_since_last = (now - last_post_time).total_seconds() / 60
                
                if minutes_since_last < self.config["posting"]["min_interval_minutes"]:
                    return False
        
        return True
    
    def _is_good_posting_time(self):
        """
        Check if current time is a good time to post based on configuration.
        
        Returns:
            bool: True if it's a good time to post, False otherwise
        """
        now = datetime.now()
        current_time = now.strftime("%H:%M")
        
        # Check if current time is close to any of the best times
        best_times = self.config["posting"]["best_times"]
        for best_time in best_times:
            best_hour, best_minute = map(int, best_time.split(":"))
            current_hour, current_minute = map(int, current_time.split(":"))
            
            # Calculate difference in minutes
            best_total_minutes = best_hour * 60 + best_minute
            current_total_minutes = current_hour * 60 + current_minute
            diff_minutes = abs(best_total_minutes - current_total_minutes)
            
            # If within 30 minutes of a best time, it's a good time to post
            if diff_minutes <= 30:
                return True
        
        # If no best times are configured, always return True
        return not best_times
    
    def _post_to_twitter(self, post_text, image_url=None):
        """
        Post to Twitter.
        
        Args:
            post_text (str): Text to post
            image_url (str): Optional image URL
            
        Returns:
            dict: Result dictionary
        """
        twitter_config = self.config["platforms"]["twitter"]
        
        if not twitter_config.get("api_key") or not twitter_config.get("api_secret") or not twitter_config.get("access_token") or not twitter_config.get("token_secret"):
            return {"success": False, "error": "Twitter API credentials not configured"}
        
        try:
            # This is a placeholder for actual Twitter API implementation
            # In a real implementation, you would use the Twitter API to post
            print(f"[TWITTER] Posting: {post_text[:50]}...")
            if image_url:
                print(f"[TWITTER] With image: {image_url}")
                
            # Simulate successful posting
            return {
                "success": True,
                "post_id": f"twitter_{int(time.time())}",
                "url": f"https://twitter.com/user/status/{int(time.time())}"
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _post_to_facebook(self, post_text, image_url=None):
        """
        Post to Facebook.
        
        Args:
            post_text (str): Text to post
            image_url (str): Optional image URL
            
        Returns:
            dict: Result dictionary
        """
        facebook_config = self.config["platforms"]["facebook"]
        
        if not facebook_config.get("page_id") or not facebook_config.get("access_token"):
            return {"success": False, "error": "Facebook API credentials not configured"}
        
        try:
            # This is a placeholder for actual Facebook API implementation
            # In a real implementation, you would use the Facebook Graph API to post
            print(f"[FACEBOOK] Posting: {post_text[:50]}...")
            if image_url:
                print(f"[FACEBOOK] With image: {image_url}")
                
            # Simulate successful posting
            return {
                "success": True,
                "post_id": f"facebook_{int(time.time())}",
                "url": f"https://facebook.com/post/{int(time.time())}"
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _post_to_linkedin(self, post_text, image_url=None):
        """
        Post to LinkedIn.
        
        Args:
            post_text (str): Text to post
            image_url (str): Optional image URL
            
        Returns:
            dict: Result dictionary
        """
        linkedin_config = self.config["platforms"]["linkedin"]
        
        if not linkedin_config.get("access_token"):
            return {"success": False, "error": "LinkedIn API credentials not configured"}
        
        try:
            # This is a placeholder for actual LinkedIn API implementation
            # In a real implementation, you would use the LinkedIn API to post
            print(f"[LINKEDIN] Posting: {post_text[:50]}...")
            if image_url:
                print(f"[LINKEDIN] With image: {image_url}")
                
            # Simulate successful posting
            return {
                "success": True,
                "post_id": f"linkedin_{int(time.time())}",
                "url": f"https://linkedin.com/post/{int(time.time())}"
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _post_to_instagram(self, post_text, image_url):
        """
        Post to Instagram.
        
        Args:
            post_text (str): Text to post
            image_url (str): Image URL (required for Instagram)
            
        Returns:
            dict: Result dictionary
        """
        instagram_config = self.config["platforms"]["instagram"]
        
        if not instagram_config.get("username") or not instagram_config.get("password"):
            return {"success": False, "error": "Instagram credentials not configured"}
        
        if not image_url:
            return {"success": False, "error": "Image URL is required for Instagram"}
        
        try:
            # This is a placeholder for actual Instagram API implementation
            # In a real implementation, you would use the Instagram API to post
            print(f"[INSTAGRAM] Posting: {post_text[:50]}...")
            print(f"[INSTAGRAM] With image: {image_url}")
                
            # Simulate successful posting
            return {
                "success": True,
                "post_id": f"instagram_{int(time.time())}",
                "url": f"https://instagram.com/p/{int(time.time())}"
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def post_article(self, article, platforms=None):
        """
        Post an article to specified platforms.
        
        Args:
            article (dict): Article data
            platforms (list): List of platforms to post to (defaults to all enabled)
            
        Returns:
            dict: Results dictionary
        """
        if not platforms:
            platforms = [p for p, config in self.config["platforms"].items() if config.get("enabled", False)]
        
        results = {}
        
        for platform in platforms:
            # Check if platform is enabled
            if not self.config["platforms"].get(platform, {}).get("enabled", False):
                results[platform] = {"success": False, "error": f"Platform {platform} is not enabled"}
                continue
                
            # Check if we can post now
            if not self._can_post_now(platform):
                results[platform] = {"success": False, "error": f"Posting limit reached for {platform}"}
                continue
                
            # Check if it's a good time to post
            if not self._is_good_posting_time():
                results[platform] = {"success": False, "error": "Not an optimal posting time"}
                continue
            
            # Format post text for this platform
            post_text = self._format_post_text(article, platform)
            
            # Get image URL if available and platform supports it
            image_url = None
            if self.config["platforms"][platform].get("include_image", False) and "image_url" in article:
                image_url = article["image_url"]
            
            # Post to the platform
            if platform == "twitter":
                result = self._post_to_twitter(post_text, image_url)
            elif platform == "facebook":
                result = self._post_to_facebook(post_text, image_url)
            elif platform == "linkedin":
                result = self._post_to_linkedin(post_text, image_url)
            elif platform == "instagram":
                result = self._post_to_instagram(post_text, image_url)
            else:
                result = {"success": False, "error": f"Unsupported platform: {platform}"}
            
            results[platform] = result
            
            # Record in history if successful
            if result.get("success", False):
                self.history["posts"].append({
                    "article_id": article["id"],
                    "platform": platform,
                    "post_id": result.get("post_id", ""),
                    "url": result.get("url", ""),
                    "timestamp": datetime.now().isoformat()
                })
                self._save_history()
        
        return results
    
    def post_trending_news(self, categories=None, count=1, platforms=None):
        """
        Post trending news articles to social media.
        
        Args:
            categories (list): Optional list of categories to filter by
            count (int): Number of articles to post
            platforms (list): List of platforms to post to
            
        Returns:
            dict: Results dictionary
        """
        # Get trending news
        articles = self.news_crawler.crawl_news(categories=categories, max_articles=count*2)  # Get more than needed in case some fail
        
        results = []
        posted_count = 0
        
        for article in articles:
            # Check if article was already posted
            already_posted = False
            for post in self.history["posts"]:
                if post["article_id"] == article["id"]:
                    already_posted = True
                    break
                    
            if already_posted:
                continue
                
            # Post the article
            post_results = self.post_article(article, platforms)
            
            # Check if posting was successful on any platform
            success = any(result.get("success", False) for result in post_results.values())
            
            results.append({
                "article": {
                    "id": article["id"],
                    "title": article["title"],
                    "url": article["url"],
                    "source": article["source"]
                },
                "results": post_results,
                "success": success
            })
            
            if success:
                posted_count += 1
                
            if posted_count >= count:
                break
        
        return results
    
    def schedule_posts(self, categories=None, posts_per_day=None, platforms=None):
        """
        Schedule posts throughout the day.
        
        Args:
            categories (list): Optional list of categories to filter by
            posts_per_day (int): Number of posts to schedule per day
            platforms (list): List of platforms to post to
            
        Returns:
            dict: Schedule dictionary
        """
        if not posts_per_day:
            posts_per_day = self.config["posting"]["max_posts_per_day"]
            
        # Get best posting times
        best_times = self.config["posting"]["best_times"]
        if not best_times:
            # Default to evenly spaced times during the day
            hours_between = 24 / posts_per_day
            best_times = [f"{int(i * hours_between):02d}:00" for i in range(posts_per_day)]
        
        # Get articles to post
        articles = self.news_crawler.crawl_news(categories=categories, max_articles=posts_per_day*2)
        
        # Filter out already posted articles
        filtered_articles = []
        for article in articles:
            already_posted = False
            for post in self.history["posts"]:
                if post["article_id"] == article["id"]:
                    already_posted = True
                    break
                    
            if not already_posted:
                filtered_articles.append(article)
        
        # Create schedule
        schedule = []
        now = datetime.now()
        today = now.strftime("%Y-%m-%d")
        
        for i in range(min(len(filtered_articles), posts_per_day, len(best_times))):
            time_str = best_times[i % len(best_times)]
            hour, minute = map(int, time_str.split(":"))
            
            scheduled_time = datetime(now.year, now.month, now.day, hour, minute)
            
            # If time is in the past, schedule for tomorrow
            if scheduled_time < now:
                scheduled_time = scheduled_time.replace(day=scheduled_time.day + 1)
            
            schedule.append({
                "article": {
                    "id": filtered_articles[i]["id"],
                    "title": filtered_articles[i]["title"],
                    "url": filtered_articles[i]["url"],
                    "source": filtered_articles[i]["source"]
                },
                "scheduled_time": scheduled_time.isoformat(),
                "platforms": platforms or [p for p, config in self.config["platforms"].items() if config.get("enabled", False)]
            })
        
        return {
            "date": today,
            "posts": schedule
        }
    
    def get_posting_stats(self, days=7):
        """
        Get posting statistics.
        
        Args:
            days (int): Number of days to include in stats
            
        Returns:
            dict: Statistics dictionary
        """
        now = datetime.now()
        cutoff_date = (now - timedelta(days=days)).isoformat()
        
        # Filter recent posts
        recent_posts = [post for post in self.history["posts"] if post["timestamp"] >= cutoff_date]
        
        # Count by platform
        platform_counts = {}
        for post in recent_posts:
            platform = post["platform"]
            if platform in platform_counts:
                platform_counts[platform] += 1
            else:
                platform_counts[platform] = 1
        
        # Count by day
        day_counts = {}
        for post in recent_posts:
            day = datetime.fromisoformat(post["timestamp"]).strftime("%Y-%m-%d")
            if day in day_counts:
                day_counts[day] += 1
            else:
                day_counts[day] = 1
        
        # Get most recent posts
        most_recent = sorted(recent_posts, key=lambda x: x["timestamp"], reverse=True)[:5]
        recent_posts_data = []
        
        for post in most_recent:
            # Find the article data
            article_data = None
            for article_id, article in self.news_crawler.cache["articles"].items():
                if article_id == post["article_id"]:
                    article_data = article
                    break
                    
            if article_data:
                recent_posts_data.append({
                    "platform": post["platform"],
                    "timestamp": post["timestamp"],
                    "url": post["url"],
                    "article": {
                        "title": article_data["title"],
                        "source": article_data["source"],
                        "url": article_data["url"]
                    }
                })
            else:
                recent_posts_data.append({
                    "platform": post["platform"],
                    "timestamp": post["timestamp"],
                    "url": post["url"],
                    "article": {
                        "id": post["article_id"]
                    }
                })
        
        return {
            "total_posts": len(recent_posts),
            "platform_counts": platform_counts,
            "day_counts": day_counts,
            "recent_posts": recent_posts_data
        }


class NewsUploader:
    """
    Main class for crawling news and uploading to social networks.
    """
    def __init__(self, config_path=None):
        """
        Initialize the NewsUploader.
        
        Args:
            config_path (str): Path to configuration file
        """
        self.config_path = config_path
        self.news_crawler = NewsCrawler(config_path)
        self.sns_uploader = SNSUploader(config_path)
    
    def crawl_and_post(self, categories=None, count=1, platforms=None):
        """
        Crawl news and post to social networks.
        
        Args:
            categories (list): Optional list of categories to filter by
            count (int): Number of articles to post
            platforms (list): List of platforms to post to
            
        Returns:
            dict: Results dictionary
        """
        return self.sns_uploader.post_trending_news(categories, count, platforms)
    
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
        return self.sns_uploader.schedule_posts(categories, posts_per_day, platforms)
    
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
    
    def get_posting_stats(self, days=7):
        """
        Get posting statistics.
        
        Args:
            days (int): Number of days to include in stats
            
        Returns:
            dict: Statistics dictionary
        """
        return self.sns_uploader.get_posting_stats(days)
    
    def run_scheduled_posting(self, interval_minutes=30):
        """
        Run scheduled posting in a loop.
        
        Args:
            interval_minutes (int): Interval between checks in minutes
            
        Returns:
            None
        """
        print(f"Starting scheduled posting with {interval_minutes} minute intervals")
        
        try:
            while True:
                # Get current schedule
                schedule = self.sns_uploader.schedule_posts()
                
                # Check if any posts are due
                now = datetime.now()
                for post in schedule["posts"]:
                    scheduled_time = datetime.fromisoformat(post["scheduled_time"])
                    
                    # If post is due (within 5 minutes of scheduled time)
                    time_diff = (scheduled_time - now).total_seconds() / 60
                    if 0 <= time_diff <= 5:
                        print(f"Posting scheduled article: {post['article']['title']}")
                        
                        # Find the full article data
                        article_data = None
                        for article_id, article in self.news_crawler.cache["articles"].items():
                            if article_id == post["article"]["id"]:
                                article_data = article
                                break
                                
                        if article_data:
                            # Post the article
                            results = self.sns_uploader.post_article(article_data, post["platforms"])
                            print(f"Posting results: {results}")
                
                # Sleep for the specified interval
                time.sleep(interval_minutes * 60)
                
        except KeyboardInterrupt:
            print("Scheduled posting stopped by user")
        except Exception as e:
            print(f"Error in scheduled posting: {e}")


# Example usage
if __name__ == "__main__":
    # Create a news uploader
    uploader = NewsUploader()
    
    # Crawl and post news
    results = uploader.crawl_and_post(categories=["technology"], count=1)
    print(f"Posting results: {results}")
    
    # Get trending topics
    trending = uploader.get_trending_topics(count=3)
    print(f"Trending topics: {trending}")
    
    # Schedule daily posts
    schedule = uploader.schedule_daily_posts(posts_per_day=3)
    print(f"Daily schedule: {schedule}")
    
    # Get posting stats
    stats = uploader.get_posting_stats(days=7)
    print(f"Posting stats: {stats}")
