import os
import sys
import unittest
import logging
from datetime import datetime

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.classes.NewsShortsGenerator import NewsShortsGenerator
from src.news_crawler import NewsCrawler
from src.news_extractor import NewsExtractor
from src.news_shorts_template import NewsShortsTemplate

# Disable logging for tests
logging.disable(logging.CRITICAL)

class TestNewsShortsGeneration(unittest.TestCase):
    """
    Test cases for the news shorts generation functionality.
    """
    
    def setUp(self):
        """Set up test environment."""
        # Create test article
        self.test_article = {
            "id": "test123",
            "title": "AI Breakthrough Enables Computers to Understand Human Emotions",
            "description": "Scientists have developed a new AI system that can accurately detect and interpret human emotions from facial expressions and voice tones.",
            "url": "https://example.com/ai-emotions",
            "published": datetime.now().isoformat(),
            "source": "Tech News Daily",
            "categories": ["technology", "artificial intelligence"],
            "timestamp": datetime.now().isoformat()
        }
        
        # Create mock extracted content
        self.test_extracted_content = {
            "url": "https://example.com/ai-emotions",
            "title": "AI Breakthrough Enables Computers to Understand Human Emotions",
            "meta_description": "Scientists have developed a new AI system that can accurately detect and interpret human emotions.",
            "meta_keywords": ["AI", "emotions", "technology", "research"],
            "meta_author": "Dr. Jane Smith",
            "meta_date": datetime.now().isoformat(),
            "content": """
            In a groundbreaking development, researchers at the Institute of Advanced AI have created a system that can understand human emotions with unprecedented accuracy.
            
            The new AI model, called EmotionNet, uses a combination of computer vision and natural language processing to analyze facial expressions, voice tones, and contextual cues.
            
            "This represents a major step forward in human-computer interaction," said lead researcher Dr. Jane Smith. "Computers that can understand how we feel will be able to respond more appropriately and provide better assistance."
            
            The system has achieved a 95% accuracy rate in detecting six basic emotions: happiness, sadness, anger, fear, surprise, and disgust. It can also recognize more complex emotional states by combining these basic emotions.
            
            Applications for the technology include improved mental health monitoring, more responsive virtual assistants, and enhanced customer service systems.
            
            The team has published their findings in the journal Nature AI and plans to release an open-source version of the technology later this year.
            
            Privacy advocates have raised concerns about the potential misuse of emotion-detection technology, particularly in surveillance and marketing contexts.
            
            Dr. Smith acknowledges these concerns: "We're developing strict ethical guidelines for the use of this technology. Understanding emotions should be used to help people, not to manipulate or monitor them without consent."
            
            The research was funded by a grant from the National Science Foundation and received no corporate funding.
            """,
            "images": [
                {
                    "url": "https://example.com/images/emotionnet.jpg",
                    "alt": "EmotionNet AI system diagram",
                    "width": "800",
                    "height": "600"
                }
            ],
            "extracted_at": datetime.now().isoformat()
        }
    
    def test_news_crawler_initialization(self):
        """Test that the NewsCrawler initializes correctly."""
        crawler = NewsCrawler()
        self.assertIsNotNone(crawler)
        self.assertIsNotNone(crawler.config)
        self.assertTrue(isinstance(crawler.config, dict))
    
    def test_news_extractor_initialization(self):
        """Test that the NewsExtractor initializes correctly."""
        extractor = NewsExtractor()
        self.assertIsNotNone(extractor)
        self.assertIsNotNone(extractor.config)
        self.assertTrue(isinstance(extractor.config, dict))
    
    def test_news_shorts_template_initialization(self):
        """Test that the NewsShortsTemplate initializes correctly."""
        template = NewsShortsTemplate()
        self.assertIsNotNone(template)
        self.assertIsNotNone(template.config)
        self.assertTrue(isinstance(template.config, dict))
    
    def test_news_shorts_generator_initialization(self):
        """Test that the NewsShortsGenerator initializes correctly."""
        generator = NewsShortsGenerator(topic="AI Technology")
        self.assertIsNotNone(generator)
        self.assertEqual(generator.topic, "AI Technology")
        self.assertIsNotNone(generator.news_crawler)
        self.assertIsNotNone(generator.news_extractor)
        self.assertIsNotNone(generator.template_manager)
    
    def test_template_selection_by_category(self):
        """Test that the correct template is selected based on category."""
        template = NewsShortsTemplate()
        
        # Test various categories
        self.assertEqual(template.get_template_by_category("technology"), "tech_news")
        self.assertEqual(template.get_template_by_category("business"), "business_news")
        self.assertEqual(template.get_template_by_category("sports"), "sports")
        self.assertEqual(template.get_template_by_category("politics"), "breaking_news")
        
        # Test default template for unknown category
        self.assertEqual(template.get_template_by_category("unknown"), template.config["templates"]["default_template"])
    
    def test_generator_with_provided_article(self):
        """Test that the generator works with a provided article."""
        generator = NewsShortsGenerator(article=self.test_article, template_type="tech_news")
        
        # Check that the article was stored
        self.assertEqual(generator.article, self.test_article)
        
        # Mock the extract_article_content method to return test content
        original_extract = generator.extract_article_content
        generator.extract_article_content = lambda article: self.test_extracted_content
        
        # Test script generation
        script = generator.generate_script()
        self.assertIsNotNone(script)
        self.assertTrue(len(script) > 0)
        
        # Test metadata generation
        metadata = generator.generate_metadata()
        self.assertIsNotNone(metadata)
        self.assertTrue("title" in metadata)
        self.assertTrue("description" in metadata)
        
        # Test image prompt generation
        image_prompts = generator.generate_image_prompts()
        self.assertIsNotNone(image_prompts)
        self.assertTrue(len(image_prompts) > 0)
        
        # Restore original method
        generator.extract_article_content = original_extract
    
    def test_different_template_types(self):
        """Test that different template types produce different results."""
        # Create generators with different template types
        tech_generator = NewsShortsGenerator(article=self.test_article, template_type="tech_news")
        breaking_generator = NewsShortsGenerator(article=self.test_article, template_type="breaking_news")
        
        # Mock the extract_article_content method
        tech_generator.extract_article_content = lambda article: self.test_extracted_content
        breaking_generator.extract_article_content = lambda article: self.test_extracted_content
        
        # Generate scripts
        tech_script = tech_generator.generate_script()
        breaking_script = breaking_generator.generate_script()
        
        # Scripts should be different due to different templates
        self.assertNotEqual(tech_script, breaking_script)
        
        # Generate metadata
        tech_metadata = tech_generator.generate_metadata()
        breaking_metadata = breaking_generator.generate_metadata()
        
        # Metadata should be different
        self.assertNotEqual(tech_metadata, breaking_metadata)
    
    def test_visual_style_by_template(self):
        """Test that different templates have different visual styles."""
        template = NewsShortsTemplate()
        
        # Get visual styles for different templates
        tech_style = template.get_visual_style("tech_news")
        breaking_style = template.get_visual_style("breaking_news")
        sports_style = template.get_visual_style("sports")
        
        # Styles should be different
        self.assertNotEqual(tech_style, breaking_style)
        self.assertNotEqual(tech_style, sports_style)
        self.assertNotEqual(breaking_style, sports_style)


if __name__ == "__main__":
    unittest.main()
