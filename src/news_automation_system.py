import os
import json
import time
import requests
import feedparser
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from src.openai_generator import OpenAIGenerator
from src.constants import ROOT_DIR

class NewsAutomationSystem:
    """
    Automated system for crawling news sources, processing content, and posting to various platforms.
    """
    def __init__(self):
        """
        Initialize the NewsAutomationSystem.
        """
        self.openai_generator = OpenAIGenerator()
        self.output_dir = os.path.join(ROOT_DIR, ".mp", "news_automation")
        self.data_file = os.path.join(self.output_dir, "news_data.json")
        self.sources_file = os.path.join(self.output_dir, "news_sources.json")
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Load existing data if available
        self.news_data = self._load_data()
        self.news_sources = self._load_sources()
        
    def _load_data(self):
        """
        Load news data from file.
        
        Returns:
            dict: News data
        """
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading news data: {e}")
                
        # Default structure if file doesn't exist or can't be loaded
        return {
            "articles": [],
            "processed_content": [],
            "posts": [],
            "stats": {
                "articles_crawled": 0,
                "articles_processed": 0,
                "posts_created": 0,
                "platforms_posted": {}
            },
            "last_updated": datetime.now().isoformat()
        }
    
    def _load_sources(self):
        """
        Load news sources from file.
        
        Returns:
            list: News sources
        """
        if os.path.exists(self.sources_file):
            try:
                with open(self.sources_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading news sources: {e}")
                
        # Default sources if file doesn't exist or can't be loaded
        return [
            {
                "id": "cnn",
                "name": "CNN",
                "url": "http://rss.cnn.com/rss/cnn_topstories.rss",
                "type": "rss",
                "categories": ["general", "news", "politics"]
            },
            {
                "id": "bbc",
                "name": "BBC News",
                "url": "http://feeds.bbci.co.uk/news/rss.xml",
                "type": "rss",
                "categories": ["general", "news", "world"]
            },
            {
                "id": "techcrunch",
                "name": "TechCrunch",
                "url": "https://techcrunch.com/feed/",
                "type": "rss",
                "categories": ["technology", "startups", "business"]
            },
            {
                "id": "espn",
                "name": "ESPN",
                "url": "https://www.espn.com/espn/rss/news",
                "type": "rss",
                "categories": ["sports"]
            }
        ]
    
    def _save_data(self):
        """
        Save news data to file.
        """
        try:
            self.news_data["last_updated"] = datetime.now().isoformat()
            
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.news_data, f, indent=2)
                
        except Exception as e:
            print(f"Error saving news data: {e}")
    
    def _save_sources(self):
        """
        Save news sources to file.
        """
        try:
            with open(self.sources_file, 'w', encoding='utf-8') as f:
                json.dump(self.news_sources, f, indent=2)
                
        except Exception as e:
            print(f"Error saving news sources: {e}")
    
    def add_news_source(self, name, url, source_type="rss", categories=None):
        """
        Add a news source.
        
        Args:
            name (str): Name of the news source
            url (str): URL of the news source (RSS feed or website)
            source_type (str): Type of source (rss, website)
            categories (list): Categories for the source
            
        Returns:
            dict: Added source data
        """
        source_id = name.lower().replace(" ", "_")
        
        # Check if source already exists
        for source in self.news_sources:
            if source["id"] == source_id:
                return source
        
        source = {
            "id": source_id,
            "name": name,
            "url": url,
            "type": source_type,
            "categories": categories or ["general"]
        }
        
        self.news_sources.append(source)
        self._save_sources()
        
        return source
    
    def remove_news_source(self, source_id):
        """
        Remove a news source.
        
        Args:
            source_id (str): ID of the source to remove
            
        Returns:
            bool: True if removed, False if not found
        """
        for i, source in enumerate(self.news_sources):
            if source["id"] == source_id:
                self.news_sources.pop(i)
                self._save_sources()
                return True
                
        return False
    
    def crawl_news(self, source_ids=None, max_articles=10, hours_back=24):
        """
        Crawl news from specified sources.
        
        Args:
            source_ids (list): IDs of sources to crawl (None for all)
            max_articles (int): Maximum number of articles to crawl per source
            hours_back (int): Only crawl articles from the last X hours
            
        Returns:
            list: Crawled articles
        """
        sources_to_crawl = []
        
        if source_ids:
            # Crawl only specified sources
            for source_id in source_ids:
                for source in self.news_sources:
                    if source["id"] == source_id:
                        sources_to_crawl.append(source)
                        break
        else:
            # Crawl all sources
            sources_to_crawl = self.news_sources
        
        crawled_articles = []
        
        for source in sources_to_crawl:
            try:
                if source["type"] == "rss":
                    articles = self._crawl_rss_feed(source, max_articles, hours_back)
                else:
                    articles = self._crawl_website(source, max_articles, hours_back)
                
                crawled_articles.extend(articles)
                
                # Update stats
                self.news_data["stats"]["articles_crawled"] += len(articles)
                
            except Exception as e:
                print(f"Error crawling {source['name']}: {e}")
        
        # Add crawled articles to data
        self.news_data["articles"].extend(crawled_articles)
        
        # Remove duplicates based on URL
        unique_articles = []
        urls = set()
        
        for article in self.news_data["articles"]:
            if article["url"] not in urls:
                unique_articles.append(article)
                urls.add(article["url"])
        
        self.news_data["articles"] = unique_articles
        
        self._save_data()
        
        return crawled_articles
    
    def _crawl_rss_feed(self, source, max_articles, hours_back):
        """
        Crawl articles from an RSS feed.
        
        Args:
            source (dict): Source data
            max_articles (int): Maximum number of articles to crawl
            hours_back (int): Only crawl articles from the last X hours
            
        Returns:
            list: Crawled articles
        """
        articles = []
        
        try:
            feed = feedparser.parse(source["url"])
            
            # Calculate cutoff time
            cutoff_time = datetime.now() - timedelta(hours=hours_back)
            
            for i, entry in enumerate(feed.entries):
                if i >= max_articles:
                    break
                
                # Get publication date
                if hasattr(entry, 'published_parsed'):
                    pub_date = datetime(*entry.published_parsed[:6])
                elif hasattr(entry, 'updated_parsed'):
                    pub_date = datetime(*entry.updated_parsed[:6])
                else:
                    pub_date = datetime.now()  # Default to now if no date available
                
                # Skip if article is older than cutoff time
                if pub_date < cutoff_time:
                    continue
                
                # Extract article data
                article = {
                    "id": f"{source['id']}_{int(time.time())}_{i}",
                    "title": entry.title,
                    "url": entry.link,
                    "source_id": source["id"],
                    "source_name": source["name"],
                    "published_date": pub_date.isoformat(),
                    "categories": source["categories"],
                    "summary": entry.summary if hasattr(entry, 'summary') else "",
                    "content": entry.content[0].value if hasattr(entry, 'content') else entry.summary if hasattr(entry, 'summary') else "",
                    "crawled_date": datetime.now().isoformat()
                }
                
                articles.append(article)
                
        except Exception as e:
            print(f"Error parsing RSS feed {source['url']}: {e}")
        
        return articles
    
    def _crawl_website(self, source, max_articles, hours_back):
        """
        Crawl articles from a website.
        
        Args:
            source (dict): Source data
            max_articles (int): Maximum number of articles to crawl
            hours_back (int): Only crawl articles from the last X hours
            
        Returns:
            list: Crawled articles
        """
        articles = []
        
        try:
            response = requests.get(source["url"], headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            })
            
            if response.status_code != 200:
                print(f"Error fetching {source['url']}: Status code {response.status_code}")
                return articles
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find article links (this is a simple implementation and may need customization for specific sites)
            links = soup.find_all('a', href=True)
            article_links = []
            
            for link in links:
                href = link['href']
                
                # Check if link is likely an article
                if ('article' in href or 'story' in href or 'news' in href) and not href.endswith(('.jpg', '.png', '.pdf')):
                    # Make relative URLs absolute
                    if href.startswith('/'):
                        base_url = '/'.join(source["url"].split('/')[:3])  # http(s)://domain.com
                        href = base_url + href
                    
                    article_links.append(href)
            
            # Remove duplicates and limit to max_articles
            article_links = list(set(article_links))[:max_articles]
            
            # Fetch and parse each article
            for i, link in enumerate(article_links):
                try:
                    article_response = requests.get(link, headers={
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                    })
                    
                    if article_response.status_code != 200:
                        continue
                    
                    article_soup = BeautifulSoup(article_response.text, 'html.parser')
                    
                    # Extract title
                    title = article_soup.find('h1')
                    title_text = title.text.strip() if title else "Untitled Article"
                    
                    # Extract content (this is a simple implementation and may need customization)
                    content_elements = article_soup.find_all(['p', 'h2', 'h3'])
                    content = ' '.join([elem.text.strip() for elem in content_elements])
                    
                    # Extract publication date (this is a simple implementation and may need customization)
                    date_elem = article_soup.find('time') or article_soup.find(class_=['date', 'time', 'published'])
                    pub_date = datetime.now()  # Default to now if no date found
                    
                    if date_elem and date_elem.get('datetime'):
                        try:
                            pub_date = datetime.fromisoformat(date_elem['datetime'].replace('Z', '+00:00'))
                        except:
                            pass
                    
                    # Skip if article is older than cutoff time
                    cutoff_time = datetime.now() - timedelta(hours=hours_back)
                    if pub_date < cutoff_time:
                        continue
                    
                    # Create article object
                    article = {
                        "id": f"{source['id']}_{int(time.time())}_{i}",
                        "title": title_text,
                        "url": link,
                        "source_id": source["id"],
                        "source_name": source["name"],
                        "published_date": pub_date.isoformat(),
                        "categories": source["categories"],
                        "summary": content[:200] + "..." if len(content) > 200 else content,
                        "content": content,
                        "crawled_date": datetime.now().isoformat()
                    }
                    
                    articles.append(article)
                    
                except Exception as e:
                    print(f"Error parsing article {link}: {e}")
                    
        except Exception as e:
            print(f"Error crawling website {source['url']}: {e}")
        
        return articles
    
    def process_articles(self, article_ids=None, platforms=None):
        """
        Process articles to create content for different platforms.
        
        Args:
            article_ids (list): IDs of articles to process (None for all unprocessed)
            platforms (list): Platforms to create content for
            
        Returns:
            list: Processed content
        """
        if not platforms:
            platforms = ["blog", "social", "newsletter"]
        
        articles_to_process = []
        
        if article_ids:
            # Process only specified articles
            for article_id in article_ids:
                for article in self.news_data["articles"]:
                    if article["id"] == article_id:
                        articles_to_process.append(article)
                        break
        else:
            # Find unprocessed articles
            processed_ids = set(item["article_id"] for item in self.news_data["processed_content"])
            articles_to_process = [a for a in self.news_data["articles"] if a["id"] not in processed_ids]
        
        processed_content = []
        
        for article in articles_to_process:
            for platform in platforms:
                try:
                    content = self._process_article_for_platform(article, platform)
                    
                    if content:
                        processed_item = {
                            "id": f"{article['id']}_{platform}_{int(time.time())}",
                            "article_id": article["id"],
                            "platform": platform,
                            "content": content,
                            "processed_date": datetime.now().isoformat(),
                            "posted": False
                        }
                        
                        processed_content.append(processed_item)
                        
                        # Update stats
                        self.news_data["stats"]["articles_processed"] += 1
                        
                except Exception as e:
                    print(f"Error processing article {article['id']} for {platform}: {e}")
        
        # Add processed content to data
        self.news_data["processed_content"].extend(processed_content)
        self._save_data()
        
        return processed_content
    
    def _process_article_for_platform(self, article, platform):
        """
        Process an article for a specific platform.
        
        Args:
            article (dict): Article data
            platform (str): Platform to create content for
            
        Returns:
            dict: Processed content
        """
        system_message = "You are a professional content creator who repurposes news articles for different platforms."
        
        if platform == "blog":
            prompt = f"""
            Transform this news article into a blog post:
            
            Title: {article['title']}
            Source: {article['source_name']}
            Content: {article['content']}
            
            The blog post should:
            - Have an engaging title that's SEO-friendly
            - Include an introduction that hooks the reader
            - Expand on the original content with additional context and insights
            - Be organized with clear headings and subheadings
            - Include a conclusion with key takeaways
            - Be between 800-1200 words
            - Cite the original source
            
            Format the blog post in HTML with proper tags.
            """
            
            content = self.openai_generator.generate_content(prompt, system_message, max_tokens=2000)
            
            return {
                "title": f"Analysis: {article['title']}",
                "format": "html",
                "body": content.strip() if content else f"<h1>{article['title']}</h1><p>{article['content']}</p>",
                "source_attribution": f"Based on reporting from {article['source_name']}"
            }
            
        elif platform == "social":
            prompt = f"""
            Create social media posts for Twitter, Facebook, and LinkedIn based on this news article:
            
            Title: {article['title']}
            Source: {article['source_name']}
            Content: {article['summary']}
            
            For each platform:
            - Twitter: Create a concise post under 280 characters with relevant hashtags
            - Facebook: Create a more detailed post (2-3 paragraphs) with an engaging question
            - LinkedIn: Create a professional post highlighting business implications or industry relevance
            
            Each post should include a brief summary and a hook to read more.
            """
            
            content = self.openai_generator.generate_content(prompt, system_message, max_tokens=1000)
            
            # Parse the content to separate posts for different platforms
            twitter_post = ""
            facebook_post = ""
            linkedin_post = ""
            
            if content:
                content_parts = content.split("\n\n")
                
                for part in content_parts:
                    if part.startswith("Twitter:"):
                        twitter_post = part.replace("Twitter:", "").strip()
                    elif part.startswith("Facebook:"):
                        facebook_post = part.replace("Facebook:", "").strip()
                    elif part.startswith("LinkedIn:"):
                        linkedin_post = part.replace("LinkedIn:", "").strip()
            
            return {
                "twitter": twitter_post or f"Breaking: {article['title']} via {article['source_name']} #news",
                "facebook": facebook_post or f"Just in: {article['title']}\n\n{article['summary']}\n\nSource: {article['source_name']}",
                "linkedin": linkedin_post or f"Industry Update: {article['title']}\n\n{article['summary']}\n\nSource: {article['source_name']}"
            }
            
        elif platform == "newsletter":
            prompt = f"""
            Transform this news article into a newsletter section:
            
            Title: {article['title']}
            Source: {article['source_name']}
            Content: {article['content']}
            
            The newsletter section should:
            - Have a catchy headline
            - Include a brief summary (2-3 sentences)
            - Highlight key points in bullet form
            - Include a "Why it matters" section
            - End with a "Read more" link
            - Be concise and scannable
            
            Format the content in HTML with proper tags.
            """
            
            content = self.openai_generator.generate_content(prompt, system_message, max_tokens=1000)
            
            return {
                "headline": f"News Alert: {article['title']}",
                "format": "html",
                "body": content.strip() if content else f"<h2>{article['title']}</h2><p>{article['summary']}</p><p><a href='{article['url']}'>Read more</a></p>",
                "source_attribution": f"Source: {article['source_name']}"
            }
        
        return None
    
    def post_content(self, content_ids=None, platforms=None):
        """
        Post processed content to platforms.
        
        Args:
            content_ids (list): IDs of content to post (None for all unposted)
            platforms (list): Platforms to post to (None for all)
            
        Returns:
            list: Posted content
        """
        if not platforms:
            platforms = ["blog", "social", "newsletter"]
        
        content_to_post = []
        
        if content_ids:
            # Post only specified content
            for content_id in content_ids:
                for content in self.news_data["processed_content"]:
                    if content["id"] == content_id and not content["posted"]:
                        content_to_post.append(content)
                        break
        else:
            # Find unposted content
            content_to_post = [c for c in self.news_data["processed_content"] if not c["posted"] and c["platform"] in platforms]
        
        posted_content = []
        
        for content in content_to_post:
            try:
                # Simulate posting to platform
                post_result = self._post_to_platform(content)
                
                if post_result:
                    # Mark content as posted
                    for i, c in enumerate(self.news_data["processed_content"]):
                        if c["id"] == content["id"]:
                            self.news_data["processed_content"][i]["posted"] = True
                            self.news_data["processed_content"][i]["post_date"] = datetime.now().isoformat()
                            self.news_data["processed_content"][i]["post_result"] = post_result
                            break
                    
                    # Add to posts list
                    post = {
                        "id": f"post_{int(time.time())}_{len(self.news_data['posts'])}",
                        "content_id": content["id"],
                        "platform": content["platform"],
                        "post_date": datetime.now().isoformat(),
                        "post_result": post_result
                    }
                    
                    self.news_data["posts"].append(post)
                    posted_content.append(post)
                    
                    # Update stats
                    self.news_data["stats"]["posts_created"] += 1
                    
                    platform = content["platform"]
                    if platform in self.news_data["stats"]["platforms_posted"]:
                        self.news_data["stats"]["platforms_posted"][platform] += 1
                    else:
                        self.news_data["stats"]["platforms_posted"][platform] = 1
                    
            except Exception as e:
                print(f"Error posting content {content['id']}: {e}")
        
        self._save_data()
        
        return posted_content
    
    def _post_to_platform(self, content):
        """
        Post content to a platform.
        
        Args:
            content (dict): Content to post
            
        Returns:
            dict: Post result
        """
        # This is a simulation of posting to platforms
        # In a real implementation, this would use APIs to post to actual platforms
        
        platform = content["platform"]
        
        if platform == "blog":
            # Simulate posting to a blog
            return {
                "success": True,
                "url": f"https://example.com/blog/{content['id']}",
                "platform": "blog",
                "post_id": f"blog_{int(time.time())}"
            }
            
        elif platform == "social":
            # Simulate posting to social media
            results = {}
            
            if "twitter" in content["content"]:
                results["twitter"] = {
                    "success": True,
                    "url": f"https://twitter.com/user/status/{int(time.time())}",
                    "platform": "twitter",
                    "post_id": f"tweet_{int(time.time())}"
                }
            
            if "facebook" in content["content"]:
                results["facebook"] = {
                    "success": True,
                    "url": f"https://facebook.com/post/{int(time.time())}",
                    "platform": "facebook",
                    "post_id": f"fb_{int(time.time())}"
                }
            
            if "linkedin" in content["content"]:
                results["linkedin"] = {
                    "success": True,
                    "url": f"https://linkedin.com/post/{int(time.time())}",
                    "platform": "linkedin",
                    "post_id": f"li_{int(time.time())}"
                }
            
            return results
            
        elif platform == "newsletter":
            # Simulate sending a newsletter
            return {
                "success": True,
                "recipients": 1000,
                "open_rate": 0.25,
                "click_rate": 0.05,
                "platform": "newsletter",
                "post_id": f"newsletter_{int(time.time())}"
            }
        
        return None
    
    def run_automation_cycle(self, source_ids=None, max_articles=10, hours_back=24, platforms=None):
        """
        Run a complete automation cycle: crawl, process, post.
        
        Args:
            source_ids (list): IDs of sources to crawl (None for all)
            max_articles (int): Maximum number of articles to crawl per source
            hours_back (int): Only crawl articles from the last X hours
            platforms (list): Platforms to create content for and post to
            
        Returns:
            dict: Results of the automation cycle
        """
        # Crawl news
        crawled_articles = self.crawl_news(source_ids, max_articles, hours_back)
        
        # Process articles
        processed_content = self.process_articles(None, platforms)
        
        # Post content
        posted_content = self.post_content(None, platforms)
        
        return {
            "crawled_articles": len(crawled_articles),
            "processed_content": len(processed_content),
            "posted_content": len(posted_content),
            "timestamp": datetime.now().isoformat()
        }
    
    def schedule_automation(self, interval_hours=6):
        """
        Schedule automation to run at regular intervals.
        
        Args:
            interval_hours (int): Interval between runs in hours
            
        Returns:
            dict: Scheduling information
        """
        # This is a placeholder for scheduling functionality
        # In a real implementation, this would use a task scheduler or cron job
        
        next_run = datetime.now() + timedelta(hours=interval_hours)
        
        return {
            "scheduled": True,
            "interval_hours": interval_hours,
            "next_run": next_run.isoformat()
        }
    
    def get_stats(self):
        """
        Get statistics about the automation system.
        
        Returns:
            dict: Statistics
        """
        return self.news_data["stats"]
    
    def get_recent_posts(self, limit=10):
        """
        Get recent posts.
        
        Args:
            limit (int): Maximum number of posts to return
            
        Returns:
            list: Recent posts
        """
        # Sort posts by post date (newest first)
        sorted_posts = sorted(
            self.news_data["posts"],
            key=lambda p: p["post_date"],
            reverse=True
        )
        
        return sorted_posts[:limit]
