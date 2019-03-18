import asyncio
import json
from asgiref.sync import async_to_sync
from channels.consumer import AsyncConsumer
from channels.db import database_sync_to_async
from channels.exceptions import StopConsumer
from django.db.models import Max

from chess_clock import models
from chess_clock.models import Users, Games, Players

class Consumer(AsyncConsumer):

    async def websocket_connect(self, event):
        print('connection successfull', event)

        await self.send({'type': 'websocket.accept',})

        # Получаем short_url и определяем по нему игрока и активную игру.
        full_url = models.base_url + 'user/' + self.scope['url_route']['kwargs']['full_url']
        try:
            user = Users.objects.get(full_url = full_url)
        except Users.DoesNotExist:
            await self.send({'type': 'websocket.accept', 'error': 'bad url'})
        self.user_id = user.get_id()
        games = Games.objects.filter(user_id = self.user_id)
        game_id = games.aggregate(Max('id'))['id__max']
        self.game_id = game_id
        game = Games.objects.get(id = self.game_id)
        await self.channel_layer.group_add("user-{}".format(self.user_id), self.channel_name)

        # Определяем общее время игры и паузу
        total_time = game.get_total_time()
        pause = game.get_pause()
        turn_run = game.get_turn_run()

        # Определяем список игроков и время их ходов
        colors = list(Players.objects.filter(game_id = self.game_id).values_list('color', flat=True))
        players_time = list(Players.objects.filter(game_id = self.game_id).values_list('total_player_time', flat = True))

        # Определяем активного игрока. (номер и цвет)
        active_color = game.get_active()
        active_player = colors.index(active_color)+1

        turn_time = '00:00'
        color_player_timer=[]
        color_numbers=[]
        color_time_turn=[]
        color_time_turn_outline=[]
        color_restangles=[]

        for color in colors:
            color_numbers.append(models.color_set[color]["Number"])
            color_time_turn.append(models.color_set[color]["Time turn"])
            color_time_turn_outline.append(models.color_set[color]["Time turn outline"])
            color_restangles.append(models.color_set[color]["Restangls"])
            color_player_timer.append(models.color_set[color]["colorA"])

        data = {
            "task": "create web",
            "game": {
                "id": game_id,
                "active player": active_player,
                "total time": total_time,
                "pause": pause,
                "turn_run": turn_run
            },
            "players": {
                "colors": colors,
                "players time": players_time
            },
            "turn": {
                "turn time": turn_time
            },
            "set_colors": {

                "color_numbers": color_numbers,
                "color_time_turn": color_time_turn,
                "color_time_turn_outline": color_time_turn_outline,
                "color_restangles": color_restangles,
                "color_player_timer": color_player_timer
            }
        }
        await self.send({
            'type': 'websocket.send',
            'text': json.dumps(data),
        })

    async def set_pause_on(self, event):
        print("websocket_message: pause_on")
        data = {
            "task": "pause_on",
        }
        await self.send({
            'type': 'websocket.send',
            'text': json.dumps(data),
        })

    async def set_pause_off(self, event):
        print("websocket_message: pause_off")
        data = {
            "task": "pause_off",
        }
        await self.send({
            'type': 'websocket.send',
            'text': json.dumps(data),
        })

    async def update_status(self, event):
        print("websocket_message: update_status" + str(event))
        turn_time = event["turn_time"]
        # Определяем общее время игры и паузу
        game = Games.objects.get(id = self.game_id)
        total_time = game.get_total_time()
        pause = game.get_pause()


        # Определяем список игроков и время их ходов
        colors = list(Players.objects.filter(game_id = self.game_id).values_list('color', flat = True))
        players_time = list(Players.objects.filter(game_id = self.game_id).values_list('total_player_time', flat = True))

        # Определяем активного игрока. (номер и цвет)
        active_color = game.get_active()
        active_player = colors.index(active_color) + 1
        print(game.get_active())

        data = {
            "task": "update_status",
            "game": {
                "active player": active_player,
                "total time": total_time,
                "pause": pause
            },
            "players": {
                "colors": colors,
                "players time": players_time
            },
            "turn": {
                "turn time": turn_time
            }
        }
        await self.send({
            'type': 'websocket.send',
            'text': json.dumps(data),
        })

    async def set_new_game(self, event):
        print("websocket_message: new_game")
        data = {
            "task": "new_game",
        }
        await self.send({
            'type': 'websocket.send',
            'text': json.dumps(data),
        })

    async def set_game_over(self, event):
        print("websocket_message: game_over")
        data = {
            "task": "game_over",
        }
        await self.send({
            'type': 'websocket.send',
            'text': json.dumps(data),
        })


    async def websocket_message(self, event):
        print('websocket_message', event)
        await self.send({
            'type': 'websocket.send',
            'text': json.dumps({
                'active player': 5
            }),
        })

    async def websocket_disconnect(self, event):
        self.channel_layer.group_discard("user-{}".format(self.user_id), self.channel_name)
        raise StopConsumer()
