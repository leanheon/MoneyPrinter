import os
import sys
import time
import unittest
from datetime import datetime
from src.news_automation_system import NewsAutomationSystem
from src.automation_scheduler import AutomationScheduler
from src.channel_manager import ChannelManager
from src.integrated_workflow import IntegratedWorkflow

class TestAutomationProcess(unittest.TestCase):
    """
    Test suite for the automation process.
    Tests all components individually and their integration.
    """
    
    def setUp(self):
        """Set up test environment."""
        self.news_automation = NewsAutomationSystem()
        self.automation_scheduler = AutomationScheduler()
        self.channel_manager = ChannelManager()
        self.integrated_workflow = IntegratedWorkflow()
        
        # Create test output directory
        self.test_output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "test_output")
        os.makedirs(self.test_output_dir, exist_ok=True)
        
        # Log test start
        self.log_message("Starting automation process tests")
    
    def log_message(self, message):
        """Log a message to the test log file."""
        log_file = os.path.join(self.test_output_dir, "test_log.txt")
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        with open(log_file, "a") as f:
            f.write(f"[{timestamp}] {message}\n")
        
        print(f"[{timestamp}] {message}")
    
    def test_01_news_automation(self):
        """Test the news automation system."""
        self.log_message("Testing news automation system...")
        
        # Add a test news source
        source = self.news_automation.add_news_source(
            name="Test News",
            url="https://news.google.com/rss",
            source_type="rss",
            categories=["test", "news"]
        )
        
        self.assertIsNotNone(source, "Failed to add news source")
        self.log_message(f"Added news source: {source['name']}")
        
        # Crawl news
        articles = self.news_automation.crawl_news(
            source_ids=[source["id"]],
            max_articles=3,
            hours_back=24
        )
        
        self.assertIsInstance(articles, list, "Crawl news should return a list")
        self.log_message(f"Crawled {len(articles)} articles")
        
        # Process articles
        processed_content = self.news_automation.process_articles(
            platforms=["blog", "social"]
        )
        
        self.assertIsInstance(processed_content, list, "Process articles should return a list")
        self.log_message(f"Processed {len(processed_content)} content items")
        
        # Post content
        posted_content = self.news_automation.post_content()
        
        self.assertIsInstance(posted_content, list, "Post content should return a list")
        self.log_message(f"Posted {len(posted_content)} content items")
        
        # Run automation cycle
        cycle_result = self.news_automation.run_automation_cycle(
            source_ids=[source["id"]],
            max_articles=3,
            hours_back=24,
            platforms=["blog", "social"]
        )
        
        self.assertIsInstance(cycle_result, dict, "Run automation cycle should return a dict")
        self.log_message(f"Automation cycle result: {cycle_result}")
        
        self.log_message("News automation system tests passed")
    
    def test_02_channel_manager(self):
        """Test the channel manager."""
        self.log_message("Testing channel manager...")
        
        # Create a test channel
        channel = self.channel_manager.create_channel(
            name="Test Channel",
            theme="Technology",
            personality="Informative",
            target_audience="Tech enthusiasts aged 25-40"
        )
        
        self.assertIsNotNone(channel, "Failed to create channel")
        self.log_message(f"Created channel: {channel['name']}")
        
        # Generate channel content
        content = self.channel_manager.generate_channel_content(
            channel_id=channel["id"],
            content_type="social",
            topic="Latest AI advancements"
        )
        
        self.assertIsInstance(content, list, "Generate channel content should return a list")
        self.assertTrue(len(content) > 0, "Should generate at least one content item")
        self.log_message(f"Generated {len(content)} content items")
        
        # Publish content
        if content:
            publish_result = self.channel_manager.publish_content(content[0]["id"])
            
            self.assertIsInstance(publish_result, dict, "Publish content should return a dict")
            self.log_message(f"Published content with result: {publish_result}")
        
        # Generate content for all channels
        all_content = self.channel_manager.generate_content_for_all_channels()
        
        self.assertIsInstance(all_content, dict, "Generate content for all channels should return a dict")
        self.log_message(f"Generated content for all channels: {all_content}")
        
        # Publish all pending content
        publish_all_result = self.channel_manager.publish_all_pending_content()
        
        self.assertIsInstance(publish_all_result, dict, "Publish all pending content should return a dict")
        self.log_message(f"Published all pending content with result: {publish_all_result}")
        
        # Get channel stats
        stats = self.channel_manager.get_channel_stats(channel["id"])
        
        self.assertIsInstance(stats, dict, "Get channel stats should return a dict")
        self.log_message(f"Channel stats: {stats}")
        
        self.log_message("Channel manager tests passed")
    
    def test_03_automation_scheduler(self):
        """Test the automation scheduler."""
        self.log_message("Testing automation scheduler...")
        
        # Add a test schedule
        schedule = self.automation_scheduler.add_schedule(
            name="Test Schedule",
            interval_hours=6,
            max_articles=5,
            hours_back=12,
            platforms=["blog", "social"]
        )
        
        self.assertIsNotNone(schedule, "Failed to add schedule")
        self.log_message(f"Added schedule: {schedule['name']}")
        
        # Update schedule
        updated_schedule = self.automation_scheduler.update_schedule(
            schedule["id"],
            interval_hours=12,
            max_articles=10
        )
        
        self.assertIsNotNone(updated_schedule, "Failed to update schedule")
        self.assertEqual(updated_schedule["interval_hours"], 12, "Schedule interval should be updated")
        self.log_message(f"Updated schedule: {updated_schedule['name']}")
        
        # Run schedule
        run_result = self.automation_scheduler.run_schedule_now(schedule["id"])
        
        self.assertIsInstance(run_result, dict, "Run schedule should return a dict")
        self.log_message(f"Run schedule result: {run_result}")
        
        # Get scheduler status
        status = self.automation_scheduler.get_scheduler_status()
        
        self.assertIsInstance(status, dict, "Get scheduler status should return a dict")
        self.log_message(f"Scheduler status: {status}")
        
        # Get recent runs
        runs = self.automation_scheduler.get_recent_runs()
        
        self.assertIsInstance(runs, list, "Get recent runs should return a list")
        self.log_message(f"Recent runs: {len(runs)}")
        
        self.log_message("Automation scheduler tests passed")
    
    def test_04_integrated_workflow(self):
        """Test the integrated workflow."""
        self.log_message("Testing integrated workflow...")
        
        # Create a test workflow
        workflow = self.integrated_workflow.create_workflow(
            name="Test Workflow",
            description="A test workflow for integration testing",
            steps=[
                {
                    "id": "step_1",
                    "name": "Crawl News",
                    "type": "news_crawl",
                    "params": {
                        "max_articles": 3,
                        "hours_back": 12
                    }
                },
                {
                    "id": "step_2",
                    "name": "Process Articles",
                    "type": "news_process",
                    "params": {
                        "platforms": ["blog", "social"]
                    }
                },
                {
                    "id": "step_3",
                    "name": "Generate Channel Content",
                    "type": "channel_generate",
                    "params": {
                        "content_type": "social"
                    }
                }
            ]
        )
        
        self.assertIsNotNone(workflow, "Failed to create workflow")
        self.log_message(f"Created workflow: {workflow['name']}")
        
        # Run workflow
        run_result = self.integrated_workflow.run_workflow(workflow["id"])
        
        self.assertIsInstance(run_result, dict, "Run workflow should return a dict")
        self.log_message(f"Run workflow result: {run_result}")
        
        # Schedule workflow
        schedule_result = self.integrated_workflow.schedule_workflow(
            workflow["id"],
            interval_hours=24
        )
        
        self.assertIsInstance(schedule_result, dict, "Schedule workflow should return a dict")
        self.log_message(f"Schedule workflow result: {schedule_result}")
        
        # Create complete content pipeline
        pipeline = self.integrated_workflow.create_complete_content_pipeline(
            name="Test Pipeline",
            news_sources=[
                {
                    "name": "Tech News",
                    "url": "https://news.google.com/rss/search?q=technology",
                    "type": "rss",
                    "categories": ["technology"]
                }
            ],
            channels=[
                {
                    "name": "Tech Channel",
                    "theme": "Technology",
                    "personality": "Informative"
                },
                {
                    "name": "Fun Tech",
                    "theme": "Technology",
                    "personality": "Humorous"
                }
            ],
            schedule_hours=12
        )
        
        self.assertIsInstance(pipeline, dict, "Create complete content pipeline should return a dict")
        self.log_message(f"Created pipeline: {pipeline['name']}")
        
        # Get workflow runs
        runs = self.integrated_workflow.get_workflow_runs(workflow["id"])
        
        self.assertIsInstance(runs, list, "Get workflow runs should return a list")
        self.log_message(f"Workflow runs: {len(runs)}")
        
        # Get stats
        stats = self.integrated_workflow.get_stats()
        
        self.assertIsInstance(stats, dict, "Get stats should return a dict")
        self.log_message(f"Integrated workflow stats: {stats}")
        
        self.log_message("Integrated workflow tests passed")
    
    def test_05_end_to_end(self):
        """Test the end-to-end automation process."""
        self.log_message("Testing end-to-end automation process...")
        
        # Create a complete pipeline
        pipeline = self.integrated_workflow.create_complete_content_pipeline(
            name="E2E Test Pipeline",
            news_sources=[
                {
                    "name": "World News",
                    "url": "https://news.google.com/rss",
                    "type": "rss",
                    "categories": ["news", "world"]
                }
            ],
            channels=[
                {
                    "name": "News Channel",
                    "theme": "Current Events",
                    "personality": "Informative"
                }
            ],
            schedule_hours=24
        )
        
        self.assertIsNotNone(pipeline, "Failed to create pipeline")
        self.log_message(f"Created E2E pipeline: {pipeline['name']}")
        
        # Run the workflow
        run_result = self.integrated_workflow.run_workflow(pipeline["workflow"]["id"])
        
        self.assertIsInstance(run_result, dict, "Run workflow should return a dict")
        self.assertEqual(run_result["status"], "completed", "Workflow should complete successfully")
        self.log_message(f"E2E workflow run result: {run_result}")
        
        # Verify that content was generated and published
        stats = self.integrated_workflow.get_stats()
        
        self.assertIsInstance(stats, dict, "Get stats should return a dict")
        self.log_message(f"E2E test stats: {stats}")
        
        self.log_message("End-to-end automation process tests passed")
    
    def tearDown(self):
        """Clean up after tests."""
        self.log_message("Completed automation process tests")


if __name__ == "__main__":
    unittest.main()
