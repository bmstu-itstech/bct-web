import json
from channels.generic.websocket import AsyncWebsocketConsumer

from tournament import models


class LeaderboardConsumer(AsyncWebsocketConsumer):

    game_id: int

    async def connect(self):
        self.game_id = int(self.scope['url_route']['kwargs']['game'])
        await self.channel_layer.group_add("results_updates", self.channel_name)
        await self.accept()
        await self.send_results()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("results_updates", self.channel_name)

    async def send_results(self):
        results = await models.fetch_team_results_async(self.game_id)
        await self.send(text_data=json.dumps(results))

    async def send_results_update(self, event):
        results = event["results"]
        game_id = event["game"]
        if self.game_id == game_id:
            await self.send(text_data=json.dumps(results))
