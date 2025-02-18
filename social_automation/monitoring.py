from django.conf import settings
import logging
import sentry_sdk
from prometheus_client import Counter, Histogram
import json

# Metrics
AUTOMATION_DURATION = Histogram(
    'automation_task_duration_seconds',
    'Time spent executing automation tasks',
    ['platform', 'action']
)

AUTOMATION_SUCCESS = Counter(
    'automation_success_total',
    'Number of successful automation operations',
    ['platform', 'action']
)

AUTOMATION_FAILURE = Counter(
    'automation_failure_total',
    'Number of failed automation operations',
    ['platform', 'action', 'error_type']
)

class AutomationMonitor:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    def log_error(self, error, context=None):
        """Log error with context"""
        error_data = {
            'error': str(error),
            'error_type': type(error).__name__,
            'context': context or {}
        }
        
        self.logger.error(
            f"Automation error: {json.dumps(error_data, indent=2)}"
        )
        
        if hasattr(settings, 'SENTRY_DSN'):
            sentry_sdk.capture_exception(error)
            
    def track_metrics(self, platform, action, duration, success, error_type=None):
        """Record metrics for monitoring"""
        AUTOMATION_DURATION.labels(
            platform=platform,
            action=action
        ).observe(duration)
        
        if success:
            AUTOMATION_SUCCESS.labels(
                platform=platform,
                action=action
            ).inc()
        else:
            AUTOMATION_FAILURE.labels(
                platform=platform,
                action=action,
                error_type=error_type or 'unknown'
            ).inc() 