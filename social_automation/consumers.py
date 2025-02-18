from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async
import json
import logging

class AutomationConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        self.logger = logging.getLogger(__name__)
        self.task_id = self.scope['url_route']['kwargs']['task_id']
        self.room_group_name = f'automation_{self.task_id}'
        
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()
        
    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        
    async def receive_json(self, content):
        """Handle incoming messages"""
        try:
            message_type = content.get('type')
            if message_type == 'start_automation':
                await self.start_automation(content)
            elif message_type == 'pause_automation':
                await self.pause_automation()
            elif message_type == 'stop_automation':
                await self.stop_automation()
                
        except Exception as e:
            self.logger.error(f"WebSocket error: {str(e)}")
            await self.send_json({
                'type': 'error',
                'message': str(e)
            })
            
    async def automation_update(self, event):
        """Send automation updates to WebSocket"""
        await self.send_json(event) 