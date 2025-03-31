# Automation Manager Documentation

## Overview

The Automation Manager is a robust system for scheduling, executing, and monitoring automated tasks related to content creation, publishing, and monetization. It enables users to set up recurring workflows that operate with minimal manual intervention, maximizing efficiency and consistency.

## Architecture

The Automation Manager consists of two main components:

1. **AutomationManager Class** (`src/automation_manager.py`): The core class that handles task scheduling, execution, and monitoring.

2. **Task-specific Executors**: Specialized components that handle different types of automated tasks (content creation, publishing, monetization).

## AutomationManager Class

### Key Features

- Task scheduling with various recurrence patterns
- Task queue management
- Execution logging and monitoring
- Performance analytics
- Failure handling and recovery
- Configuration management

### Class Structure

```python
class AutomationManager:
    def __init__(self, google_credentials_path=None, dropbox_token=None):
        # Initialize with optional API credentials
        
    def _load_config(self):
        # Load automation configuration
        
    def _load_schedules(self):
        # Load automation schedules
        
    def _load_tasks(self):
        # Load automation tasks
        
    def save_config(self):
        # Save current configuration
        
    def add_task(self, task_type, task_data):
        # Add a new task
        
    def remove_task(self, task_type, task_index):
        # Remove a task
        
    def update_task(self, task_type, task_index, task_data):
        # Update an existing task
        
    def setup_schedules(self):
        # Set up scheduled tasks
        
    def execute_content_creation_task(self, task):
        # Execute a content creation task
        
    def execute_publishing_task(self, task):
        # Execute a publishing task
        
    def execute_monetization_task(self, task):
        # Execute a monetization task
        
    def log_task_result(self, task_category, task, result):
        # Log the result of a task execution
        
    def run_scheduler(self, run_once=False):
        # Run the scheduler
        
    def execute_task_now(self, task_type, task_data):
        # Execute a task immediately
        
    def get_task_history(self, days=7, category=None, success_only=False):
        # Get history of executed tasks
```

### Workflow

1. Initialize the AutomationManager
2. Configure tasks with specific schedules
3. Start the scheduler to run tasks automatically
4. Monitor task execution and results
5. Adjust tasks and schedules based on performance

### Example Usage

```python
from src.automation_manager import AutomationManager

# Initialize the manager
automation = AutomationManager()

# Add content creation task
automation.add_task("content_creation", {
    "type": "shorts",
    "topic": "productivity tips",
    "schedule": "daily",
    "enabled": True
})

# Add publishing task
automation.add_task("publishing", {
    "type": "social",
    "platform": "twitter",
    "schedule": "daily",
    "enabled": True
})

# Add monetization task
automation.add_task("monetization", {
    "type": "affiliate_content",
    "topic": "best productivity tools",
    "schedule": "weekly",
    "enabled": True
})

# Start the scheduler
automation.run_scheduler()
```

## Task Types

The Automation Manager supports three main categories of tasks:

### Content Creation Tasks

Tasks that generate various types of content:

- **Shorts**: Create short-form video content
- **Blog**: Generate blog posts
- **Ebook**: Create ebooks
- **Social**: Generate social media content

Example configuration:
```json
{
    "type": "shorts",
    "topic": "productivity tips",
    "method": "story",
    "schedule": "daily",
    "enabled": true
}
```

### Publishing Tasks

Tasks that publish content to various platforms:

- **Pending**: Process all pending content
- **Ebook**: Publish an ebook to platforms
- **Social**: Publish social media content

Example configuration:
```json
{
    "type": "ebook",
    "platform": "amazon_kdp",
    "ebook_id": "ebook_12345",
    "schedule": "weekly",
    "enabled": true
}
```

### Monetization Tasks

Tasks that implement and optimize monetization strategies:

- **Affiliate Content**: Generate affiliate marketing content
- **Ebook Promotion**: Create ebook promotion materials
- **Bundle Creation**: Create product bundles
- **Affiliate Program**: Set up affiliate programs
- **Sales Report**: Generate sales reports

Example configuration:
```json
{
    "type": "ebook_promotion",
    "ebook_id": "ebook_12345",
    "schedule": "weekly",
    "enabled": true
}
```

## Scheduling System

### Schedule Types

The system supports various schedule types:

- **Daily**: Execute every day at a specified time
- **Weekly**: Execute on specific days of the week
- **Biweekly**: Execute twice a week
- **Monthly**: Execute once a month
- **Custom**: Execute on a custom schedule

### Schedule Configuration

Schedules are configured in the `schedules.json` file:

```json
{
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
```

