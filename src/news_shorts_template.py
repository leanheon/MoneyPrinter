import os
import json
import logging
from datetime import datetime

class NewsShortsTemplate:
    """
    Class for managing templates for news-based shorts generation.
    Provides various templates for different types of news content and presentation styles.
    """
    
    def __init__(self, config_path=None):
        """
        Initialize the NewsShortsTemplate.
        
        Args:
            config_path (str, optional): Path to configuration file
        """
        self.config = self._load_config(config_path)
        self.logger = self._setup_logging()
        
    def _setup_logging(self):
        """
        Set up logging for the NewsShortsTemplate.
        
        Returns:
            logging.Logger: Configured logger
        """
        logger = logging.getLogger("NewsShortsTemplate")
        logger.setLevel(logging.INFO)
        
        # Create handlers if they don't exist
        if not logger.handlers:
            # Create file handler
            log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "logs")
            os.makedirs(log_dir, exist_ok=True)
            
            log_file = os.path.join(log_dir, "news_shorts_template.log")
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
            "templates": {
                "default_template": "breaking_news",
                "sentence_count": {
                    "min": 8,
                    "max": 12
                },
                "include_source_attribution": True,
                "include_call_to_action": True,
                "visual_styles": {
                    "breaking_news": "Urgent, high-contrast news photography style with dramatic lighting",
                    "explainer": "Clear, informative visual style with diagrams and illustrations",
                    "feature_story": "Cinematic, documentary-style visuals with rich colors",
                    "tech_news": "Modern, clean visuals with technology themes and blue tones",
                    "business_news": "Professional, corporate style with charts and business imagery",
                    "entertainment": "Vibrant, colorful celebrity and entertainment imagery",
                    "sports": "Dynamic, action-oriented sports photography with motion blur"
                }
            }
        }
        
        if config_path and os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    user_config = json.load(f)
                    # Merge user config with defaults
                    if "templates" in user_config:
                        for key, value in user_config["templates"].items():
                            default_config["templates"][key] = value
            except Exception as e:
                self.logger.error(f"Error loading config file: {e}")
                
        return default_config
    
    def get_template_system_message(self, template_type=None):
        """
        Get system message for a specific template type.
        
        Args:
            template_type (str, optional): Template type to use
            
        Returns:
            str: System message for the template
        """
        if not template_type:
            template_type = self.config["templates"]["default_template"]
            
        # Base system message for all news shorts
        base_message = (
            "You are a professional script writer for news-based YouTube Shorts. "
            "Create engaging, informative scripts that present news stories in a concise format. "
            "Use simple language, short sentences, and a journalistic tone. "
            "Each sentence should be on a new line. "
            f"The total script should be between {self.config['templates']['sentence_count']['min']} and {self.config['templates']['sentence_count']['max']} sentences. "
        )
        
        # Add source attribution if configured
        if self.config["templates"]["include_source_attribution"]:
            base_message += "Include the source of the news in the script. "
            
        # Add call to action if configured
        if self.config["templates"]["include_call_to_action"]:
            base_message += "End with a call to action for viewers to engage with the content. "
        
        # Template-specific additions
        if template_type == "breaking_news":
            template_message = (
                "Focus on urgency and importance. "
                "Start with an attention-grabbing headline that conveys the breaking nature of the news. "
                "Present the most critical information first, followed by context and details. "
                "Use a tone that conveys the significance of the news without being alarmist. "
                "Emphasize recency with phrases like 'just in' or 'breaking news'."
            )
        elif template_type == "explainer":
            template_message = (
                "Focus on clarity and education. "
                "Start by identifying a complex topic that needs explanation. "
                "Break down the topic into simple, digestible points. "
                "Use analogies or comparisons to make abstract concepts concrete. "
                "Anticipate and address common questions or misconceptions. "
                "Conclude with the significance or implications of the topic."
            )
        elif template_type == "feature_story":
            template_message = (
                "Focus on human interest and narrative. "
                "Start with an intriguing hook that draws viewers into the story. "
                "Introduce the main character or situation early. "
                "Include descriptive details that create a sense of place or emotion. "
                "Build toward a meaningful conclusion or insight. "
                "Use a more conversational, less formal tone than hard news."
            )
        elif template_type == "tech_news":
            template_message = (
                "Focus on innovation and impact. "
                "Start with what's new or changing in technology. "
                "Explain technical concepts in accessible language. "
                "Highlight the real-world implications or applications. "
                "Include relevant statistics or specifications when helpful. "
                "Address how the technology might affect viewers' lives."
            )
        elif template_type == "business_news":
            template_message = (
                "Focus on markets, companies, and economic trends. "
                "Start with the most significant business development or market movement. "
                "Include relevant numbers (stock prices, percentages, dollar amounts) but keep them simple. "
                "Explain how business news might impact consumers or the broader economy. "
                "Use business terminology but define any complex terms. "
                "Maintain an objective tone when discussing companies or investments."
            )
        elif template_type == "entertainment":
            template_message = (
                "Focus on celebrities, media, and cultural events. "
                "Start with the most exciting or surprising entertainment news. "
                "Include names of key celebrities, shows, films, or events. "
                "Keep the tone light and engaging while remaining informative. "
                "Include interesting details that fans would appreciate. "
                "Avoid speculation or unverified gossip."
            )
        elif template_type == "sports":
            template_message = (
                "Focus on games, athletes, and sporting events. "
                "Start with the most important result or development. "
                "Include key statistics, scores, or records. "
                "Highlight standout performances or dramatic moments. "
                "Provide context about the significance of the news within the sport. "
                "Use dynamic, energetic language that captures the excitement of sports."
            )
        else:
            # Default to general news template
            template_message = (
                "Focus on clarity and importance. "
                "Start with the most newsworthy element of the story. "
                "Answer the key questions: who, what, when, where, why, and how. "
                "Present facts objectively before any analysis or reaction. "
                "Include relevant context that helps viewers understand the significance. "
                "Maintain a balanced, journalistic tone throughout."
            )
            
        return base_message + template_message
    
    def get_template_prompt(self, template_type, article_data):
        """
        Get prompt for a specific template type and article data.
        
        Args:
            template_type (str): Template type to use
            article_data (dict): Article data including title, content, source, etc.
            
        Returns:
            str: Prompt for the template
        """
        # Extract article information
        title = article_data.get("title", "")
        source = article_data.get("source", "")
        description = article_data.get("description", "")
        content = article_data.get("content", "")
        published_date = article_data.get("published", "")
        
        # Format date if available
        date_info = ""
        if published_date:
            try:
                date = datetime.fromisoformat(published_date)
                date_info = f"Published: {date.strftime('%B %d, %Y')}"
            except:
                date_info = f"Published: {published_date}"
        
        # Base prompt for all templates
        base_prompt = f"""
        Write a script for a YouTube Short based on this news article:
        
        Title: {title}
        Source: {source}
        {date_info}
        
        """
        
        # Add description if available
        if description:
            base_prompt += f"Description: {description}\n\n"
            
        # Add content if available (limit length)
        if content:
            base_prompt += f"Content:\n{content[:1500]}...\n\n"
            
        # Template-specific additions
        if template_type == "breaking_news":
            template_prompt = (
                "This is BREAKING NEWS that just happened. "
                "Create an urgent, attention-grabbing script that emphasizes the immediacy and importance of this story. "
                "Start with a powerful headline and focus on the most critical information first. "
                "Use phrases like 'breaking news' or 'just in' to convey urgency."
            )
        elif template_type == "explainer":
            template_prompt = (
                "This news requires explanation to help viewers understand a complex topic. "
                "Create an educational script that breaks down the key concepts in simple terms. "
                "Focus on making the information accessible and easy to understand. "
                "Use a clear, step-by-step approach to explain the topic."
            )
        elif template_type == "feature_story":
            template_prompt = (
                "This is a human interest story that deserves a narrative approach. "
                "Create a compelling script that focuses on the people and emotions involved. "
                "Use descriptive language and storytelling techniques to engage viewers. "
                "Build toward a meaningful conclusion or insight."
            )
        elif template_type == "tech_news":
            template_prompt = (
                "This is technology news that highlights innovation or change. "
                "Create a script that explains technical concepts in accessible language. "
                "Focus on how this technology might impact viewers or change the future. "
                "Include relevant technical details without being overly complex."
            )
        elif template_type == "business_news":
            template_prompt = (
                "This is business or financial news that affects markets or consumers. "
                "Create a script that presents key financial information clearly. "
                "Include relevant numbers but keep them simple and meaningful. "
                "Explain how this business news might impact the average person."
            )
        elif template_type == "entertainment":
            template_prompt = (
                "This is entertainment news about celebrities, media, or cultural events. "
                "Create an engaging script that captures the excitement of the entertainment world. "
                "Focus on the most interesting or surprising aspects of the story. "
                "Keep the tone light and fun while remaining informative."
            )
        elif template_type == "sports":
            template_prompt = (
                "This is sports news about games, athletes, or sporting events. "
                "Create an energetic script that captures the excitement of sports. "
                "Include key statistics or results and highlight standout performances. "
                "Use dynamic language that conveys the action and drama of sports."
            )
        else:
            # Default to general news template
            template_prompt = (
                "Create an informative script that presents this news story clearly and concisely. "
                "Focus on the most important aspects of the story first. "
                "Include the key facts: who, what, when, where, why, and how. "
                "Maintain a balanced, journalistic tone throughout."
            )
            
        return base_prompt + template_prompt
    
    def get_visual_style(self, template_type=None):
        """
        Get visual style guidance for a specific template type.
        
        Args:
            template_type (str, optional): Template type to use
            
        Returns:
            str: Visual style guidance
        """
        if not template_type:
            template_type = self.config["templates"]["default_template"]
            
        # Get visual style from config
        visual_styles = self.config["templates"]["visual_styles"]
        if template_type in visual_styles:
            return visual_styles[template_type]
        else:
            return visual_styles["default_template"]
    
    def get_image_prompt_guidance(self, template_type=None):
        """
        Get image prompt guidance for a specific template type.
        
        Args:
            template_type (str, optional): Template type to use
            
        Returns:
            str: Image prompt guidance
        """
        if not template_type:
            template_type = self.config["templates"]["default_template"]
            
        # Base guidance for all templates
        base_guidance = (
            "Create detailed image prompts that are visually descriptive and focused on journalistic imagery. "
            "Each prompt should NOT include any text overlays or words to appear in the image. "
        )
        
        # Template-specific guidance
        if template_type == "breaking_news":
            template_guidance = (
                "Focus on urgent, high-impact imagery with dramatic lighting and contrast. "
                "Use news photography style with a sense of immediacy. "
                "Include visual elements that convey breaking news like red colors or alert symbols. "
                "Create a sense of importance through composition and lighting."
            )
        elif template_type == "explainer":
            template_guidance = (
                "Focus on clear, educational visuals that help explain concepts. "
                "Include diagrams, illustrations, or infographic-style elements. "
                "Use visual metaphors to make abstract concepts concrete. "
                "Keep the style clean and focused on clarity rather than drama."
            )
        elif template_type == "feature_story":
            template_guidance = (
                "Focus on cinematic, documentary-style visuals with rich colors. "
                "Create imagery that tells a human story with emotional impact. "
                "Use composition that highlights people and their environments. "
                "Include visual details that create a sense of place and atmosphere."
            )
        elif template_type == "tech_news":
            template_guidance = (
                "Focus on modern, clean visuals with technology themes. "
                "Use blue tones and digital elements in the imagery. "
                "Include visual representations of devices, interfaces, or technological concepts. "
                "Create a sense of innovation and future-focused design."
            )
        elif template_type == "business_news":
            template_guidance = (
                "Focus on professional, corporate style imagery. "
                "Include visual elements like charts, graphs, or business settings. "
                "Use a color palette of blues, grays, and other professional tones. "
                "Create compositions that convey professionalism and authority."
            )
        elif template_type == "entertainment":
            template_guidance = (
                "Focus on vibrant, colorful celebrity and entertainment imagery. "
                "Use visual elements associated with media, film, music, or pop culture. "
                "Create dynamic compositions with high visual interest and energy. "
                "Include glamorous lighting and settings appropriate for entertainment news."
            )
        elif template_type == "sports":
            template_guidance = (
                "Focus on dynamic, action-oriented sports photography. "
                "Include visual elements of motion, competition, and athletic achievement. "
                "Use dramatic angles and compositions that capture the energy of sports. "
                "Create a sense of movement through motion blur or action-freezing techniques."
            )
        else:
            # Default guidance
            template_guidance = (
                "Focus on clear, journalistic imagery that tells the news story visually. "
                "Use composition and lighting to highlight the most important elements. "
                "Create visuals that are informative and support the narrative of the news. "
                "Maintain a professional, news-appropriate visual style."
            )
            
        return base_guidance + template_guidance
    
    def get_metadata_guidance(self, template_type=None):
        """
        Get metadata guidance for a specific template type.
        
        Args:
            template_type (str, optional): Template type to use
            
        Returns:
            str: Metadata guidance
        """
        if not template_type:
            template_type = self.config["templates"]["default_template"]
            
        # Base guidance for all templates
        base_guidance = (
            "Create an attention-grabbing title (max 60 characters) and "
            "a compelling description with relevant hashtags (max 200 characters). "
        )
        
        # Template-specific guidance
        if template_type == "breaking_news":
            template_guidance = (
                "Use urgent language in the title like 'BREAKING:' or 'JUST IN:' "
                "Include time-sensitive terms and emphasize recency. "
                "Use hashtags like #BreakingNews #JustIn #NewsAlert in the description. "
                "Create a sense of must-watch immediacy in both title and description."
            )
        elif template_type == "explainer":
            template_guidance = (
                "Use 'How' or 'Why' questions in the title to signal explanation. "
                "Include terms like 'Explained' or 'Understanding' to set expectations. "
                "Use hashtags like #Explained #LearnWithMe #Understanding in the description. "
                "Emphasize the educational value in both title and description."
            )
        elif template_type == "feature_story":
            template_guidance = (
                "Use intriguing, narrative-focused language in the title. "
                "Create curiosity without being clickbait. "
                "Use hashtags like #Story #HumanInterest #RealLife in the description. "
                "Emphasize the emotional or human elements in both title and description."
            )
        elif template_type == "tech_news":
            template_guidance = (
                "Include tech terms or company names in the title. "
                "Signal innovation with words like 'New,' 'Launch,' or 'Update.' "
                "Use hashtags like #Tech #Innovation #TechNews in the description. "
                "Emphasize what's new or changing in both title and description."
            )
        elif template_type == "business_news":
            template_guidance = (
                "Include company names, market terms, or financial indicators in the title. "
                "Use numbers when relevant (percentages, dollar amounts). "
                "Use hashtags like #Business #Markets #Finance in the description. "
                "Emphasize impact or significance in both title and description."
            )
        elif template_type == "entertainment":
            template_guidance = (
                "Include celebrity names or entertainment properties in the title. "
                "Use engaging, upbeat language that captures attention. "
                "Use hashtags like #Celebrity #Entertainment #Movies in the description. "
                "Emphasize what fans and viewers would find most interesting."
            )
        elif template_type == "sports":
            template_guidance = (
                "Include team names, athlete names, or competition references in the title. "
                "Use dynamic, action-oriented language. "
                "Use hashtags like #Sports #Highlights #GameDay in the description. "
                "Emphasize achievements, results, or dramatic moments."
            )
        else:
            # Default guidance
            template_guidance = (
                "Create a clear, informative title that captures the main point of the news. "
                "Balance accuracy with engagement in your wording. "
                "Use hashtags like #News #TrendingNews #CurrentEvents in the description. "
                "Emphasize why this news matters to viewers."
            )
            
        return base_guidance + template_guidance
    
    def get_template_by_category(self, category):
        """
        Get appropriate template type based on news category.
        
        Args:
            category (str): News category
            
        Returns:
            str: Template type
        """
        category = category.lower()
        
        # Map categories to templates
        category_map = {
            "technology": "tech_news",
            "tech": "tech_news",
            "business": "business_news",
            "finance": "business_news",
            "economy": "business_news",
            "entertainment": "entertainment",
            "celebrity": "entertainment",
            "movies": "entertainment",
            "music": "entertainment",
            "sports": "sports",
            "sport": "sports",
            "politics": "breaking_news",
            "world": "breaking_news",
            "breaking": "breaking_news",
            "science": "explainer",
            "health": "explainer",
            "education": "explainer",
            "feature": "feature_story",
            "human interest": "feature_story",
            "lifestyle": "feature_story"
        }
        
        # Return mapped template or default
        return category_map.get(category, self.config["templates"]["default_template"])


# Example usage
if __name__ == "__main__":
    # Create a news shorts template
    template = NewsShortsTemplate()
    
    # Get system message for breaking news template
    system_message = template.get_template_system_message("breaking_news")
    print("System Message for Breaking News:")
    print(system_message)
    print()
    
    # Get prompt for tech news template
    article_data = {
        "title": "New AI Model Breaks Records in Natural Language Understanding",
        "source": "Tech Daily",
        "description": "A groundbreaking new AI model has surpassed human performance on language benchmarks.",
        "published": "2025-03-30T12:00:00"
    }
    prompt = template.get_template_prompt("tech_news", article_data)
    print("Prompt for Tech News:")
    print(prompt)
    print()
    
    # Get visual style for entertainment template
    visual_style = template.get_visual_style("entertainment")
    print("Visual Style for Entertainment:")
    print(visual_style)
    print()
    
    # Get template type by category
    template_type = template.get_template_by_category("sports")
    print(f"Template for 'sports' category: {template_type}")
