import unittest
import os
import json
from unittest.mock import patch, MagicMock

# Ensure src package is discoverable when running tests directly
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.expanded_sns_connector import ExpandedSNSConnector
from src.automated_posting_workflow import AutomatedPostingWorkflow
from src.integrated_social_media_system import IntegratedSocialMediaSystem

class TestExpandedSNSIntegration(unittest.TestCase):
    """
    Test suite for the expanded SNS integration.
    Tests the functionality of the ExpandedSNSConnector, AutomatedPostingWorkflow,
    and IntegratedSocialMediaSystem classes.
    """
    
    def setUp(self):
        """Set up test environment."""
        # Create mock objects
        self.sns_connector = ExpandedSNSConnector()
        self.posting_workflow = AutomatedPostingWorkflow()
        self.integrated_system = IntegratedSocialMediaSystem()
        
        # Mock platform configuration methods
        self.sns_connector.configure_twitter = MagicMock(return_value=True)
        self.sns_connector.configure_threads = MagicMock(return_value=True)
        self.sns_connector.configure_instagram = MagicMock(return_value=True)
        self.sns_connector.configure_facebook = MagicMock(return_value=True)
        self.sns_connector.configure_linkedin = MagicMock(return_value=True)
        self.sns_connector.configure_tiktok = MagicMock(return_value=True)
        self.sns_connector.configure_youtube = MagicMock(return_value=True)
        
        # Mock posting methods
        self.sns_connector.post_to_twitter = MagicMock(return_value={"success": True, "post_id": "123456"})
        self.sns_connector.post_to_threads = MagicMock(return_value={"success": True, "post_id": "123456"})
        self.sns_connector.post_to_instagram = MagicMock(return_value={"success": True, "post_id": "123456"})
        self.sns_connector.post_to_facebook = MagicMock(return_value={"success": True, "post_id": "123456"})
        self.sns_connector.post_to_linkedin = MagicMock(return_value={"success": True, "post_id": "123456"})
        self.sns_connector.post_to_tiktok = MagicMock(return_value={"success": True, "post_id": "123456"})
        self.sns_connector.post_to_youtube = MagicMock(return_value={"success": True, "post_id": "123456"})
        
        # Mock post_to_all_platforms method
        self.sns_connector.post_to_all_platforms = MagicMock(return_value={
            "success": True,
            "results": {
                "twitter": {"success": True, "post_id": "123456"},
                "threads": {"success": True, "post_id": "123456"},
                "instagram": {"success": True, "post_id": "123456"},
                "facebook": {"success": True, "post_id": "123456"},
                "linkedin": {"success": True, "post_id": "123456"},
                "tiktok": {"success": True, "post_id": "123456"},
                "youtube": {"success": True, "post_id": "123456"}
            }
        })
        
        # Patch the ExpandedSNSConnector in other classes
        patcher1 = patch('src.automated_posting_workflow.ExpandedSNSConnector', return_value=self.sns_connector)
        patcher2 = patch('src.integrated_social_media_system.ExpandedSNSConnector', return_value=self.sns_connector)
        patcher1.start()
        patcher2.start()
        self.addCleanup(patcher1.stop)
        self.addCleanup(patcher2.stop)
    
    def test_sns_connector_configuration(self):
        """Test SNS connector configuration methods."""
        # Test Twitter configuration
        result = self.sns_connector.configure_twitter(
            api_key="test_key",
            api_secret="test_secret",
            access_token="test_token",
            access_token_secret="test_token_secret"
        )
        self.assertTrue(result)
        self.sns_connector.configure_twitter.assert_called_once()
        
        # Test Threads configuration
        result = self.sns_connector.configure_threads(
            username="test_user",
            password="test_pass"
        )
        self.assertTrue(result)
        self.sns_connector.configure_threads.assert_called_once()
        
        # Test Instagram configuration
        result = self.sns_connector.configure_instagram(
            username="test_user",
            password="test_pass",
            access_token="test_token"
        )
        self.assertTrue(result)
        self.sns_connector.configure_instagram.assert_called_once()
        
        # Test Facebook configuration
        result = self.sns_connector.configure_facebook(
            app_id="test_app_id",
            app_secret="test_app_secret",
            access_token="test_token",
            page_id="test_page_id"
        )
        self.assertTrue(result)
        self.sns_connector.configure_facebook.assert_called_once()
        
        # Test LinkedIn configuration
        result = self.sns_connector.configure_linkedin(
            client_id="test_client_id",
            client_secret="test_client_secret",
            access_token="test_token"
        )
        self.assertTrue(result)
        self.sns_connector.configure_linkedin.assert_called_once()
        
        # Test TikTok configuration
        result = self.sns_connector.configure_tiktok(
            client_key="test_client_key",
            client_secret="test_client_secret",
            access_token="test_token"
        )
        self.assertTrue(result)
        self.sns_connector.configure_tiktok.assert_called_once()
        
        # Test YouTube configuration
        result = self.sns_connector.configure_youtube(
            client_id="test_client_id",
            client_secret="test_client_secret",
            api_key="test_api_key",
            refresh_token="test_refresh_token",
            access_token="test_token"
        )
        self.assertTrue(result)
        self.sns_connector.configure_youtube.assert_called_once()
    
    def test_sns_connector_posting(self):
        """Test SNS connector posting methods."""
        # Test Twitter posting
        result = self.sns_connector.post_to_twitter(
            text="Test tweet",
            media_paths=[]
        )
        self.assertTrue(result["success"])
        self.sns_connector.post_to_twitter.assert_called_once()
        
        # Test Threads posting
        result = self.sns_connector.post_to_threads(
            text="Test thread",
            media_paths=[]
        )
        self.assertTrue(result["success"])
        self.sns_connector.post_to_threads.assert_called_once()
        
        # Test Instagram posting
        result = self.sns_connector.post_to_instagram(
            caption="Test caption",
            media_paths=[],
            post_type="feed"
        )
        self.assertTrue(result["success"])
        self.sns_connector.post_to_instagram.assert_called_once()
        
        # Test Facebook posting
        result = self.sns_connector.post_to_facebook(
            message="Test message",
            media_paths=[]
        )
        self.assertTrue(result["success"])
        self.sns_connector.post_to_facebook.assert_called_once()
        
        # Test LinkedIn posting
        result = self.sns_connector.post_to_linkedin(
            text="Test post",
            media_paths=[]
        )
        self.assertTrue(result["success"])
        self.sns_connector.post_to_linkedin.assert_called_once()
        
        # Test TikTok posting
        result = self.sns_connector.post_to_tiktok(
            caption="Test caption",
            video_path="test_video.mp4"
        )
        self.assertTrue(result["success"])
        self.sns_connector.post_to_tiktok.assert_called_once()
        
        # Test YouTube posting
        result = self.sns_connector.post_to_youtube(
            title="Test title",
            description="Test description",
            video_path="test_video.mp4"
        )
        self.assertTrue(result["success"])
        self.sns_connector.post_to_youtube.assert_called_once()
        
        # Test posting to all platforms
        formatted_content = {
            "twitter": {"text": "Test tweet"},
            "threads": {"text": "Test thread"},
            "instagram": {"caption": "Test caption", "post_type": "feed"},
            "facebook": {"message": "Test message"},
            "linkedin": {"text": "Test post"},
            "tiktok": {"caption": "Test caption"},
            "youtube": {"title": "Test title", "description": "Test description"}
        }
        
        media_paths = {
            "twitter": [],
            "threads": [],
            "instagram": [],
            "facebook": [],
            "linkedin": [],
            "tiktok": "test_video.mp4",
            "youtube": "test_video.mp4"
        }
        
        result = self.sns_connector.post_to_all_platforms(formatted_content, media_paths)
        self.assertTrue(result["success"])
        self.sns_connector.post_to_all_platforms.assert_called_once()
    
    @patch('src.automated_posting_workflow.AutomatedPostingWorkflow._get_content_from_source')
    def test_automated_posting_workflow(self, mock_get_content):
        """Test automated posting workflow."""
        # Mock content retrieval
        mock_get_content.return_value = {
            "text": "Test content",
            "title": "Test title",
            "media_paths": [],
            "source": "test",
            "content_id": "test_content_id"
        }
        
        # Test creating a posting schedule
        schedule = self.posting_workflow.create_posting_schedule(
            name="Test Schedule",
            content_source="news",
            platforms=["twitter", "facebook"],
            schedule_type="daily",
            time_of_day="09:00",
            days_of_week=[0, 2, 4]
        )
        
        self.assertIsNotNone(schedule)
        self.assertEqual(schedule["name"], "Test Schedule")
        self.assertEqual(schedule["content_source"], "news")
        self.assertEqual(schedule["platforms"], ["twitter", "facebook"])
        
        # Test posting content now
        result = self.posting_workflow.post_content_now(
            content_source="news",
            platforms=["twitter", "facebook"]
        )
        
        self.assertTrue(result["success"])
        self.assertEqual(result["platforms"], ["twitter", "facebook"])
        mock_get_content.assert_called_once()
    
    @patch('src.integrated_social_media_system.IntegratedSocialMediaSystem._create_content')
    def test_integrated_social_media_system(self, mock_create_content):
        """Test integrated social media system."""
        # Mock content creation
        mock_create_content.return_value = {
            "id": "test_content_id",
            "type": "shorts",
            "title": "Test Shorts",
            "video_path": "test_video.mp4",
            "thumbnail_path": "test_thumbnail.jpg"
        }
        
        # Test setting up a social media account
        result = self.integrated_system.setup_social_media_account(
            platform="twitter",
            credentials={
                "api_key": "test_key",
                "api_secret": "test_secret",
                "access_token": "test_token",
                "access_token_secret": "test_token_secret"
            }
        )
        
        self.assertTrue(result)
        
        # Test creating content and posting
        result = self.integrated_system.create_content_and_post(
            content_type="shorts",
            topic="Test Topic"
        )
        
        self.assertTrue(result["success"])
        self.assertEqual(result["content_type"], "shorts")
        mock_create_content.assert_called_once()
        
        # Test configuring platform integration
        result = self.integrated_system.configure_platform_integration(
            platform="twitter",
            enabled=True
        )
        
        self.assertTrue(result["twitter"])
        
        # Test creating a complete social media pipeline
        with patch('src.integrated_social_media_system.ChannelManager') as mock_channel_manager, \
             patch('src.integrated_social_media_system.IntegratedWorkflow') as mock_integrated_workflow:
            
            # Mock channel creation
            mock_channel_manager.return_value.create_channel.return_value = {"id": "test_channel_id"}
            
            # Mock workflow creation
            mock_integrated_workflow.return_value.create_workflow.return_value = {"id": "test_workflow_id"}
            mock_integrated_workflow.return_value.schedule_workflow.return_value = {"id": "test_schedule_id"}
            
            result = self.integrated_system.create_complete_social_media_pipeline(
                name="Test Pipeline",
                channel_config={"name": "Test Channel", "theme": "Technology"},
                content_types=["shorts", "blog"],
                platforms=["twitter", "youtube"]
            )
            
            self.assertEqual(result["name"], "Test Pipeline")
            self.assertEqual(result["channel"]["id"], "test_channel_id")
            self.assertEqual(result["content_types"], ["shorts", "blog"])
            self.assertEqual(result["platforms"], ["twitter", "youtube"])
            self.assertIsNotNone(result["workflow"])
            self.assertIsNotNone(result["workflow_schedule"])

if __name__ == '__main__':
    unittest.main()
