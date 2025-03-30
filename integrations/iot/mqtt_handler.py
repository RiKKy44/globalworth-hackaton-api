import logging
from asyncio_mqtt import Client, MqttError
from core.config import settings
from typing import Optional, Callable

class MQTTClient:
    def __init__(self):
        self.client: Optional[Client] = None
        self.logger = logging.getLogger(__name__)
        self._connect_options = {
            "hostname": settings.MQTT_HOST,
            "port": settings.MQTT_PORT,
            "username": settings.MQTT_USER,
            "password": settings.MQTT_PASSWORD,
            "keepalive": 60
        }

    async def connect(self):
        """Connect to MQTT broker"""
        try:
            self.client = Client(**self._connect_options)
            await self.client.connect()
            self.logger.info("Connected to MQTT broker")
        except MqttError as e:
            self.logger.error(f"MQTT connection error: {str(e)}")
            raise

    async def publish_esg_data(self, building_id: str, data: dict):
        """Publish ESG data to MQTT topic"""
        topic = f"esg/{building_id}/data"
        try:
            await self.client.publish(topic, str(data).encode(), qos=1)
            self.logger.debug(f"Published to {topic}: {data}")
        except MqttError as e:
            self.logger.error(f"MQTT publish failed: {str(e)}")

    async def subscribe_to_commands(self, callback: Callable):
        """Subscribe to command topics"""
        try:
            async with self.client.filtered_messages("esg/+/command") as messages:
                await self.client.subscribe("esg/#")
                async for message in messages:
                    callback(message.topic, message.payload.decode())
        except MqttError as e:
            self.logger.error(f"MQTT subscription error: {str(e)}")

    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        if self.client:
            await self.client.disconnect()