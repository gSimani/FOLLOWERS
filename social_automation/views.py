from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
import json
import uuid
from .automation import AutomationController
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

@csrf_exempt
@require_http_methods(["POST"])
def start_automation(request):
    try:
        data = json.loads(request.body)
        platform = data.get('platform')
        action = data.get('action')
        target_url = data.get('target_url')
        quantity = int(data.get('quantity', 100))
        
        # Generate task ID
        task_id = str(uuid.uuid4())
        
        # Start automation in background
        controller = AutomationController()
        async_to_sync(controller.execute_automation)(
            platform=platform,
            action=action,
            target_url=target_url,
            quantity=quantity,
            task_id=task_id
        )
        
        return JsonResponse({
            'status': 'success',
            'task_id': task_id,
            'message': 'Automation started'
        })
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=400)

@require_http_methods(["GET"])
def get_progress(request, task_id):
    try:
        # Get progress from Redis or database
        channel_layer = get_channel_layer()
        progress = async_to_sync(channel_layer.group_send)(
            f'automation_{task_id}',
            {
                'type': 'automation_update',
                'message': 'Getting progress'
            }
        )
        
        return JsonResponse({
            'status': 'success',
            'progress': progress
        })
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=400)

@require_http_methods(["GET"])
def get_logs(request):
    try:
        # Get logs from database
        logs = []  # Replace with actual log retrieval
        
        return JsonResponse({
            'status': 'success',
            'logs': logs
        })
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=400) 