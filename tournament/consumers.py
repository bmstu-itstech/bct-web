import json
from channels.generic.websocket import AsyncWebsocketConsumer

from tournament import models


class LeaderboardConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add("results_updates", self.channel_name)
        await self.accept()
        await self.send_results()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("results_updates", self.channel_name)

    async def send_results(self):
        results = await models.fetch_team_results_async()
        await self.send(text_data=json.dumps(results))

    async def send_results_update(self, event):
        results = event["results"]
        await self.send(text_data=json.dumps(results))
