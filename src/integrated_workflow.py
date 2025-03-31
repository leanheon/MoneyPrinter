import os
import json
import time
from datetime import datetime
from src.news_automation_system import NewsAutomationSystem
from src.automation_scheduler import AutomationScheduler
from src.channel_manager import ChannelManager
from src.constants import ROOT_DIR

class IntegratedWorkflow:
    """
    Integrated workflow system that combines news automation, scheduling, and multi-channel management
    into a complete content production and distribution pipeline.
    """
    def __init__(self, dropbox_token=None):
        """
        Initialize the IntegratedWorkflow.
        
        Args:
            dropbox_token (str): Optional Dropbox access token for uploading videos
        """
        self.news_automation = NewsAutomationSystem()
        self.automation_scheduler = AutomationScheduler()
        self.channel_manager = ChannelManager(dropbox_token)
        
        self.output_dir = os.path.join(ROOT_DIR, ".mp", "integrated_workflow")
        self.data_file = os.path.join(self.output_dir, "workflow_data.json")
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Load existing data if available
        self.workflow_data = self._load_data()
        
    def _load_data(self):
        """
        Load workflow data from file.
        
        Returns:
            dict: Workflow data
        """
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading workflow data: {e}")
                
        # Default structure if file doesn't exist or can't be loaded
        return {
            "workflows": [],
            "runs": [],
            "stats": {
                "total_workflows": 0,
                "total_runs": 0,
                "content_generated": 0,
                "content_published": 0
            },
            "last_updated": datetime.now().isoformat()
        }
    
    def _save_data(self):
        """
        Save workflow data to file.
        """
        try:
            self.workflow_data["last_updated"] = datetime.now().isoformat()
            self.workflow_data["stats"]["total_workflows"] = len(self.workflow_data["workflows"])
            self.workflow_data["stats"]["total_runs"] = len(self.workflow_data["runs"])
            
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.workflow_data, f, indent=2)
                
        except Exception as e:
            print(f"Error saving workflow data: {e}")
    
    def create_workflow(self, name, description, steps=None):
        """
        Create a new workflow.
        
        Args:
            name (str): Name of the workflow
            description (str): Description of the workflow
            steps (list): Steps in the workflow
            
        Returns:
            dict: Created workflow data
        """
        workflow_id = f"workflow_{len(self.workflow_data['workflows']) + 1}"
        
        # Default steps if not provided
        if not steps:
            steps = [
                {
                    "id": "step_1",
                    "name": "Crawl News",
                    "type": "news_crawl",
                    "params": {
                        "max_articles": 10,
                        "hours_back": 24
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
                        "content_type": "shorts"
                    }
                },
                {
                    "id": "step_4",
                    "name": "Publish Content",
                    "type": "publish_all",
                    "params": {}
                }
            ]
        
        workflow = {
            "id": workflow_id,
            "name": name,
            "description": description,
            "steps": steps,
            "enabled": True,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        self.workflow_data["workflows"].append(workflow)
        self._save_data()
        
        return workflow
    
    def update_workflow(self, workflow_id, **kwargs):
        """
        Update an existing workflow.
        
        Args:
            workflow_id (str): ID of the workflow to update
            **kwargs: Fields to update
            
        Returns:
            dict: Updated workflow data or None if not found
        """
        for i, workflow in enumerate(self.workflow_data["workflows"]):
            if workflow["id"] == workflow_id:
                # Update fields
                for key, value in kwargs.items():
                    if key in workflow:
                        workflow[key] = value
                
                workflow["updated_at"] = datetime.now().isoformat()
                
                self.workflow_data["workflows"][i] = workflow
                self._save_data()
                
                return workflow
                
        return None
    
    def delete_workflow(self, workflow_id):
        """
        Delete a workflow.
        
        Args:
            workflow_id (str): ID of the workflow to delete
            
        Returns:
            bool: True if deleted, False if not found
        """
        for i, workflow in enumerate(self.workflow_data["workflows"]):
            if workflow["id"] == workflow_id:
                self.workflow_data["workflows"].pop(i)
                self._save_data()
                return True
                
        return False
    
    def get_workflows(self):
        """
        Get all workflows.
        
        Returns:
            list: All workflows
        """
        return self.workflow_data["workflows"]
    
    def get_workflow(self, workflow_id):
        """
        Get a specific workflow.
        
        Args:
            workflow_id (str): ID of the workflow to get
            
        Returns:
            dict: Workflow data or None if not found
        """
        for workflow in self.workflow_data["workflows"]:
            if workflow["id"] == workflow_id:
                return workflow
                
        return None
    
    def run_workflow(self, workflow_id):
        """
        Run a specific workflow.
        
        Args:
            workflow_id (str): ID of the workflow to run
            
        Returns:
            dict: Run result
        """
        workflow = self.get_workflow(workflow_id)
        
        if not workflow:
            raise ValueError(f"Workflow not found: {workflow_id}")
        
        if not workflow["enabled"]:
            raise ValueError(f"Workflow is disabled: {workflow_id}")
        
        run_id = f"run_{int(time.time())}"
        
        run = {
            "id": run_id,
            "workflow_id": workflow_id,
            "workflow_name": workflow["name"],
            "start_time": datetime.now().isoformat(),
            "steps_results": [],
            "status": "running"
        }
        
        # Add run to data
        self.workflow_data["runs"].append(run)
        self._save_data()
        
        try:
            # Run each step in the workflow
            for step in workflow["steps"]:
                step_result = self._run_workflow_step(step)
                
                run["steps_results"].append({
                    "step_id": step["id"],
                    "step_name": step["name"],
                    "step_type": step["type"],
                    "result": step_result,
                    "success": True
                })
                
                # Update run in data
                for i, r in enumerate(self.workflow_data["runs"]):
                    if r["id"] == run_id:
                        self.workflow_data["runs"][i]["steps_results"] = run["steps_results"]
                        break
                
                self._save_data()
            
            # Update run status
            for i, r in enumerate(self.workflow_data["runs"]):
                if r["id"] == run_id:
                    self.workflow_data["runs"][i]["status"] = "completed"
                    self.workflow_data["runs"][i]["end_time"] = datetime.now().isoformat()
                    break
            
            self._save_data()
            
            return {
                "run_id": run_id,
                "workflow_id": workflow_id,
                "status": "completed",
                "steps_completed": len(workflow["steps"]),
                "steps_results": run["steps_results"]
            }
            
        except Exception as e:
            error_message = str(e)
            print(f"Error running workflow {workflow_id}: {error_message}")
            
            # Update run status
            for i, r in enumerate(self.workflow_data["runs"]):
                if r["id"] == run_id:
                    self.workflow_data["runs"][i]["status"] = "failed"
                    self.workflow_data["runs"][i]["error"] = error_message
                    self.workflow_data["runs"][i]["end_time"] = datetime.now().isoformat()
                    break
            
            self._save_data()
            
            return {
                "run_id": run_id,
                "workflow_id": workflow_id,
                "status": "failed",
                "error": error_message,
                "steps_completed": len(run["steps_results"]),
                "steps_results": run["steps_results"]
            }
    
    def _run_workflow_step(self, step):
        """
        Run a specific workflow step.
        
        Args:
            step (dict): Step data
            
        Returns:
            dict: Step result
        """
        step_type = step["type"]
        params = step.get("params", {})
        
        if step_type == "news_crawl":
            return self.news_automation.crawl_news(
                source_ids=params.get("source_ids"),
                max_articles=params.get("max_articles", 10),
                hours_back=params.get("hours_back", 24)
            )
            
        elif step_type == "news_process":
            return self.news_automation.process_articles(
                article_ids=params.get("article_ids"),
                platforms=params.get("platforms")
            )
            
        elif step_type == "news_post":
            return self.news_automation.post_content(
                content_ids=params.get("content_ids"),
                platforms=params.get("platforms")
            )
            
        elif step_type == "news_cycle":
            return self.news_automation.run_automation_cycle(
                source_ids=params.get("source_ids"),
                max_articles=params.get("max_articles", 10),
                hours_back=params.get("hours_back", 24),
                platforms=params.get("platforms")
            )
            
        elif step_type == "channel_generate":
            channel_id = params.get("channel_id")
            
            if channel_id:
                return self.channel_manager.generate_channel_content(
                    channel_id=channel_id,
                    content_type=params.get("content_type"),
                    topic=params.get("topic"),
                    count=params.get("count", 1)
                )
            else:
                return self.channel_manager.generate_content_for_all_channels(
                    content_type=params.get("content_type")
                )
                
        elif step_type == "channel_publish":
            content_id = params.get("content_id")
            
            if content_id:
                return self.channel_manager.publish_content(content_id)
            else:
                return self.channel_manager.publish_all_pending_content()
                
        elif step_type == "publish_all":
            # Publish all pending content from both systems
            news_result = self.news_automation.post_content()
            channel_result = self.channel_manager.publish_all_pending_content()
            
            return {
                "news": news_result,
                "channel": channel_result
            }
            
        elif step_type == "schedule_add":
            return self.automation_scheduler.add_schedule(
                name=params.get("name", f"Schedule {int(time.time())}"),
                interval_hours=params.get("interval_hours", 6),
                source_ids=params.get("source_ids"),
                max_articles=params.get("max_articles", 10),
                hours_back=params.get("hours_back", 24),
                platforms=params.get("platforms")
            )
            
        elif step_type == "schedule_run":
            schedule_id = params.get("schedule_id")
            
            if schedule_id:
                return self.automation_scheduler.run_schedule_now(schedule_id)
            else:
                return {"error": "No schedule_id provided"}
                
        else:
            return {"error": f"Unknown step type: {step_type}"}
    
    def schedule_workflow(self, workflow_id, interval_hours=24):
        """
        Schedule a workflow to run at regular intervals.
        
        Args:
            workflow_id (str): ID of the workflow to schedule
            interval_hours (int): Interval between runs in hours
            
        Returns:
            dict: Scheduling information
        """
        workflow = self.get_workflow(workflow_id)
        
        if not workflow:
            raise ValueError(f"Workflow not found: {workflow_id}")
        
        # Create a schedule in the automation scheduler
        schedule = self.automation_scheduler.add_schedule(
            name=f"Workflow: {workflow['name']}",
            interval_hours=interval_hours,
            source_ids=None,  # Will be handled by the workflow
            max_articles=10,
            hours_back=24,
            platforms=None  # Will be handled by the workflow
        )
        
        # Update the workflow with the schedule information
        self.update_workflow(
            workflow_id,
            schedule_id=schedule["id"],
            schedule_interval=interval_hours,
            next_run=schedule["next_run"]
        )
        
        return {
            "workflow_id": workflow_id,
            "schedule_id": schedule["id"],
            "interval_hours": interval_hours,
            "next_run": schedule["next_run"]
        }
    
    def create_complete_content_pipeline(self, name, news_sources=None, channels=None, schedule_hours=24):
        """
        Create a complete content pipeline with news sources, channels, and scheduled workflow.
        
        Args:
            name (str): Name of the pipeline
            news_sources (list): News sources to add
            channels (list): Channels to create
            schedule_hours (int): Hours between scheduled runs
            
        Returns:
            dict: Created pipeline information
        """
        # Add news sources if provided
        if news_sources:
            for source in news_sources:
                self.news_automation.add_news_source(
                    name=source["name"],
                    url=source["url"],
                    source_type=source.get("type", "rss"),
                    categories=source.get("categories")
                )
        
        # Create channels if provided
        created_channels = []
        if channels:
            for channel in channels:
                created_channel = self.channel_manager.create_channel(
                    name=channel["name"],
                    theme=channel["theme"],
                    personality=channel["personality"],
                    target_audience=channel.get("target_audience"),
                    content_types=channel.get("content_types"),
                    posting_frequency=channel.get("posting_frequency")
                )
                created_channels.append(created_channel)
        
        # Create workflow
        workflow = self.create_workflow(
            name=f"{name} Pipeline",
            description=f"Complete content pipeline for {name}",
            steps=[
                {
                    "id": "step_1",
                    "name": "Crawl News",
                    "type": "news_crawl",
                    "params": {
                        "max_articles": 20,
                        "hours_back": 24
                    }
                },
                {
                    "id": "step_2",
                    "name": "Process Articles",
                    "type": "news_process",
                    "params": {
                        "platforms": ["blog", "social", "newsletter"]
                    }
                },
                {
                    "id": "step_3",
                    "name": "Generate Channel Content",
                    "type": "channel_generate",
                    "params": {
                        "content_type": "shorts"
                    }
                },
                {
                    "id": "step_4",
                    "name": "Publish All Content",
                    "type": "publish_all",
                    "params": {}
                }
            ]
        )
        
        # Schedule the workflow
        schedule = self.schedule_workflow(workflow["id"], schedule_hours)
        
        return {
            "name": name,
            "workflow": workflow,
            "schedule": schedule,
            "news_sources_count": len(news_sources) if news_sources else 0,
            "channels": created_channels
        }
    
    def get_recent_runs(self, limit=10):
        """
        Get recent workflow runs.
        
        Args:
            limit (int): Maximum number of runs to return
            
        Returns:
            list: Recent runs
        """
        # Sort runs by start time (newest first)
        sorted_runs = sorted(
            self.workflow_data["runs"],
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
        for run in self.workflow_data["runs"]:
            if run["id"] == run_id:
                return run
                
        return None
    
    def get_workflow_runs(self, workflow_id, limit=10):
        """
        Get runs for a specific workflow.
        
        Args:
            workflow_id (str): ID of the workflow
            limit (int): Maximum number of runs to return
            
        Returns:
            list: Runs for the workflow
        """
        # Filter runs by workflow ID and sort by start time (newest first)
        workflow_runs = [r for r in self.workflow_data["runs"] if r["workflow_id"] == workflow_id]
        sorted_runs = sorted(workflow_runs, key=lambda r: r["start_time"], reverse=True)
        
        return sorted_runs[:limit]
    
    def get_stats(self):
        """
        Get statistics about the integrated workflow system.
        
        Returns:
            dict: Statistics
        """
        # Get stats from each component
        news_stats = self.news_automation.get_stats()
        channel_stats = self.channel_manager.get_overall_stats()
        scheduler_stats = self.automation_scheduler.get_scheduler_status()
        
        # Calculate overall stats
        total_content_generated = news_stats["articles_processed"] + channel_stats["total_content"]
        total_content_published = news_stats.get("posts_created", 0) + channel_stats.get("content_by_status", {}).get("published", 0)
        
        return {
            "workflows": {
                "total": len(self.workflow_data["workflows"]),
                "enabled": len([w for w in self.workflow_data["workflows"] if w["enabled"]])
            },
            "runs": {
                "total": len(self.workflow_data["runs"]),
                "completed": len([r for r in self.workflow_data["runs"] if r["status"] == "completed"]),
                "failed": len([r for r in self.workflow_data["runs"] if r["status"] == "failed"])
            },
            "content": {
                "total_generated": total_content_generated,
                "total_published": total_content_published
            },
            "news": news_stats,
            "channels": channel_stats,
            "scheduler": scheduler_stats
        }
    
    def start_all_services(self):
        """
        Start all services (scheduler, etc.).
        
        Returns:
            dict: Service status
        """
        scheduler_started = self.automation_scheduler.start_scheduler()
        
        return {
            "scheduler_started": scheduler_started,
            "status": "running" if scheduler_started else "partial"
        }
    
    def stop_all_services(self):
        """
        Stop all services (scheduler, etc.).
        
        Returns:
            dict: Service status
        """
        scheduler_stopped = self.automation_scheduler.stop_scheduler()
        
        return {
            "scheduler_stopped": scheduler_stopped,
            "status": "stopped" if scheduler_stopped else "partial"
        }
