import json
from channels.generic.websocket import AsyncWebsocketConsumer

class GameConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
    
    async def disconnect(self, close_code):
        pass
    
    async def receive(self, text_data):
        game_data = json.loads(game_data)
        
        # Now the game logic should be here!
        # You should still save things to the database to allow
        # persistance. You can modify game_data (a dictionary) and then
        # save it to the db.
        # PS: Add game logic here means delete it from your views.py :D
        # Once the logic is done, send the updated game to the listeners

        await self.send(text_data=json.dumps(game_data))