## Task Execution Process

### Execution Flow

1. **Task Selection**: The scheduler identifies tasks due for execution
2. **Parameter Preparation**: Task parameters are prepared
3. **Execution**: The appropriate executor is called
4. **Result Handling**: Results are processed and logged
5. **Status Update**: Task status is updated

### Execution Context

Each task execution includes:

- Task parameters
- Execution timestamp
- System state information
- Dependencies on other tasks
- Resource limitations

## Logging and Monitoring

### Log Structure

Task execution logs include:

- Timestamp
- Task category and type
- Input parameters
- Execution result
- Success/failure status
- Error messages (if applicable)
- Performance metrics

### Log Storage

Logs are stored in JSON format in the `.mp/automation/logs/` directory:

- Daily log files named by date (e.g., `2025-03-31.json`)
- Archived logs for historical analysis
- Summary statistics for reporting

### Monitoring Capabilities

The system provides monitoring through:

- Real-time execution status
- Success/failure rates
- Performance metrics
- Resource utilization
- Error patterns

## Maintenance Tasks

The Automation Manager includes several built-in maintenance tasks:

### Daily Maintenance

- Archive old logs
- Check for pending content
- Verify system health

### Weekly Maintenance

- Generate weekly sales reports
- Check for ebooks without affiliate programs
- Optimize resource allocation

### Monthly Maintenance

- Generate monthly sales reports
- Create bundles if enough ebooks are available
- Perform system optimization

## Integration with Other Components

The Automation Manager integrates with several other components in the MoneyPrinter system:

1. **Content Generation**: Automates the creation of various content types.

2. **Publishing Systems**: Automates the publishing process across platforms.

3. **Monetization Modules**: Schedules and executes monetization strategies.

4. **Analytics**: Collects and processes performance data.

## Technical Details

### Scheduler Implementation

The scheduler is implemented using the `schedule` library with:

- Time-based job scheduling
- Persistent job storage
- Failure recovery
- Priority-based execution

### Task Queue Management

The task queue is managed with:

- Priority-based ordering
- Dependency resolution
- Resource allocation
- Concurrency control

### Configuration Management

Configuration is stored in JSON files:

- `config.json`: General configuration
- `schedules.json`: Schedule definitions
- `tasks.json`: Task definitions

## Performance Considerations

- Scheduler check interval: 60 seconds
- Task execution timeout: Configurable per task type
- Maximum concurrent tasks: Configurable (default: 3)
- Log rotation: 30 days
- Memory usage: ~50-100MB depending on task load

## Best Practices

1. **Task Design**: Create focused tasks with clear objectives
2. **Scheduling**: Distribute tasks throughout the day to avoid resource contention
3. **Dependencies**: Clearly define task dependencies to ensure proper execution order
4. **Monitoring**: Regularly review task execution logs
5. **Optimization**: Adjust schedules based on performance data
6. **Testing**: Test new task configurations before enabling them

## Configuration Options

### General Configuration

```json
{
  "enabled": true,
  "max_daily_content": 5,
  "max_daily_ebooks": 2,
  "content_types": ["shorts", "blog", "ebook", "social"],
  "platforms": ["youtube", "twitter", "instagram"],
  "monetization_methods": ["affiliate", "digital_product", "ebook_sales"],
  "notification_email": "",
  "log_level": "info"
}
```

### Resource Limits

- `max_daily_content`: Maximum content items to create per day
- `max_daily_ebooks`: Maximum ebooks to create per day
- `max_concurrent_tasks`: Maximum tasks to run simultaneously
- `max_retries`: Maximum retry attempts for failed tasks

## Troubleshooting

### Common Issues

1. **Scheduling Issues**
   - Check system time synchronization
   - Verify task schedule configuration
   - Ensure the scheduler process is running

2. **Task Execution Failures**
   - Check dependency availability
   - Verify API credentials
   - Check resource availability
   - Review error logs for specific failure reasons

3. **Performance Problems**
   - Reduce concurrent task count
   - Distribute tasks more evenly
   - Check for resource-intensive tasks
   - Monitor system resource usage

### Error Recovery

The system implements several error recovery mechanisms:

- Automatic retry for transient failures
- Graceful degradation for partial failures
- State preservation for interrupted tasks
- Notification system for critical failures

## Future Enhancements

Planned enhancements for future versions:

1. Machine learning for optimal task scheduling
2. Enhanced dependency management
3. Distributed task execution
4. Advanced performance analytics
5. Custom task type creation interface
6. Integration with external workflow systems

---

*This documentation was last updated on March 31, 2025*
