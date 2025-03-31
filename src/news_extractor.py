import os
import json
import time
import requests
import logging
import re
from datetime import datetime
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin

class NewsExtractor:
    """
    Class for extracting content from news articles.
    """
    def __init__(self, config_path=None):
        """
        Initialize the NewsExtractor.
        
        Args:
            config_path (str): Path to configuration file
        """
        self.config = self._load_config(config_path)
        self.cache_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".cache")
        os.makedirs(self.cache_dir, exist_ok=True)
        
        # Set up logging
        self.logger = self._setup_logging()
        
        # Initialize cache
        self.extraction_cache_file = os.path.join(self.cache_dir, "extraction_cache.json")
        self.extraction_cache = self._load_cache()
    
    def _setup_logging(self):
        """
        Set up logging for the NewsExtractor.
        
        Returns:
            logging.Logger: Configured logger
        """
        logger = logging.getLogger("NewsExtractor")
        logger.setLevel(logging.INFO)
        
        # Create handlers if they don't exist
        if not logger.handlers:
            # Create file handler
            log_file = os.path.join(self.cache_dir, "news_extractor.log")
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
            "extractor": {
                "request_timeout": 10,
                "request_delay": 1,
                "user_agents": [
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
                    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36"
                ],
                "cache_expiry_hours": 24,
                "min_article_length": 200,
                "max_article_length": 10000,
                "extract_images": True,
                "summarize_content": True,
                "content_tags": ["article", "main", "div.content", "div.article-content", "div.story-content"],
                "exclude_tags": ["nav", "header", "footer", "aside", "div.comments", "div.related", "div.advertisement"]
            }
        }
        
        if config_path and os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    user_config = json.load(f)
                    # Merge user config with defaults
                    if "extractor" in user_config:
                        for key, value in user_config["extractor"].items():
                            default_config["extractor"][key] = value
            except Exception as e:
                self.logger.error(f"Error loading config file: {e}")
                
        return default_config
    
    def _load_cache(self):
        """
        Load extraction cache from file.
        
        Returns:
            dict: Cache dictionary
        """
        if os.path.exists(self.extraction_cache_file):
            try:
                with open(self.extraction_cache_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                self.logger.error(f"Error loading extraction cache: {e}")
                
        return {"articles": {}, "last_updated": datetime.now().isoformat()}
    
    def _save_cache(self):
        """
        Save extraction cache to file.
        """
        try:
            with open(self.extraction_cache_file, 'w') as f:
                json.dump(self.extraction_cache, f, indent=2)
        except Exception as e:
            self.logger.error(f"Error saving extraction cache: {e}")
    
    def _get_random_user_agent(self):
        """
        Get a random user agent from the configured list.
        
        Returns:
            str: User agent string
        """
        user_agents = self.config["extractor"]["user_agents"]
        return user_agents[hash(datetime.now().isoformat()) % len(user_agents)]
    
    def extract_article(self, url):
        """
        Extract content from a news article.
        
        Args:
            url (str): URL of the article
            
        Returns:
            dict: Extracted article content
        """
        # Check cache first
        url_hash = url.replace("/", "_").replace(":", "_")
        if url_hash in self.extraction_cache["articles"]:
            self.logger.info(f"Using cached extraction for {url}")
            return self.extraction_cache["articles"][url_hash]
        
        self.logger.info(f"Extracting content from {url}")
        
        try:
            # Fetch the article
            headers = {
                "User-Agent": self._get_random_user_agent(),
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
                "Referer": "https://www.google.com/",
                "DNT": "1",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1"
            }
            
            response = requests.get(url, headers=headers, timeout=self.config["extractor"]["request_timeout"])
            response.raise_for_status()
            
            # Parse HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract title
            title = soup.title.text.strip() if soup.title else ""
            
            # Extract metadata
            meta_description = ""
            meta_keywords = []
            meta_author = ""
            meta_date = ""
            
            # Description
            meta_desc_tag = soup.find("meta", attrs={"name": "description"}) or soup.find("meta", attrs={"property": "og:description"})
            if meta_desc_tag and "content" in meta_desc_tag.attrs:
                meta_description = meta_desc_tag["content"]
            
            # Keywords
            meta_keywords_tag = soup.find("meta", attrs={"name": "keywords"})
            if meta_keywords_tag and "content" in meta_keywords_tag.attrs:
                meta_keywords = [k.strip() for k in meta_keywords_tag["content"].split(",")]
            
            # Author
            meta_author_tag = soup.find("meta", attrs={"name": "author"}) or soup.find("meta", attrs={"property": "article:author"})
            if meta_author_tag and "content" in meta_author_tag.attrs:
                meta_author = meta_author_tag["content"]
            
            # Publication date
            meta_date_tag = soup.find("meta", attrs={"name": "date"}) or soup.find("meta", attrs={"property": "article:published_time"})
            if meta_date_tag and "content" in meta_date_tag.attrs:
                meta_date = meta_date_tag["content"]
            
            # Extract main content
            content = ""
            
            # Try different content selectors
            for selector in self.config["extractor"]["content_tags"]:
                if "." in selector:
                    tag, class_name = selector.split(".")
                    elements = soup.find_all(tag, class_=class_name)
                else:
                    elements = soup.find_all(selector)
                
                if elements:
                    for element in elements:
                        # Skip excluded elements
                        should_skip = False
                        for exclude in self.config["extractor"]["exclude_tags"]:
                            if "." in exclude:
                                ex_tag, ex_class = exclude.split(".")
                                if element.find(ex_tag, class_=ex_class):
                                    should_skip = True
                                    break
                            elif element.find(exclude):
                                should_skip = True
                                break
                        
                        if should_skip:
                            continue
                        
                        # Extract text
                        paragraphs = element.find_all("p")
                        if paragraphs:
                            for p in paragraphs:
                                if p.text.strip():
                                    content += p.text.strip() + "\n\n"
                    
                    # If we found content, break
                    if content:
                        break
            
            # If no content found with selectors, try a more general approach
            if not content:
                # Remove unwanted elements
                for tag in self.config["extractor"]["exclude_tags"]:
                    if "." in tag:
                        tag_name, class_name = tag.split(".")
                        for element in soup.find_all(tag_name, class_=class_name):
                            element.decompose()
                    else:
                        for element in soup.find_all(tag):
                            element.decompose()
                
                # Extract paragraphs
                paragraphs = soup.find_all("p")
                for p in paragraphs:
                    if p.text.strip():
                        content += p.text.strip() + "\n\n"
            
            # Extract images if configured
            images = []
            if self.config["extractor"]["extract_images"]:
                # Find all images with src attribute
                img_tags = soup.find_all("img", src=True)
                for img in img_tags:
                    # Skip small icons and tracking pixels
                    if "width" in img.attrs and "height" in img.attrs:
                        try:
                            width = int(img["width"])
                            height = int(img["height"])
                            if width < 100 or height < 100:
                                continue
                        except (ValueError, TypeError):
                            pass
                    
                    # Get absolute URL
                    img_url = img["src"]
                    if not img_url.startswith(("http://", "https://")):
                        img_url = urljoin(url, img_url)
                    
                    # Add to images list
                    images.append({
                        "url": img_url,
                        "alt": img.get("alt", ""),
                        "width": img.get("width", ""),
                        "height": img.get("height", "")
                    })
            
            # Clean up content
            content = re.sub(r'\n{3,}', '\n\n', content)  # Remove excessive newlines
            
            # Check if content meets minimum length
            min_length = self.config["extractor"]["min_article_length"]
            if len(content) < min_length:
                self.logger.warning(f"Extracted content too short: {len(content)} chars (min: {min_length})")
            
            # Truncate if exceeds maximum length
            max_length = self.config["extractor"]["max_article_length"]
            if len(content) > max_length:
                content = content[:max_length] + "..."
                self.logger.info(f"Truncated content to {max_length} chars")
            
            # Create result
            result = {
                "url": url,
                "title": title,
                "meta_description": meta_description,
                "meta_keywords": meta_keywords,
                "meta_author": meta_author,
                "meta_date": meta_date,
                "content": content,
                "images": images,
                "extracted_at": datetime.now().isoformat()
            }
            
            # Cache the result
            self.extraction_cache["articles"][url_hash] = result
            self._save_cache()
            
            self.logger.info(f"Successfully extracted content from {url}: {len(content)} chars")
            return result
            
        except Exception as e:
            self.logger.error(f"Error extracting content from {url}: {e}")
            return None
    
    def summarize_article(self, article_content, max_length=500):
        """
        Summarize article content.
        
        Args:
            article_content (dict): Extracted article content
            max_length (int): Maximum length of summary
            
        Returns:
            str: Summarized content
        """
        if not article_content or not article_content.get("content"):
            self.logger.warning("No content to summarize")
            return ""
        
        content = article_content["content"]
        
        # If content is already short, return it
        if len(content) <= max_length:
            return content
        
        # Simple extractive summarization
        # Split into sentences
        sentences = re.split(r'(?<=[.!?])\s+', content)
        
        # Score sentences (simple approach: position and length)
        scored_sentences = []
        for i, sentence in enumerate(sentences):
            # Skip very short sentences
            if len(sentence) < 10:
                continue
                
            # Position score (first sentences are more important)
            position_score = 1.0 if i < 3 else 0.5 if i < 10 else 0.1
            
            # Length score (prefer medium-length sentences)
            length = len(sentence)
            length_score = 0.5 if 20 <= length <= 200 else 0.1
            
            # Keyword score (presence of important words)
            keyword_score = 0
            important_words = article_content.get("meta_keywords", [])
            if important_words:
                for word in important_words:
                    if word.lower() in sentence.lower():
                        keyword_score += 0.2
            
            # Title word score
            title_score = 0
            if article_content.get("title"):
                title_words = [w.lower() for w in re.findall(r'\b\w+\b', article_content["title"])]
                for word in title_words:
                    if len(word) > 3 and word.lower() in sentence.lower():
                        title_score += 0.2
            
            # Total score
            total_score = position_score + length_score + keyword_score + title_score
            
            scored_sentences.append((sentence, total_score))
        
        # Sort by score
        scored_sentences.sort(key=lambda x: x[1], reverse=True)
        
        # Select top sentences until we reach max_length
        summary = ""
        for sentence, _ in scored_sentences:
            if len(summary) + len(sentence) + 1 <= max_length:
                summary += sentence + " "
            else:
                break
        
        self.logger.info(f"Summarized content from {len(content)} to {len(summary)} chars")
        return summary.strip()
    
    def extract_and_summarize(self, url):
        """
        Extract and summarize an article.
        
        Args:
            url (str): URL of the article
            
        Returns:
            dict: Extracted and summarized article
        """
        # Extract article
        article = self.extract_article(url)
        
        if not article:
            return None
        
        # Summarize if configured
        if self.config["extractor"]["summarize_content"]:
            summary = self.summarize_article(article)
            article["summary"] = summary
        
        return article


# Example usage
if __name__ == "__main__":
    # Create a news extractor
    extractor = NewsExtractor()
    
    # Extract article
    article = extractor.extract_article("https://www.bbc.com/news/technology-56901363")
    
    if article:
        print(f"Title: {article['title']}")
        print(f"Description: {article['meta_description']}")
        print(f"Author: {article['meta_author']}")
        print(f"Date: {article['meta_date']}")
        print(f"Content length: {len(article['content'])} chars")
        print(f"Number of images: {len(article['images'])}")
        print("\nFirst 300 chars of content:")
        print(article['content'][:300] + "...")
        
        # Summarize
        summary = extractor.summarize_article(article, 300)
        print("\nSummary:")
        print(summary)
    else:
        print("Failed to extract article")
