"""Task scheduler for periodic event discovery"""

import logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

logger = logging.getLogger(__name__)


class EventScheduler:
    """Schedules periodic event discovery"""
    
    def __init__(self, config, discovery_callback):
        self.config = config
        self.discovery_callback = discovery_callback
        self.scheduler = BackgroundScheduler()
    
    def start(self):
        """Start the scheduler"""
        schedule = self.config.get('scraping.schedule', 'daily')
        run_time = self.config.get('scraping.run_time', '08:00')
        
        hour, minute = run_time.split(':')
        
        if schedule == 'daily':
            trigger = CronTrigger(hour=hour, minute=minute)
        elif schedule == 'weekly':
            trigger = CronTrigger(day_of_week='mon', hour=hour, minute=minute)
        else:
            logger.warning(f"Unknown schedule: {schedule}, defaulting to daily")
            trigger = CronTrigger(hour=hour, minute=minute)
        
        self.scheduler.add_job(
            self.discovery_callback,
            trigger=trigger,
            id='event_discovery',
            name='Discover Coptic Service Events'
        )
        
        self.scheduler.start()
        logger.info(f"Scheduler started: {schedule} at {run_time}")
    
    def stop(self):
        """Stop the scheduler"""
        self.scheduler.shutdown()
        logger.info("Scheduler stopped")
