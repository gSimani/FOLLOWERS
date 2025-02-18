import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from ..automation import AutomationController
import asyncio

@pytest.mark.asyncio
class TestAutomation:
    @pytest.fixture
    async def controller(self):
        controller = AutomationController()
        yield controller
        await controller.cleanup()
        
    @pytest.fixture
    def mock_websocket(self):
        class MockWebSocket:
            async def send_json(self, data):
                self.last_message = data
        return MockWebSocket()
        
    async def test_instagram_follow(self, controller, mock_websocket):
        """Test Instagram follow automation"""
        result = await controller.execute_automation(
            platform='instagram',
            action='follow',
            target_url='https://instagram.com/test_account',
            quantity=5,
            websocket=mock_websocket
        )
        
        assert result is True
        assert mock_websocket.last_message['progress'] == 100
        
    async def test_error_handling(self, controller, mock_websocket):
        """Test error handling during automation"""
        with pytest.raises(Exception):
            await controller.execute_automation(
                platform='instagram',
                action='follow',
                target_url='invalid_url',
                quantity=5,
                websocket=mock_websocket
            ) 