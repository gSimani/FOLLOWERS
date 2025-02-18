from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from .models import AutomationTask, TargetURL, TaskProgress
from .scrapers.factory import ScraperFactory
from .google_calendar import GoogleCalendarAPI
import logging
import time
import random

logger = logging.getLogger(__name__)

@shared_task
def schedule_automation_task(task_id):
    """Schedule an automation task with Google Calendar"""
    try:
        task = AutomationTask.objects.get(id=task_id)
        calendar_api = GoogleCalendarAPI()
        
        # Calculate start time (5 minutes from now)
        start_time = timezone.now() + timedelta(minutes=5)
        
        task_data = {
            'platform': task.platform,
            'action': task.action,
            'target_url': task.target_url.url,
            'quantity': task.quantity,
            'task_id': task.id,
            'start_time': start_time
        }
        
        event_id = calendar_api.schedule_automation(task_data)
        if event_id:
            task.calendar_event_id = event_id
            task.status = 'scheduled'
            task.save()
            logger.info(f"Task {task_id} scheduled successfully with event ID {event_id}")
            return True
        else:
            task.status = 'failed'
            task.error_message = "Failed to schedule task in Google Calendar"
            task.save()
            logger.error(f"Failed to schedule task {task_id} in Google Calendar")
            return False
            
    except Exception as e:
        logger.exception(f"Error scheduling task {task_id}: {str(e)}")
        return False

@shared_task
def execute_automation_task(task_id):
    """Execute a scheduled automation task"""
    try:
        task = AutomationTask.objects.get(id=task_id)
        task.status = 'running'
        task.started_at = timezone.now()
        task.save()
        
        scraper = ScraperFactory.get_scraper(
            task.platform,
            username=task.user.socialprofile_set.get(platform=task.platform).username,
            password=task.user.socialprofile_set.get(platform=task.platform).access_token
        )
        
        target_username = task.target_url.url.split('/')[-1]
        success = False
        
        try:
            # Get target users based on task configuration
            if task.target_type == 'followers':
                target_users = scraper.get_followers(target_username, task.quantity)
            else:  # following
                target_users = scraper.get_following(target_username, task.quantity)
            
            # Process each target user
            for user in target_users:
                try:
                    if task.action == 'follow':
                        success = scraper.follow_user(user)
                    else:  # unfollow
                        success = scraper.unfollow_user(user)
                    
                    # Log progress
                    TaskProgress.objects.create(
                        task=task,
                        action=task.action,
                        target_username=user,
                        status='success' if success else 'failed',
                        error_message=None if success else 'Action failed'
                    )
                    
                    # Update task progress
                    task.update_progress(
                        processed=1,
                        succeeded=1 if success else 0,
                        failed=0 if success else 1
                    )
                    
                except Exception as e:
                    error_msg = str(e)
                    logger.error(f"Error processing user {user}: {error_msg}")
                    
                    # Log error in progress
                    TaskProgress.objects.create(
                        task=task,
                        action=task.action,
                        target_username=user,
                        status='failed',
                        error_message=error_msg
                    )
                    
                    # Update task progress
                    task.update_progress(processed=1, failed=1)
                
                # Add random delay between actions
                time.sleep(random.uniform(2, 5))
        
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Error getting target users: {error_msg}")
            task.error_message = f"Failed to get target users: {error_msg}"
            task.status = 'failed'
            task.save()
            return False
        
        # Complete the task
        task.status = 'completed'
        task.completed_at = timezone.now()
        task.save()
        
        logger.info(f"Task {task_id} completed successfully. "
                   f"Processed: {task.total_processed}, "
                   f"Succeeded: {task.total_succeeded}, "
                   f"Failed: {task.total_failed}")
        return True
        
    except Exception as e:
        error_msg = str(e)
        logger.exception(f"Error executing task {task_id}: {error_msg}")
        task.status = 'failed'
        task.error_message = error_msg
        task.completed_at = timezone.now()
        task.save()
        return False
    finally:
        ScraperFactory.close_all()

@shared_task
def cleanup_completed_tasks():
    """Clean up old completed tasks"""
    try:
        # Delete completed tasks older than 30 days
        cutoff_date = timezone.now() - timedelta(days=30)
        AutomationTask.objects.filter(
            status='completed',
            created_at__lt=cutoff_date
        ).delete()
        logger.info("Cleaned up old completed tasks")
    except Exception as e:
        logger.exception(f"Error cleaning up tasks: {str(e)}")

@shared_task
def retry_failed_tasks():
    """Retry failed tasks"""
    try:
        # Retry tasks that failed in the last 24 hours
        cutoff_date = timezone.now() - timedelta(days=1)
        failed_tasks = AutomationTask.objects.filter(
            status='failed',
            created_at__gt=cutoff_date
        )
        
        for task in failed_tasks:
            logger.info(f"Retrying failed task {task.id}")
            schedule_automation_task.delay(task.id)
            
    except Exception as e:
        logger.exception(f"Error retrying failed tasks: {str(e)}") 