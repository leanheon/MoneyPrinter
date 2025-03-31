import os
import sys
import argparse
import logging
from datetime import datetime

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.classes.NewsShortsGenerator import NewsShortsGenerator
from src.news_crawler import NewsCrawler

def setup_logging():
    """Set up logging configuration"""
    log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
    os.makedirs(log_dir, exist_ok=True)
    
    log_file = os.path.join(log_dir, f"news_shorts_{datetime.now().strftime('%Y%m%d')}.log")
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    
    return logging.getLogger("news_shorts_main")

def main():
    """Main function to run the News Shorts Generator"""
    logger = setup_logging()
    logger.info("Starting News Shorts Generator")
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='News Shorts Generator - Create short videos from news articles')
    parser.add_argument('--topic', type=str, help='Topic to search for news about')
    parser.add_argument('--category', type=str, help='News category to focus on (technology, business, sports, etc.)')
    parser.add_argument('--template', type=str, help='Template type to use (breaking_news, tech_news, feature_story, etc.)')
    parser.add_argument('--url', type=str, help='Specific news article URL to use')
    parser.add_argument('--trending', action='store_true', help='Use trending news topic')
    parser.add_argument('--list-categories', action='store_true', help='List available news categories')
    parser.add_argument('--list-templates', action='store_true', help='List available template types')
    
    args = parser.parse_args()
    
    # List categories if requested
    if args.list_categories:
        print("Available news categories:")
        print("- technology: Tech news and innovations")
        print("- business: Business and financial news")
        print("- politics: Political news and government")
        print("- health: Health and medical news")
        print("- science: Scientific discoveries and research")
        print("- sports: Sports news and events")
        print("- entertainment: Entertainment and celebrity news")
        print("- world: International and global news")
        return
    
    # List templates if requested
    if args.list_templates:
        print("Available template types:")
        print("- breaking_news: Urgent, time-sensitive news")
        print("- explainer: Educational content explaining complex topics")
        print("- feature_story: Human interest stories with narrative focus")
        print("- tech_news: Technology news with focus on innovation")
        print("- business_news: Business and financial news")
        print("- entertainment: Celebrity and entertainment news")
        print("- sports: Sports news with dynamic presentation")
        return
    
    # Get trending topic if requested
    if args.trending:
        logger.info("Fetching trending news topic")
        crawler = NewsCrawler()
        trending_topics = crawler.get_trending_topics(5)
        
        if trending_topics:
            topic = trending_topics[0]["topic"]
            print(f"Using trending topic: {topic}")
            args.topic = topic
        else:
            logger.warning("No trending topics found")
            print("No trending topics found. Please specify a topic or category.")
            return
    
    # Check if URL is provided
    article = None
    if args.url:
        logger.info(f"Fetching article from URL: {args.url}")
        crawler = NewsCrawler()
        extractor = crawler.news_extractor if hasattr(crawler, 'news_extractor') else None
        
        if extractor:
            article_content = extractor.extract_article(args.url)
            if article_content:
                article = {
                    "id": "custom",
                    "title": article_content.get("title", ""),
                    "description": article_content.get("meta_description", ""),
                    "url": args.url,
                    "published": article_content.get("meta_date", datetime.now().isoformat()),
                    "source": article_content.get("meta_author", "Custom Source"),
                    "categories": article_content.get("meta_keywords", []),
                    "timestamp": datetime.now().isoformat()
                }
                logger.info(f"Successfully extracted article: {article['title']}")
            else:
                logger.error(f"Failed to extract article from {args.url}")
                print(f"Failed to extract article from {args.url}")
                return
    
    # Create news shorts generator
    generator = NewsShortsGenerator(
        topic=args.topic,
        article=article,
        category=args.category,
        template_type=args.template
    )
    
    # Create news short
    print("Generating news short... This may take a few minutes.")
    result = generator.create_news_short()
    
    if result:
        print("\nSuccessfully created news short!")
        print(f"Title: {result['title']}")
        print(f"Description: {result['description']}")
        print(f"Source: {result['news_source']}")
        print(f"Category: {result['category']}")
        print(f"Template: {result['template_type']}")
        print(f"Video path: {result['video_path']}")
        
        # Open video if possible
        try:
            import platform
            import subprocess
            
            system = platform.system()
            if system == "Darwin":  # macOS
                subprocess.call(["open", result['video_path']])
            elif system == "Windows":
                os.startfile(result['video_path'])
            elif system == "Linux":
                subprocess.call(["xdg-open", result['video_path']])
                
            print("\nOpened video in default player.")
        except Exception as e:
            print(f"\nCould not open video automatically: {e}")
            print("Please open the video file manually using the path above.")
    else:
        print("Failed to create news short. Check logs for details.")

if __name__ == "__main__":
    main()
