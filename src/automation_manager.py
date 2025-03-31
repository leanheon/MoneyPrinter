import os
import json
import time
import schedule
from datetime import datetime, timedelta
from src.monetization.monetization_manager import MonetizationManager
from src.monetization.ebook_monetization import EbookMonetizationManager
from src.integrated_content_manager import IntegratedContentManager
from src.constants import ROOT_DIR

class AutomationManager:
    """
    Class for automating content creation, publishing, and monetization processes
    """
    def __init__(self, google_credentials_path=None, dropbox_token=None):
        """
        Initialize the AutomationManager with all required components
        
        Args:
            google_credentials_path (str): Path to Google API credentials
            dropbox_token (str): Dropbox access token
        """
        # Initialize component managers
        self.content_manager = IntegratedContentManager(google_credentials_path, dropbox_token)
        self.monetization_manager = MonetizationManager()
        self.ebook_monetization = EbookMonetizationManager()
        
        # Create automation directory if it doesn't exist
        self.automation_dir = os.path.join(ROOT_DIR, ".mp", "automation")
        os.makedirs(self.automation_dir, exist_ok=True)
        
        # Load automation configuration
        self.config = self._load_config()
        self.schedules = self._load_schedules()
        self.tasks = self._load_tasks()
        
        # Initialize task queue
        self.task_queue = []
        
    def _load_config(self):
        """
        Load automation configuration from file or create default
        
        Returns:
            dict: Automation configuration
        """
        config_file = os.path.join(self.automation_dir, "config.json")
        
        if os.path.exists(config_file):
            with open(config_file, 'r') as f:
                return json.load(f)
        else:
            # Create default configuration
            default_config = {
                "enabled": True,
                "max_daily_content": 5,
                "max_daily_ebooks": 2,
                "content_types": ["shorts", "blog", "ebook", "social"],
                "platforms": ["youtube", "twitter", "instagram"],
                "monetization_methods": ["affiliate", "digital_product", "ebook_sales"],
                "notification_email": "",
                "log_level": "info"
            }
            
            # Save default configuration
            with open(config_file, 'w') as f:
                json.dump(default_config, f, indent=2)
                
            return default_config
            
    def _load_schedules(self):
        """
        Load automation schedules from file or create default
        
        Returns:
            dict: Automation schedules
        """
        schedules_file = os.path.join(self.automation_dir, "schedules.json")
        
        if os.path.exists(schedules_file):
            with open(schedules_file, 'r') as f:
                return json.load(f)
        else:
            # Create default schedules
            default_schedules = {
                "content_creation": {
                    "shorts": "daily",
                    "blog": "weekly",
                    "ebook": "monthly",
                    "social": "daily"
                },
                "publishing": {
                    "shorts": "daily",
                    "blog": "weekly",
                    "ebook": "monthly",
                    "social": "daily"
                },
                "monetization": {
                    "affiliate_content": "weekly",
                    "ebook_promotion": "weekly",
                    "bundle_creation": "monthly",
                    "sales_report": "weekly"
                }
            }
            
            # Save default schedules
            with open(schedules_file, 'w') as f:
                json.dump(default_schedules, f, indent=2)
                
            return default_schedules
            
    def _load_tasks(self):
        """
        Load automation tasks from file or create default
        
        Returns:
            dict: Automation tasks
        """
        tasks_file = os.path.join(self.automation_dir, "tasks.json")
        
        if os.path.exists(tasks_file):
            with open(tasks_file, 'r') as f:
                return json.load(f)
        else:
            # Create default tasks
            default_tasks = {
                "content_creation": [
                    {
                        "type": "shorts",
                        "topic": "productivity tips",
                        "schedule": "daily",
                        "enabled": True
                    },
                    {
                        "type": "blog",
                        "topic": "digital marketing strategies",
                        "schedule": "weekly",
                        "enabled": True
                    },
                    {
                        "type": "ebook",
                        "topic": "passive income guide",
                        "schedule": "monthly",
                        "enabled": True
                    }
                ],
                "publishing": [
                    {
                        "type": "social",
                        "platform": "twitter",
                        "schedule": "daily",
                        "enabled": True
                    }
                ],
                "monetization": [
                    {
                        "type": "affiliate_content",
                        "topic": "best productivity tools",
                        "schedule": "weekly",
                        "enabled": True
                    },
                    {
                        "type": "ebook_promotion",
                        "schedule": "weekly",
                        "enabled": True
                    }
                ]
            }
            
            # Save default tasks
            with open(tasks_file, 'w') as f:
                json.dump(default_tasks, f, indent=2)
                
            return default_tasks
            
    def save_config(self):
        """
        Save current configuration to file
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            config_file = os.path.join(self.automation_dir, "config.json")
            with open(config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
                
            schedules_file = os.path.join(self.automation_dir, "schedules.json")
            with open(schedules_file, 'w') as f:
                json.dump(self.schedules, f, indent=2)
                
            tasks_file = os.path.join(self.automation_dir, "tasks.json")
            with open(tasks_file, 'w') as f:
                json.dump(self.tasks, f, indent=2)
                
            return True
        except Exception as e:
            print(f"Error saving automation configuration: {e}")
            return False
            
    def add_task(self, task_type, task_data):
        """
        Add a new task to the automation system
        
        Args:
            task_type (str): Type of task (content_creation, publishing, monetization)
            task_data (dict): Task data
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if task_type not in self.tasks:
                self.tasks[task_type] = []
                
            self.tasks[task_type].append(task_data)
            
            # Save updated tasks
            self.save_config()
            
            return True
        except Exception as e:
            print(f"Error adding task: {e}")
            return False
            
    def remove_task(self, task_type, task_index):
        """
        Remove a task from the automation system
        
        Args:
            task_type (str): Type of task (content_creation, publishing, monetization)
            task_index (int): Index of the task to remove
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if task_type not in self.tasks:
                return False
                
            if task_index < 0 or task_index >= len(self.tasks[task_type]):
                return False
                
            self.tasks[task_type].pop(task_index)
            
            # Save updated tasks
            self.save_config()
            
            return True
        except Exception as e:
            print(f"Error removing task: {e}")
            return False
            
    def update_task(self, task_type, task_index, task_data):
        """
        Update an existing task in the automation system
        
        Args:
            task_type (str): Type of task (content_creation, publishing, monetization)
            task_index (int): Index of the task to update
            task_data (dict): Updated task data
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if task_type not in self.tasks:
                return False
                
            if task_index < 0 or task_index >= len(self.tasks[task_type]):
                return False
                
            self.tasks[task_type][task_index] = task_data
            
            # Save updated tasks
            self.save_config()
            
            return True
        except Exception as e:
            print(f"Error updating task: {e}")
            return False
            
    def setup_schedules(self):
        """
        Set up scheduled tasks based on configuration
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Clear existing schedules
            schedule.clear()
            
            # Set up content creation schedules
            for task in self.tasks.get("content_creation", []):
                if not task.get("enabled", True):
                    continue
                    
                task_schedule = task.get("schedule", "daily")
                
                if task_schedule == "daily":
                    schedule.every().day.at("10:00").do(
                        self.execute_content_creation_task, task
                    )
                elif task_schedule == "weekly":
                    schedule.every().monday.at("10:00").do(
                        self.execute_content_creation_task, task
                    )
                elif task_schedule == "monthly":
                    schedule.every(30).days.at("10:00").do(
                        self.execute_content_creation_task, task
                    )
                    
            # Set up publishing schedules
            for task in self.tasks.get("publishing", []):
                if not task.get("enabled", True):
                    continue
                    
                task_schedule = task.get("schedule", "daily")
                
                if task_schedule == "daily":
                    schedule.every().day.at("12:00").do(
                        self.execute_publishing_task, task
                    )
                elif task_schedule == "weekly":
                    schedule.every().wednesday.at("12:00").do(
                        self.execute_publishing_task, task
                    )
                elif task_schedule == "monthly":
                    schedule.every(30).days.at("12:00").do(
                        self.execute_publishing_task, task
                    )
                    
            # Set up monetization schedules
            for task in self.tasks.get("monetization", []):
                if not task.get("enabled", True):
                    continue
                    
                task_schedule = task.get("schedule", "weekly")
                
                if task_schedule == "daily":
                    schedule.every().day.at("14:00").do(
                        self.execute_monetization_task, task
                    )
                elif task_schedule == "weekly":
                    schedule.every().friday.at("14:00").do(
                        self.execute_monetization_task, task
                    )
                elif task_schedule == "monthly":
                    schedule.every(30).days.at("14:00").do(
                        self.execute_monetization_task, task
                    )
                    
            # Set up regular maintenance tasks
            schedule.every().day.at("00:00").do(self.daily_maintenance)
            schedule.every().sunday.at("23:00").do(self.weekly_maintenance)
            schedule.every(30).days.at("23:00").do(self.monthly_maintenance)
            
            return True
        except Exception as e:
            print(f"Error setting up schedules: {e}")
            return False
            
    def execute_content_creation_task(self, task):
        """
        Execute a content creation task
        
        Args:
            task (dict): Task data
            
        Returns:
            dict: Result of task execution
        """
        try:
            task_type = task.get("type", "").lower()
            topic = task.get("topic", "")
            
            if not topic:
                return {"success": False, "error": "No topic provided"}
                
            # Check daily content limits
            daily_count = self.get_daily_content_count()
            if daily_count >= self.config.get("max_daily_content", 5):
                return {"success": False, "error": "Daily content limit reached"}
                
            # Execute based on content type
            if task_type == "shorts":
                # Create a short video
                method = task.get("method", "story")
                result = self.content_manager.enhanced_shorts.create_short_by_method(
                    method, topic, None, None, True
                )
                
            elif task_type == "blog":
                # Create a blog post
                length = task.get("length", "medium")
                blog_post = self.content_manager.blog_generator.generate_blog_post(topic, length)
                saved_files = self.content_manager.blog_generator.save_blog_post(blog_post)
                result = {"success": True, "blog_post": blog_post, "saved_files": saved_files}
                
            elif task_type == "ebook":
                # Create an ebook
                format = task.get("format", "pdf")
                length = task.get("length", "medium")
                chapters = int(task.get("chapters", 5))
                
                # Check ebook limits
                daily_ebooks = self.get_daily_ebook_count()
                if daily_ebooks >= self.config.get("max_daily_ebooks", 2):
                    return {"success": False, "error": "Daily ebook limit reached"}
                    
                ebook = self.content_manager.ebook_generator.generate_ebook(topic, format, length, chapters)
                compiled_files = self.content_manager.ebook_generator.compile_ebook(ebook)
                result = {"success": True, "ebook": ebook, "compiled_files": compiled_files}
                
            elif task_type == "social":
                # Create social media content
                platform = task.get("platform", "twitter")
                with_image = task.get("with_image", True)
                
                if platform.lower() in ["twitter", "x"]:
                    post_data = self.content_manager.social_media_manager.generate_x_post(topic, with_image)
                    result = {"success": True, "platform": "twitter", "post_data": post_data}
                elif platform.lower() == "instagram":
                    post_type = task.get("post_type", "carousel")
                    post_data = self.content_manager.social_media_manager.generate_instagram_post(topic, post_type)
                    result = {"success": True, "platform": "instagram", "post_data": post_data}
                else:
                    result = {"success": False, "error": f"Unsupported platform: {platform}"}
            else:
                result = {"success": False, "error": f"Unsupported content type: {task_type}"}
                
            # Log the result
            self.log_task_result("content_creation", task, result)
            
            return result
        except Exception as e:
            error_msg = str(e)
            result = {"success": False, "error": error_msg}
            self.log_task_result("content_creation", task, result)
            return result
            
    def execute_publishing_task(self, task):
        """
        Execute a publishing task
        
        Args:
            task (dict): Task data
            
        Returns:
            dict: Result of task execution
        """
        try:
            task_type = task.get("type", "").lower()
            platform = task.get("platform", "").lower()
            
            # Get pending content from the content manager
            if task_type == "pending":
                # Process all pending content
                results = self.content_manager.process_all_pending()
                result = {"success": True, "results": results}
                
            elif task_type == "ebook":
                # Publish an ebook to platforms
                ebook_id = task.get("ebook_id")
                
                if not ebook_id:
                    # Get the most recent ebook
                    ebooks = self.ebook_monetization.ebook_products
                    if not ebooks:
                        return {"success": False, "error": "No ebooks available"}
                        
                    # Sort by created date and get the most recent
                    sorted_ebooks = sorted(
                        ebooks.items(), 
                        key=lambda x: x[1].get("created_date", ""), 
                        reverse=True
                    )
                    ebook_id = sorted_ebooks[0][0]
                    
                # Publish to specified platform or default platforms
                if platform:
                    result = self.ebook_monetization.publish_to_platform(ebook_id, platform)
                else:
                    # Publish to all enabled platforms
                    results = []
                    for platform_id, platform_data in self.ebook_monetization.platforms.items():
                        if platform_data.get("enabled", True):
                            platform_result = self.ebook_monetization.publish_to_platform(ebook_id, platform_id)
                            if platform_result:
                                results.append(platform_result)
                                
                    result = {"success": True, "results": results}
                    
            elif task_type == "social":
                # Publish social media content
                content_id = task.get("content_id")
                
                if not content_id:
                    # This is a placeholder for actual social media publishing
                    # In a real implementation, this would use platform APIs
                    result = {"success": True, "message": "Social media publishing simulation"}
                else:
                    result = {"success": True, "content_id": content_id, "platform": platform}
            else:
                result = {"success": False, "error": f"Unsupported publishing type: {task_type}"}
                
            # Log the result
            self.log_task_result("publishing", task, result)
            
            return result
        except Exception as e:
            error_msg = str(e)
            result = {"success": False, "error": error_msg}
            self.log_task_result("publishing", task, result)
            return result
            
    def execute_monetization_task(self, task):
        """
        Execute a monetization task
        
        Args:
            task (dict): Task data
            
        Returns:
            dict: Result of task execution
        """
        try:
            task_type = task.get("type", "").lower()
            
            if task_type == "affiliate_content":
                # Generate affiliate content
                topic = task.get("topic", "")
                platform = task.get("platform", "youtube")
                
                if not topic:
                    return {"success": False, "error": "No topic provided"}
                    
                result = self.monetization_manager.generate_monetized_content(
                    topic, platform, "affiliate"
                )
                
            elif task_type == "ebook_promotion":
                # Generate ebook promotion materials
                ebook_id = task.get("ebook_id")
                
                if not ebook_id:
                    # Get the most recent ebook
                    ebooks = self.ebook_monetization.ebook_products
                    if not ebooks:
                        return {"success": False, "error": "No ebooks available"}
                        
                    # Sort by created date and get the most recent
                    sorted_ebooks = sorted(
                        ebooks.items(), 
                        key=lambda x: x[1].get("created_date", ""), 
                        reverse=True
                    )
                    ebook_id = sorted_ebooks[0][0]
                    
                # Generate sales page
                sales_page = self.ebook_monetization.generate_sales_page(ebook_id)
                
                # Generate email sequence
                email_sequence = self.ebook_monetization.generate_email_sequence(ebook_id, 5)
                
                # Generate social promotions
                social_promotions = {}
                for platform in ["twitter", "facebook", "instagram"]:
                    promotion = self.ebook_monetization.generate_social_promotion(ebook_id, platform)
                    if promotion:
                        social_promotions[platform] = promotion
                        
                result = {
                    "success": True,
                    "ebook_id": ebook_id,
                    "sales_page": sales_page,
                    "email_sequence": email_sequence,
                    "social_promotions": social_promotions
                }
                
            elif task_type == "bundle_creation":
                # Create a bundle of ebooks
                ebooks = self.ebook_monetization.ebook_products
                if not ebooks or len(ebooks) < 2:
                    return {"success": False, "error": "Not enough ebooks for a bundle"}
                    
                # Get the most recent ebooks (up to 3)
                sorted_ebooks = sorted(
                    ebooks.items(), 
                    key=lambda x: x[1].get("created_date", ""), 
                    reverse=True
                )
                
                product_ids = [ebook_id for ebook_id, _ in sorted_ebooks[:3]]
                bundle = self.ebook_monetization.generate_bundle(product_ids)
                
                result = {"success": True, "bundle": bundle}
                
            elif task_type == "affiliate_program":
                # Create an affiliate program for an ebook
                ebook_id = task.get("ebook_id")
                commission_rate = int(task.get("commission_rate", 50))
                
                if not ebook_id:
                    # Get the most recent ebook
                    ebooks = self.ebook_monetization.ebook_products
                    if not ebooks:
                        return {"success": False, "error": "No ebooks available"}
                        
                    # Sort by created date and get the most recent
                    sorted_ebooks = sorted(
                        ebooks.items(), 
                        key=lambda x: x[1].get("created_date", ""), 
                        reverse=True
                    )
                    ebook_id = sorted_ebooks[0][0]
                    
                affiliate_program = self.ebook_monetization.create_affiliate_program(ebook_id, commission_rate)
                
                result = {"success": True, "affiliate_program": affiliate_program}
                
            elif task_type == "sales_report":
                # Generate a sales report
                period = task.get("period", "weekly")
                report = self.ebook_monetization.get_sales_report(period)
                
                result = {"success": True, "report": report}
                
            else:
                result = {"success": False, "error": f"Unsupported monetization type: {task_type}"}
                
            # Log the result
            self.log_task_result("monetization", task, result)
            
            return result
        except Exception as e:
            error_msg = str(e)
            result = {"success": False, "error": error_msg}
            self.log_task_result("monetization", task, result)
            return result
            
    def log_task_result(self, task_category, task, result):
        """
        Log the result of a task execution
        
        Args:
            task_category (str): Category of the task
            task (dict): Task data
            result (dict): Result of task execution
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            log_dir = os.path.join(self.automation_dir, "logs")
            os.makedirs(log_dir, exist_ok=True)
            
            # Create log entry
            log_entry = {
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "category": task_category,
                "task": task,
                "result": result,
                "success": result.get("success", False)
            }
            
            # Determine log file name based on date
            log_date = datetime.now().strftime("%Y-%m-%d")
            log_file = os.path.join(log_dir, f"{log_date}.json")
            
            # Load existing logs if file exists
            logs = []
            if os.path.exists(log_file):
                with open(log_file, 'r') as f:
                    logs = json.load(f)
                    
            # Add new log entry
            logs.append(log_entry)
            
            # Save updated logs
            with open(log_file, 'w') as f:
                json.dump(logs, f, indent=2)
                
            return True
        except Exception as e:
            print(f"Error logging task result: {e}")
            return False
            
    def get_daily_content_count(self):
        """
        Get the count of content created today
        
        Returns:
            int: Number of content items created today
        """
        try:
            log_dir = os.path.join(self.automation_dir, "logs")
            if not os.path.exists(log_dir):
                return 0
                
            # Determine log file name based on date
            log_date = datetime.now().strftime("%Y-%m-%d")
            log_file = os.path.join(log_dir, f"{log_date}.json")
            
            if not os.path.exists(log_file):
                return 0
                
            # Load logs
            with open(log_file, 'r') as f:
                logs = json.load(f)
                
            # Count successful content creation tasks
            count = sum(
                1 for log in logs 
                if log.get("category") == "content_creation" 
                and log.get("success", False)
            )
            
            return count
        except Exception as e:
            print(f"Error getting daily content count: {e}")
            return 0
            
    def get_daily_ebook_count(self):
        """
        Get the count of ebooks created today
        
        Returns:
            int: Number of ebooks created today
        """
        try:
            log_dir = os.path.join(self.automation_dir, "logs")
            if not os.path.exists(log_dir):
                return 0
                
            # Determine log file name based on date
            log_date = datetime.now().strftime("%Y-%m-%d")
            log_file = os.path.join(log_dir, f"{log_date}.json")
            
            if not os.path.exists(log_file):
                return 0
                
            # Load logs
            with open(log_file, 'r') as f:
                logs = json.load(f)
                
            # Count successful ebook creation tasks
            count = sum(
                1 for log in logs 
                if log.get("category") == "content_creation" 
                and log.get("success", False)
                and log.get("task", {}).get("type") == "ebook"
            )
            
            return count
        except Exception as e:
            print(f"Error getting daily ebook count: {e}")
            return 0
            
    def daily_maintenance(self):
        """
        Perform daily maintenance tasks
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Archive old logs
            self._archive_old_logs()
            
            # Check for pending content
            pending_content = self.content_manager.get_pending_content()
            if pending_content:
                # Add task to process pending content
                self.add_task("publishing", {
                    "type": "pending",
                    "schedule": "daily",
                    "enabled": True
                })
                
            return True
        except Exception as e:
            print(f"Error performing daily maintenance: {e}")
            return False
            
    def weekly_maintenance(self):
        """
        Perform weekly maintenance tasks
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Generate weekly sales report
            self.execute_monetization_task({
                "type": "sales_report",
                "period": "weekly"
            })
            
            # Check for ebooks without affiliate programs
            ebooks = self.ebook_monetization.ebook_products
            
            # Load affiliate programs
            affiliate_programs_file = os.path.join(
                self.ebook_monetization.ebook_monetization_dir, 
                "affiliate_programs.json"
            )
            
            affiliate_programs = {}
            if os.path.exists(affiliate_programs_file):
                with open(affiliate_programs_file, 'r') as f:
                    affiliate_programs = json.load(f)
                    
            # Check each ebook
            for ebook_id, ebook in ebooks.items():
                # Check if this ebook has an affiliate program
                has_program = False
                for program_id, program in affiliate_programs.items():
                    if program.get("product_id") == ebook_id:
                        has_program = True
                        break
                        
                if not has_program:
                    # Create affiliate program for this ebook
                    self.execute_monetization_task({
                        "type": "affiliate_program",
                        "ebook_id": ebook_id,
                        "commission_rate": 50
                    })
                    
            return True
        except Exception as e:
            print(f"Error performing weekly maintenance: {e}")
            return False
            
    def monthly_maintenance(self):
        """
        Perform monthly maintenance tasks
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Generate monthly sales report
            self.execute_monetization_task({
                "type": "sales_report",
                "period": "monthly"
            })
            
            # Create bundle if enough ebooks
            ebooks = self.ebook_monetization.ebook_products
            if len(ebooks) >= 3:
                self.execute_monetization_task({
                    "type": "bundle_creation"
                })
                
            return True
        except Exception as e:
            print(f"Error performing monthly maintenance: {e}")
            return False
            
    def _archive_old_logs(self):
        """
        Archive logs older than 30 days
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            log_dir = os.path.join(self.automation_dir, "logs")
            if not os.path.exists(log_dir):
                return True
                
            archive_dir = os.path.join(log_dir, "archive")
            os.makedirs(archive_dir, exist_ok=True)
            
            # Get current date
            current_date = datetime.now()
            
            # Check each log file
            for filename in os.listdir(log_dir):
                if not filename.endswith(".json"):
                    continue
                    
                if filename == "archive":
                    continue
                    
                # Parse date from filename
                try:
                    file_date = datetime.strptime(filename.split(".")[0], "%Y-%m-%d")
                    
                    # Check if file is older than 30 days
                    if (current_date - file_date).days > 30:
                        # Move file to archive
                        os.rename(
                            os.path.join(log_dir, filename),
                            os.path.join(archive_dir, filename)
                        )
                except:
                    # Skip files with invalid names
                    continue
                    
            return True
        except Exception as e:
            print(f"Error archiving old logs: {e}")
            return False
            
    def run_scheduler(self, run_once=False):
        """
        Run the scheduler to execute tasks
        
        Args:
            run_once (bool): Whether to run pending tasks once and return
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Set up schedules
            self.setup_schedules()
            
            if run_once:
                # Run pending tasks once
                schedule.run_pending()
                return True
                
            # Run scheduler continuously
            while self.config.get("enabled", True):
                schedule.run_pending()
                time.sleep(60)  # Check every minute
                
            return True
        except Exception as e:
            print(f"Error running scheduler: {e}")
            return False
            
    def execute_task_now(self, task_type, task_data):
        """
        Execute a task immediately
        
        Args:
            task_type (str): Type of task (content_creation, publishing, monetization)
            task_data (dict): Task data
            
        Returns:
            dict: Result of task execution
        """
        try:
            if task_type == "content_creation":
                return self.execute_content_creation_task(task_data)
            elif task_type == "publishing":
                return self.execute_publishing_task(task_data)
            elif task_type == "monetization":
                return self.execute_monetization_task(task_data)
            else:
                return {"success": False, "error": f"Unsupported task type: {task_type}"}
        except Exception as e:
            error_msg = str(e)
            return {"success": False, "error": error_msg}
            
    def get_task_history(self, days=7, category=None, success_only=False):
        """
        Get history of executed tasks
        
        Args:
            days (int): Number of days to look back
            category (str, optional): Filter by task category
            success_only (bool): Whether to include only successful tasks
            
        Returns:
            list: List of task execution logs
        """
        try:
            log_dir = os.path.join(self.automation_dir, "logs")
            if not os.path.exists(log_dir):
                return []
                
            # Calculate date range
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            # Collect logs from date range
            logs = []
            
            current_date = start_date
            while current_date <= end_date:
                log_date = current_date.strftime("%Y-%m-%d")
                log_file = os.path.join(log_dir, f"{log_date}.json")
                
                if os.path.exists(log_file):
                    with open(log_file, 'r') as f:
                        day_logs = json.load(f)
                        
                        # Apply filters
                        if category:
                            day_logs = [log for log in day_logs if log.get("category") == category]
                            
                        if success_only:
                            day_logs = [log for log in day_logs if log.get("success", False)]
                            
                        logs.extend(day_logs)
                        
                current_date += timedelta(days=1)
                
            # Sort by timestamp
            logs.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
            
            return logs
        except Exception as e:
            print(f"Error getting task history: {e}")
            return []
