import os
import json
import logging
from datetime import datetime

from src.classes.ShortsGenerator import ShortsGenerator
from src.news_crawler import NewsCrawler
from src.news_extractor import NewsExtractor
from src.news_shorts_template import NewsShortsTemplate

class NewsShortsGenerator(ShortsGenerator):
    """
    Class for generating shorts based on news articles.
    Extends the base ShortsGenerator class to create engaging short-form videos
    from current news content.
    """
    
    def __init__(self, topic=None, article=None, category=None, template_type=None, config_path=None):
        """
        Initialize the News Shorts Generator.
        
        Args:
            topic (str, optional): Topic to search for news about
            article (dict, optional): Specific article to use for shorts generation
            category (str, optional): News category to focus on
            template_type (str, optional): Template type to use for generation
            config_path (str, optional): Path to configuration file
        """
        # Initialize with knowledge_short=True as news shorts are informational
        super().__init__(topic=topic or "Latest News", is_knowledge_short=True)
        
        # Store additional parameters
        self.article = article
        self.category = category
        self.config_path = config_path
        
        # Initialize news crawler, extractor, and template manager
        self.news_crawler = NewsCrawler(config_path)
        self.news_extractor = NewsExtractor(config_path)
        self.template_manager = NewsShortsTemplate(config_path)
        
        # Set template type
        self.template_type = template_type
        if not self.template_type and self.category:
            self.template_type = self.template_manager.get_template_by_category(self.category)
        elif not self.template_type:
            self.template_type = self.template_manager.config["templates"]["default_template"]
        
        # Set up logging
        self.logger = self._setup_logging()
        
        # Override channel name for news shorts
        self.channel_name = "News Shorts"
        
        # News-specific attributes
        self.news_source = None
        self.news_url = None
        self.news_published_date = None
        self.full_article_content = None
        
    def _setup_logging(self):
        """
        Set up logging for the NewsShortsGenerator.
        
        Returns:
            logging.Logger: Configured logger
        """
        logger = logging.getLogger("NewsShortsGenerator")
        logger.setLevel(logging.INFO)
        
        # Create handlers if they don't exist
        if not logger.handlers:
            # Create file handler
            log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "logs")
            os.makedirs(log_dir, exist_ok=True)
            
            log_file = os.path.join(log_dir, "news_shorts_generator.log")
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
    
    def fetch_news_article(self):
        """
        Fetch a news article based on topic or category.
        
        Returns:
            dict: News article dictionary
        """
        try:
            # If article is already provided, use it
            if self.article:
                self.logger.info(f"Using provided article: {self.article.get('title', 'Unknown')}")
                return self.article
            
            # If topic is provided, search for it
            if self.topic and self.topic != "Latest News":
                self.logger.info(f"Searching for news about: {self.topic}")
                articles = self.news_crawler.search_news(self.topic, max_articles=5)
                
                if articles:
                    # Use the most relevant article
                    article = articles[0]
                    self.logger.info(f"Found article: {article.get('title', 'Unknown')}")
                    return article
            
            # If category is provided, filter by it
            if self.category:
                self.logger.info(f"Fetching news in category: {self.category}")
                articles = self.news_crawler.crawl_news(categories=[self.category], max_articles=5)
                
                if articles:
                    # Use the most recent article
                    article = articles[0]
                    self.logger.info(f"Found article: {article.get('title', 'Unknown')}")
                    return article
            
            # Default: get latest news
            self.logger.info("Fetching latest news")
            articles = self.news_crawler.crawl_news(max_articles=5)
            
            if articles:
                # Use the most recent article
                article = articles[0]
                self.logger.info(f"Found article: {article.get('title', 'Unknown')}")
                return article
            
            self.logger.warning("No news articles found")
            return None
            
        except Exception as e:
            self.logger.error(f"Error fetching news article: {e}")
            return None
    
    def extract_article_content(self, article):
        """
        Extract full content from a news article.
        
        Args:
            article (dict): News article dictionary
            
        Returns:
            dict: Extracted article content
        """
        try:
            if not article:
                self.logger.warning("No article provided for extraction")
                return None
            
            # Extract full content using NewsExtractor
            url = article.get("url")
            if not url:
                self.logger.warning("Article has no URL")
                return None
                
            self.logger.info(f"Extracting content from: {url}")
            extracted_content = self.news_extractor.extract_article(url)
            
            if not extracted_content:
                self.logger.warning(f"Failed to extract content from {url}")
                return None
                
            self.logger.info(f"Successfully extracted content: {len(extracted_content.get('content', ''))} characters")
            return extracted_content
            
        except Exception as e:
            self.logger.error(f"Error extracting article content: {e}")
            return None
    
    def generate_script(self):
        """
        Generate a script for a news-based Short.
        
        Returns:
            str: Generated script
        """
        # Fetch news article if not already provided
        if not self.article:
            self.article = self.fetch_news_article()
            
            if not self.article:
                self.logger.error("Failed to fetch news article")
                # Fall back to default script generation
                return super().generate_script()
        
        # Extract full content if needed
        if not self.full_article_content:
            self.full_article_content = self.extract_article_content(self.article)
        
        # Store news metadata
        self.news_source = self.article.get("source", "Unknown Source")
        self.news_url = self.article.get("url", "")
        self.news_published_date = self.article.get("published", "")
        
        # Update topic with article title
        self.topic = self.article.get("title", self.topic)
        
        # Get template-specific system message
        system_message = self.template_manager.get_template_system_message(self.template_type)
        
        # Create article data for template
        article_data = {
            "title": self.topic,
            "source": self.news_source,
            "description": self.article.get("description", ""),
            "content": self.full_article_content.get("content", "") if self.full_article_content else "",
            "published": self.news_published_date
        }
        
        # Get template-specific prompt
        prompt = self.template_manager.get_template_prompt(self.template_type, article_data)
        
        # Generate script
        script = self.openai_generator.generate_content(prompt, system_message, max_tokens=500)
        
        # Log and store the script
        self.logger.info(f"Generated news script with {len(script.split('\\n'))} sentences")
        self.script = script.strip()
        
        return self.script
    
    def generate_metadata(self):
        """
        Generate metadata (title, description) for a news-based Short.
        
        Returns:
            dict: Dictionary containing title and description
        """
        system_message = "You are a YouTube SEO expert who creates optimized metadata for news-based short-form videos."
        
        output_structure = {
            "title": "Attention-grabbing title (max 60 chars)",
            "description": "Compelling description with hashtags (max 200 chars)"
        }
        
        # Get template-specific metadata guidance
        metadata_guidance = self.template_manager.get_metadata_guidance(self.template_type)
        
        # Include news source and date in prompt
        source_info = f"Source: {self.news_source}" if self.news_source else ""
        date_info = ""
        if self.news_published_date:
            try:
                date = datetime.fromisoformat(self.news_published_date)
                date_info = f"Published: {date.strftime('%B %d, %Y')}"
            except:
                pass
        
        prompt = f"""
        Based on the following news article and script for a YouTube Short, generate:
        1. An attention-grabbing title (max 60 characters)
        2. A compelling description with relevant hashtags (max 200 characters)
        
        News Article: {self.topic}
        {source_info}
        {date_info}
        
        Script:
        {self.script}
        
        {metadata_guidance}
        """
        
        metadata = self.openai_generator.generate_structured_content(
            prompt, 
            system_message, 
            max_tokens=300,
            output_structure=output_structure
        )
        
        if not metadata:
            # Fallback if structured content generation fails
            metadata = {
                "title": self.topic[:60],
                "description": f"Breaking news: {self.topic[:100]} | {self.news_source} #news #trending #shorts"
            }
            
        self.logger.info(f"Generated metadata: {metadata}")
        self.title = metadata["title"]
        self.description = metadata["description"]
        
        return metadata
    
    def generate_image_prompts(self):
        """
        Generate image prompts for the news-based script.
        
        Returns:
            list: List of image prompts
        """
        system_message = "You are a creative prompt engineer for news content visualization."
        
        # Get template-specific image prompt guidance
        image_guidance = self.template_manager.get_image_prompt_guidance(self.template_type)
        
        # Get visual style for the template
        visual_style = self.template_manager.get_visual_style(self.template_type)
        
        # Include news information in the prompt
        news_info = f"News headline: {self.topic}\n"
        if self.news_source:
            news_info += f"Source: {self.news_source}\n"
        
        prompt = f"""
        Create {self.script_sentence_length} detailed image prompts for DALL-E based on this news story:
        
        {news_info}
        
        Script:
        {self.script}
        
        Visual style: {visual_style}
        
        {image_guidance}
        
        Format your response as a JSON array of strings, with each string being a complete image prompt.
        """
        
        try:
            response = self.openai_generator.generate_structured_content(prompt, system_message)
            
            if isinstance(response, list):
                image_prompts = response
            elif isinstance(response, dict) and "prompts" in response:
                image_prompts = response["prompts"]
            else:
                # Try to extract a list from the response
                import re
                prompts_text = str(response)
                prompts_match = re.findall(r'"([^"]*)"', prompts_text)
                if prompts_match:
                    image_prompts = prompts_match
                else:
                    raise ValueError("Could not extract prompts from response")
                    
            # Limit to the number of sentences in the script
            script_sentences = self.script.split('\n')
            n_prompts = min(len(image_prompts), len(script_sentences))
            image_prompts = image_prompts[:n_prompts]
            
            self.logger.info(f"Generated {len(image_prompts)} news image prompts")
            self.image_prompts = image_prompts
            return image_prompts
            
        except Exception as e:
            self.logger.error(f"Failed to generate news image prompts: {e}")
            
            # Fallback to simpler approach
            image_prompts = []
            script_sentences = self.script.split('\n')
            for i, sentence in enumerate(script_sentences):
                if not sentence.strip():
                    continue
                prompt = f"A high-quality news photograph related to '{self.topic}', scene: {sentence}, {visual_style}, photojournalistic style, realistic"
                image_prompts.append(prompt)
                
            self.image_prompts = image_prompts
            return image_prompts
    
    def create_news_short(self):
        """
        Creates a news-based Short from start to finish.
        
        Returns:
            dict: Dictionary containing video path and metadata
        """
        try:
            # Fetch news article
            if not self.article:
                self.article = self.fetch_news_article()
                
                if not self.article:
                    self.logger.error("Failed to fetch news article")
                    return None
            
            # Extract full content
            if not self.full_article_content:
                self.full_article_content = self.extract_article_content(self.article)
            
            # Generate script
            if not self.script:
                self.generate_script()
                
            # Generate metadata
            self.generate_metadata()
            
            # Generate image prompts
            self.generate_image_prompts()
            
            # Generate images
            self.generate_images()
            
            # Generate speech
            from src.classes.Tts import TTS
            tts_instance = TTS()
            audio_path = self.generate_script_to_speech(tts_instance)
            
            if not audio_path:
                self.logger.error("Failed to generate audio")
                return None
                
            # Create video with subtitles
            video_path = self.create_video_with_subtitles(audio_path)
            
            if not video_path:
                self.logger.error("Failed to create video")
                return None
            
            # Return result with metadata
            result = {
                "video_path": video_path,
                "title": self.title,
                "description": self.description,
                "news_source": self.news_source,
                "news_url": self.news_url,
                "news_published_date": self.news_published_date,
                "topic": self.topic,
                "category": self.category or self.article.get("categories", ["news"])[0],
                "template_type": self.template_type
            }
            
            self.logger.info(f"Successfully created news short: {result['title']}")
            return result
                
        except Exception as e:
            self.logger.error(f"Error creating news short: {e}")
            return None


# Example usage
if __name__ == "__main__":
    # Create a news shorts generator
    generator = NewsShortsGenerator(category="technology", template_type="tech_news")
    
    # Create a news short
    result = generator.create_news_short()
    
    if result:
        print(f"Created news short: {result['title']}")
        print(f"Video path: {result['video_path']}")
        print(f"Source: {result['news_source']}")
        print(f"Template: {result['template_type']}")
    else:
        print("Failed to create news short")
