import os
import json
import time
import logging
import schedule
import threading
from datetime import datetime, timedelta
from src.news_automation_system import NewsAutomationSystem
from src.constants import ROOT_DIR

class AutomationScheduler:
    """
    Scheduler for running the news automation system at regular intervals.
    Includes monitoring and reporting functionality.
    """
    def __init__(self):
        """
        Initialize the AutomationScheduler.
        """
        self.news_automation = NewsAutomationSystem()
        self.output_dir = os.path.join(ROOT_DIR, ".mp", "automation_scheduler")
        self.schedule_file = os.path.join(self.output_dir, "schedule_data.json")
        self.log_file = os.path.join(self.output_dir, "automation.log")
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Set up logging
        logging.basicConfig(
            filename=self.log_file,
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger("AutomationScheduler")
        
        # Load existing schedule data if available
        self.schedule_data = self._load_schedule_data()
        
        # Initialize the scheduler thread
        self.scheduler_thread = None
        self.is_running = False
    
    def _load_schedule_data(self):
        """
        Load schedule data from file.
        
        Returns:
            dict: Schedule data
        """
        if os.path.exists(self.schedule_file):
            try:
                with open(self.schedule_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                self.logger.error(f"Error loading schedule data: {e}")
                
        # Default structure if file doesn't exist or can't be loaded
        return {
            "schedules": [],
            "runs": [],
            "status": "stopped",
            "last_updated": datetime.now().isoformat()
        }
    
    def _save_schedule_data(self):
        """
        Save schedule data to file.
        """
        try:
            self.schedule_data["last_updated"] = datetime.now().isoformat()
            
            with open(self.schedule_file, 'w', encoding='utf-8') as f:
                json.dump(self.schedule_data, f, indent=2)
                
        except Exception as e:
            self.logger.error(f"Error saving schedule data: {e}")
    
    def add_schedule(self, name, interval_hours, source_ids=None, max_articles=10, hours_back=24, platforms=None):
        """
        Add a new schedule.
        
        Args:
            name (str): Name of the schedule
            interval_hours (int): Interval between runs in hours
            source_ids (list): IDs of sources to crawl (None for all)
            max_articles (int): Maximum number of articles to crawl per source
            hours_back (int): Only crawl articles from the last X hours
            platforms (list): Platforms to create content for and post to
            
        Returns:
            dict: Added schedule data
        """
        schedule_id = f"schedule_{len(self.schedule_data['schedules']) + 1}"
        
        schedule_item = {
            "id": schedule_id,
            "name": name,
            "interval_hours": interval_hours,
            "source_ids": source_ids,
            "max_articles": max_articles,
            "hours_back": hours_back,
            "platforms": platforms,
            "enabled": True,
            "next_run": (datetime.now() + timedelta(hours=interval_hours)).isoformat(),
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        self.schedule_data["schedules"].append(schedule_item)
        self._save_schedule_data()
        
        self.logger.info(f"Added new schedule: {name} (every {interval_hours} hours)")
        
        return schedule_item
    
    def update_schedule(self, schedule_id, **kwargs):
        """
        Update an existing schedule.
        
        Args:
            schedule_id (str): ID of the schedule to update
            **kwargs: Fields to update
            
        Returns:
            dict: Updated schedule data or None if not found
        """
        for i, schedule in enumerate(self.schedule_data["schedules"]):
            if schedule["id"] == schedule_id:
                # Update fields
                for key, value in kwargs.items():
                    if key in schedule:
                        schedule[key] = value
                
                schedule["updated_at"] = datetime.now().isoformat()
                
                # Recalculate next run if interval changed
                if "interval_hours" in kwargs:
                    schedule["next_run"] = (datetime.now() + timedelta(hours=kwargs["interval_hours"])).isoformat()
                
                self.schedule_data["schedules"][i] = schedule
                self._save_schedule_data()
                
                self.logger.info(f"Updated schedule: {schedule['name']}")
                
                return schedule
                
        self.logger.warning(f"Schedule not found: {schedule_id}")
        return None
    
    def delete_schedule(self, schedule_id):
        """
        Delete a schedule.
        
        Args:
            schedule_id (str): ID of the schedule to delete
            
        Returns:
            bool: True if deleted, False if not found
        """
        for i, schedule in enumerate(self.schedule_data["schedules"]):
            if schedule["id"] == schedule_id:
                deleted_schedule = self.schedule_data["schedules"].pop(i)
                self._save_schedule_data()
                
                self.logger.info(f"Deleted schedule: {deleted_schedule['name']}")
                
                return True
                
        self.logger.warning(f"Schedule not found: {schedule_id}")
        return False
    
    def enable_schedule(self, schedule_id):
        """
        Enable a schedule.
        
        Args:
            schedule_id (str): ID of the schedule to enable
            
        Returns:
            bool: True if enabled, False if not found
        """
        return self.update_schedule(schedule_id, enabled=True) is not None
    
    def disable_schedule(self, schedule_id):
        """
        Disable a schedule.
        
        Args:
            schedule_id (str): ID of the schedule to disable
            
        Returns:
            bool: True if disabled, False if not found
        """
        return self.update_schedule(schedule_id, enabled=False) is not None
    
    def get_schedules(self):
        """
        Get all schedules.
        
        Returns:
            list: All schedules
        """
        return self.schedule_data["schedules"]
    
    def get_schedule(self, schedule_id):
        """
        Get a specific schedule.
        
        Args:
            schedule_id (str): ID of the schedule to get
            
        Returns:
            dict: Schedule data or None if not found
        """
        for schedule in self.schedule_data["schedules"]:
            if schedule["id"] == schedule_id:
                return schedule
                
        return None
    
    def _run_schedule(self, schedule):
        """
        Run a specific schedule.
        
        Args:
            schedule (dict): Schedule to run
            
        Returns:
            dict: Run result
        """
        self.logger.info(f"Running schedule: {schedule['name']}")
        
        try:
            # Run the automation cycle
            result = self.news_automation.run_automation_cycle(
                source_ids=schedule["source_ids"],
                max_articles=schedule["max_articles"],
                hours_back=schedule["hours_back"],
                platforms=schedule["platforms"]
            )
            
            # Record the run
            run = {
                "id": f"run_{int(time.time())}",
                "schedule_id": schedule["id"],
                "schedule_name": schedule["name"],
                "start_time": datetime.now().isoformat(),
                "end_time": datetime.now().isoformat(),
                "result": result,
                "success": True
            }
            
            self.schedule_data["runs"].append(run)
            
            # Update next run time
            for i, s in enumerate(self.schedule_data["schedules"]):
                if s["id"] == schedule["id"]:
                    self.schedule_data["schedules"][i]["next_run"] = (
                        datetime.now() + timedelta(hours=schedule["interval_hours"])
                    ).isoformat()
                    break
            
            self._save_schedule_data()
            
            self.logger.info(f"Schedule completed: {schedule['name']} - Crawled: {result['crawled_articles']}, Processed: {result['processed_content']}, Posted: {result['posted_content']}")
            
            return run
            
        except Exception as e:
            error_message = str(e)
            self.logger.error(f"Error running schedule {schedule['name']}: {error_message}")
            
            # Record the failed run
            run = {
                "id": f"run_{int(time.time())}",
                "schedule_id": schedule["id"],
                "schedule_name": schedule["name"],
                "start_time": datetime.now().isoformat(),
                "end_time": datetime.now().isoformat(),
                "result": {"error": error_message},
                "success": False
            }
            
            self.schedule_data["runs"].append(run)
            
            # Update next run time
            for i, s in enumerate(self.schedule_data["schedules"]):
                if s["id"] == schedule["id"]:
                    self.schedule_data["schedules"][i]["next_run"] = (
                        datetime.now() + timedelta(hours=schedule["interval_hours"])
                    ).isoformat()
                    break
            
            self._save_schedule_data()
            
            return run
    
    def run_schedule_now(self, schedule_id):
        """
        Run a specific schedule immediately.
        
        Args:
            schedule_id (str): ID of the schedule to run
            
        Returns:
            dict: Run result or None if schedule not found
        """
        schedule = self.get_schedule(schedule_id)
        
        if schedule:
            return self._run_schedule(schedule)
        else:
            self.logger.warning(f"Schedule not found: {schedule_id}")
            return None
    
    def _scheduler_loop(self):
        """
        Main scheduler loop that checks for schedules to run.
        """
        self.logger.info("Scheduler loop started")
        
        while self.is_running:
            try:
                # Check for schedules to run
                now = datetime.now()
                
                for schedule in self.schedule_data["schedules"]:
                    if not schedule["enabled"]:
                        continue
                        
                    next_run = datetime.fromisoformat(schedule["next_run"].replace('Z', '+00:00'))
                    
                    if now >= next_run:
                        self._run_schedule(schedule)
                
                # Sleep for a minute before checking again
                time.sleep(60)
                
            except Exception as e:
                self.logger.error(f"Error in scheduler loop: {e}")
                time.sleep(60)  # Sleep and try again
    
    def start_scheduler(self):
        """
        Start the scheduler.
        
        Returns:
            bool: True if started, False if already running
        """
        if self.is_running:
            self.logger.warning("Scheduler is already running")
            return False
        
        self.is_running = True
        self.schedule_data["status"] = "running"
        self._save_schedule_data()
        
        # Start the scheduler thread
        self.scheduler_thread = threading.Thread(target=self._scheduler_loop)
        self.scheduler_thread.daemon = True
        self.scheduler_thread.start()
        
        self.logger.info("Scheduler started")
        
        return True
    
    def stop_scheduler(self):
        """
        Stop the scheduler.
        
        Returns:
            bool: True if stopped, False if not running
        """
        if not self.is_running:
            self.logger.warning("Scheduler is not running")
            return False
        
        self.is_running = False
        self.schedule_data["status"] = "stopped"
        self._save_schedule_data()
        
        # Wait for the thread to finish
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=5)
            self.scheduler_thread = None
        
        self.logger.info("Scheduler stopped")
        
        return True
    
    def get_scheduler_status(self):
        """
        Get the current status of the scheduler.
        
        Returns:
            dict: Scheduler status
        """
        return {
            "status": self.schedule_data["status"],
            "is_running": self.is_running,
            "schedules_count": len(self.schedule_data["schedules"]),
            "enabled_schedules_count": len([s for s in self.schedule_data["schedules"] if s["enabled"]]),
            "runs_count": len(self.schedule_data["runs"]),
            "last_updated": self.schedule_data["last_updated"]
        }
    
    def get_recent_runs(self, limit=10):
        """
        Get recent runs.
        
        Args:
            limit (int): Maximum number of runs to return
            
        Returns:
            list: Recent runs
        """
        # Sort runs by start time (newest first)
        sorted_runs = sorted(
            self.schedule_data["runs"],
            key=lambda r: r["start_time"],
            reverse=True
        )
        
        return sorted_runs[:limit]
    
    def get_run(self, run_id):
        """
        Get a specific run.
        
        Args:
            run_id (str): ID of the run to get
            
        Returns:
            dict: Run data or None if not found
        """
        for run in self.schedule_data["runs"]:
            if run["id"] == run_id:
                return run
                
        return None
    
    def get_schedule_runs(self, schedule_id, limit=10):
        """
        Get runs for a specific schedule.
        
        Args:
            schedule_id (str): ID of the schedule
            limit (int): Maximum number of runs to return
            
        Returns:
            list: Runs for the schedule
        """
        # Filter runs by schedule ID and sort by start time (newest first)
        schedule_runs = [r for r in self.schedule_data["runs"] if r["schedule_id"] == schedule_id]
        sorted_runs = sorted(schedule_runs, key=lambda r: r["start_time"], reverse=True)
        
        return sorted_runs[:limit]
    
    def get_performance_stats(self):
        """
        Get performance statistics.
        
        Returns:
            dict: Performance statistics
        """
        if not self.schedule_data["runs"]:
            return {
                "total_runs": 0,
                "successful_runs": 0,
                "failed_runs": 0,
                "success_rate": 0,
                "total_articles_crawled": 0,
                "total_content_processed": 0,
                "total_content_posted": 0,
                "average_articles_per_run": 0,
                "average_content_per_run": 0,
                "average_posts_per_run": 0
            }
        
        # Calculate statistics
        total_runs = len(self.schedule_data["runs"])
        successful_runs = len([r for r in self.schedule_data["runs"] if r["success"]])
        failed_runs = total_runs - successful_runs
        success_rate = successful_runs / total_runs if total_runs > 0 else 0
        
        total_articles_crawled = 0
        total_content_processed = 0
        total_content_posted = 0
        
        for run in self.schedule_data["runs"]:
            if run["success"] and "result" in run:
                result = run["result"]
                total_articles_crawled += result.get("crawled_articles", 0)
                total_content_processed += result.get("processed_content", 0)
                total_content_posted += result.get("posted_content", 0)
        
        average_articles_per_run = total_articles_crawled / successful_runs if successful_runs > 0 else 0
        average_content_per_run = total_content_processed / successful_runs if successful_runs > 0 else 0
        average_posts_per_run = total_content_posted / successful_runs if successful_runs > 0 else 0
        
        return {
            "total_runs": total_runs,
            "successful_runs": successful_runs,
            "failed_runs": failed_runs,
            "success_rate": success_rate,
            "total_articles_crawled": total_articles_crawled,
            "total_content_processed": total_content_processed,
            "total_content_posted": total_content_posted,
            "average_articles_per_run": average_articles_per_run,
            "average_content_per_run": average_content_per_run,
            "average_posts_per_run": average_posts_per_run
        }
