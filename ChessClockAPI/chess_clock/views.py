import json

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.db.models import Max
from django.http import HttpResponseNotFound
from django.shortcuts import render
# Create your views here.
from grpc._channel import Channel
from rest_framework.response import Response
from rest_framework.views import APIView

from chess_clock import models
from .models import Users, Games, Players, Turns, color_set
from .serializers import UsersSerializer_game, \
    GamesSerializer_game

channel_layer = get_channel_layer()

# Мы должны, если неободимо создать нового игрока и его url, создать новую игру.
# Мы должны вернуть короткий url для данного игрока и id игры.


"""
------------------------------------------------------------------------------------------------------------------------
                                                       Метод /game                                                      
------------------------------------------------------------------------------------------------------------------------
Этот метод REST интерфейса должен принимать POST запрос на создание новой игры. 
В запросе приложение передает объект со следующими данными

Пример:
request:
{  
   "user":{  
      "user_id": "token-898"
   },
   "players":{  
      "colors":[  
         "#CD5C5C",
         "#FFC0CB"
      ]
   }
}
------------------------------------------------------------------------------------------------------------------------
В ответе API должен вернуть

Пример:
response:
{
    "status": "game",
    "user": {
        "short_url": "short_url"
    },
    "game": {
        "id": 10
    }
}
------------------------------------------------------------------------------------------------------------------------
Сообщения об ошибках:
"error, must be one to six items in colors":
"error, no block colors in players"
"error, no block players"
"error, no block user_id in users"
"error, no block users"
"error, ValueError"

------------------------------------------------------------------------------------------------------------------------
Веб-сайт при этом должен создать страницу игры, на которой отображаются все игроки с их цветами. 
В качестве времени у каждого значится 00:00, общее время также 00:00
------------------------------------------------------------------------------------------------------------------------
"""
class Game(APIView):
    def post(self, request, format=None):

        # преобразуем request в json, если получаем ошибку, то вернем сообщение об этом.
        try:
            json_data = json.loads(request.body)
        except ValueError:  # includes simplejson.decoder.JSONDecodeError
            return Response({"status": "error, ValueError"})

        # Мы должны убедиться в наличие всех необходимых ключей и значений в json, если чего-то не хватает:
        # вернем ошибку и сообщим в чем проблема.

        if "user" in json_data:
            if "user_id" in json_data["user"]:
                # В json есть необходимые нам ключи и значения, чтобы проверить новый это пользователь или нет:
                some_user = Users.objects.filter(user_id = json_data["user"]["user_id"])
                if not some_user.exists():
                    # это новый пользователь, надо создать его.
                    user = Users().new_user_JSON_get_short_url(json_data["user"])
                else:
                    # этот пользователь уже есть в базе, найдем его.
                    user = Users.objects.get(user_id = json_data["user"]["user_id"])
                if "players" in json_data:
                    if "colors" in json_data["players"]:
                        if 1 <= len(json_data["players"]["colors"]) <= 6:
                            # В json есть необходимые нам ключи и значения, чтобы создать новую игру:
                            colors = json_data["players"]["colors"]
                            for color in colors:
                                color.lower()
                                if not color in color_set:
                                    return Response({"status": "error, color {0} is not valid".format(color)})
                            game = Games().new_game_JSON_get_id(json_data["user"], colors[0])
                            # создадим игроков для данной игры.
                            for i in range(len(colors)):
                                Players().new_player_JSON_without_get(game, colors[i])
                        else:
                            return Response({"status": "error, must be one to six items in colors"})
                    else:
                        return Response({"status": "error, no block colors in players"})
                else:
                    return Response({"status": "error, no block players"})
            else:
                return Response({"status": "error, no block user_id in users"})
        else:
            return Response({"status": "error, no block users"})
        user_serializer = UsersSerializer_game(user)
        game_serializer = GamesSerializer_game(game)
        print("user-{}".format(Users.objects.get(user_id = json_data["user"]["user_id"]).get_id()))
        async_to_sync(channel_layer.group_send)(
            "user-{}".format(Users.objects.get(user_id = json_data["user"]["user_id"]).get_id()),
            {
                'type': 'set_new_game'
            }
        )
        return Response({
            "status": "game",
            "user": user_serializer.data,
            "game": game_serializer.data
            })

"""
------------------------------------------------------------------------------------------------------------------------
                                                       Метод /gameId/play                                                      
------------------------------------------------------------------------------------------------------------------------
Принимает POST запрос, в котором приложение сообщает о начале/продолжении хода очередного игрока. 
В теле запроса приложение передает объект со следующими данными

HEX строка цвета игрока, чей ход начинается/продолжается

Принимает:

{  
   "game":{  
      "active": "#CD5C5C"
   }
}
------------------------------------------------------------------------------------------------------------------------

Возвращает:

{
    "status": "play, game resume"
}

или

{
    "status": "play, next player"
}
------------------------------------------------------------------------------------------------------------------------
Сообщения об ошибках:
"error, gameID does not exist"
"error, this color does not exist"
"error, someone's going now"
"error, ValueError"
------------------------------------------------------------------------------------------------------------------------
Веб-страница должна активировать (выделить) указанного игрока (деактивировав всех остальных) и 
начать/продолжить отсчет его времени.
------------------------------------------------------------------------------------------------------------------------
"""

class Play(APIView):
    def post(self, request, gameId, format=None):

        # преобразуем request в json, если получаем ошибку, то вернем сообщение об этом.
        try:
            json_data = json.loads(request.body)
        except ValueError:  # includes simplejson.decoder.JSONDecodeError
            return Response({"status": "ValueError"})

            # Мы должны убедиться в наличие всех необходимых ключей и значений в json, если чего-то не хватает:
            # вернем ошибку и сообщим в чем проблема.

        if "game" in json_data:
            if "active" in json_data["game"]:
                game = Games.objects.filter(id = gameId)
                if not game.exists():
                    # Так же убедимся, что получен верный gameID, и такая игра существует.
                    return Response({"status": "error, gameID does not exist"})
                else:
                    game = Games.objects.get(id = gameId)
                    # При получении этого метода, игра всегда должна быть на паузе, в ожидании либо продолжения хода,
                    # либо начала хода следующего игрока но все, же проверим это:
                    if game.get_pause():
                        # Снимаем с паузы:
                        game.set_pause(False)
                        # Получим цвет игрока, который начинает/возобновляет ход.
                        active = json_data["game"]["active"].lower()
                        # Убедимся, что полученный цвет, есть в данной игре.
                        players = Players.objects.filter(game_id = gameId, color=active)
                        if players.exists():
                            # проверяем будет ли игрок продолжать свой ход, или начинается ход нового игрока.
                            if game.get_turn_run() is None:
                                game.set_turn_run(True)
                            if game.get_turn_run():
                                async_to_sync(channel_layer.group_send)(
                                    "user-{}".format(game.get_user()),
                                    {
                                        'type': 'set_pause_off'
                                    }
                                )
                                return Response({"status": "play, game resume"})
                            else:
                                # устанавливаем нового активного игрока
                                game.set_active(active)
                                game.set_turn_run(True)
                                print(game.get_active())
                                async_to_sync(channel_layer.group_send)(
                                    "user-{}".format(game.get_user()),
                                    {
                                        'type': 'update_status',
                                        'turn_time': '00:00'
                                    }
                                )

                                return Response({"status": "play, next player"})
                        else:
                            return Response({"status": "error, this color does not exist"})
                    # Если игра не на паузе:
                    else:
                        return Response({"status": "error, someone's going now"})

"""
------------------------------------------------------------------------------------------------------------------------
                                                       Метод /gameId/pause                                                      
------------------------------------------------------------------------------------------------------------------------
Принимает POST запрос, в котором приложение сообщает о приостановке хода текущего игрока. 
В теле запроса передаются такие же данные, как и в методе play.

Принимает:

{  
   "game":{  
      "active": "#CD5C5C"
   }
}
------------------------------------------------------------------------------------------------------------------------

Возвращает:

{
    "status": "pause"
}

------------------------------------------------------------------------------------------------------------------------
Сообщения об ошибках:
"error, gameID does not exist"
"error, pause already active"
"error, ValueError"


------------------------------------------------------------------------------------------------------------------------
Веб-страница должна остановить отсчет времени текущего игрока. 
При получении затем метода play - веб-страница должна продолжить отсчет времени.
------------------------------------------------------------------------------------------------------------------------
"""

class Pause(APIView):
    def post(self, request, gameId, format=None):

        # преобразуем request в json, если получаем ошибку, то вернем сообщение об этом.
        try:
            json_data = json.loads(request.body)
        except ValueError:  # includes simplejson.decoder.JSONDecodeError
            return Response({"status": "ValueError"})

            # Мы должны убедиться в наличие всех необходимых ключей и значений в json, если чего-то не хватает:
            # вернем ошибку и сообщим в чем проблема.

        if "game" in json_data:
            if "active" in json_data["game"]:
                game = Games.objects.filter(id = gameId)
                if not game.exists():
                    # Так же убедимся, что получен верный gameID, и такая игра существует.
                    return Response({"status": "error, gameID does not exist"})
                else:
                    game = Games.objects.get(id = gameId)
                    # При получении этого метода, игра всегда должна быть не на паузе, но все, же проверим это:
                    if not game.get_pause():
                        # Ставим паузу:
                        game.set_pause(True)
                        async_to_sync(channel_layer.group_send)(
                            "user-{}".format(game.get_user()),
                            {
                                'type': 'set_pause_on',
                                'turn_time': '00:00'
                            }
                        )
                        return Response({"status": "pause"})
                    # Если игра на паузе:
                    else:
                        return Response({"status": "error, pause already active"})

"""
------------------------------------------------------------------------------------------------------------------------
                                                       Метод /gameId/done                                                      
------------------------------------------------------------------------------------------------------------------------
Принимает POST запрос, в котором приложение сообщает о завершении хода текущего игрока. 
В теле запроса приложение передает объект со следующими данными

HEX строка цвета игрока, чей ход закончился
Его время хода (строка в формате ##:##)
Его общее время в игре (строка в формате ##:##)
Общее время всей игры (строка в формате ##:##)


Принимает:

{  
   "game":{  
      "total_game_time": "##:##"
   },
   "player"{
      "color": "#CD5C5C",
      "total_player_time": "##:##"      
   },
   "turn"{
      "turn_time": "##:##"
   }
}
------------------------------------------------------------------------------------------------------------------------

Возвращает:

{
    "status": "done"
}

------------------------------------------------------------------------------------------------------------------------
Сообщения об ошибках:
"error, gameID does not exist"
"error, this color does not exist"
"error, this player is not active now"
"error, no block turn_time in turn"
"error, no block total_player_time in player"
"error, no block color in player"
"error, no block total_game_time in game"
"error, no block turn"
"error, no block player"
"error, no block game"
"error, ValueError"
------------------------------------------------------------------------------------------------------------------------
Веб-страница должна остановить отсчет времени указанного игрока и отобразить около его пиктограммы его общее время в игре. 
Также нужно обновить общее время игры.
------------------------------------------------------------------------------------------------------------------------
"""

class Done(APIView):
    def post(self, request, gameId, format=None):

        # преобразуем request в json, если получаем ошибку, то вернем сообщение об этом.
        try:
            json_data = json.loads(request.body)
        except ValueError:  # includes simplejson.decoder.JSONDecodeError
            return Response({"status": "ValueError"})

        # Мы должны убедиться в наличие всех необходимых ключей и значений в json, если чего-то не хватает:
        # вернем ошибку и сообщим в чем проблема.

        if "game" in json_data:
            if "player" in json_data:
                if "turn" in json_data:
                    if "total_game_time" in json_data["game"]:
                        if "color" in json_data["player"]:
                            if "total_player_time" in json_data["player"]:
                                if "turn_time" in json_data["turn"]:
                                    game = Games.objects.filter(id = gameId)
                                    if not game.exists():
                                        # Так же убедимся, что получен верный gameID, и такая игра существует.
                                        return Response({"status": "error, gameID does not exist"})
                                    else:
                                        game = Games.objects.get(id = gameId)
                                        active = json_data["player"]["color"].lower()
                                        # Убедимся, что полученный цвет, есть в данной игре.
                                        players = Players.objects.filter(game_id = gameId, color = active)
                                        if not players.exists():
                                            return Response({"status": "error, this color does not exist"})
                                        else:
                                            # Убедимся, что получен верный активный игрок.
                                            if not game.get_active() == active:
                                                return Response({"status": "error, this player is not active now"})
                                            else:
                                                # поставим игру на паузу, так как этот игрок закончил ход.
                                                game.set_pause(True)
                                                game.set_turn_run(False)
                                                total_game_time = json_data["game"]["total_game_time"]
                                                game.set_total_time(total_game_time)
                                                player = Players.objects.get(game_id = gameId, color = active)
                                                total_player_time = json_data["player"]["total_player_time"]
                                                player.set_total_player_time(total_player_time)
                                                turn_time = Turns().new_turn_JSON_get_turn_time(gameId, json_data["player"], json_data["turn"])
                                                async_to_sync(channel_layer.group_send)(
                                                    "user-{}".format(game.get_user()),
                                                    {
                                                        'type': 'update_status',
                                                        'turn_time': json_data["turn"]["turn_time"]
                                                    }
                                                )
                                else:
                                    return Response({"status": "error, no block turn_time in turn"})
                            else:
                                return Response({"status": "error, no block total_player_time in player"})
                        else:
                            return Response({"status": "error, no block color in player"})
                    else:
                        return Response({"status": "error, no block total_game_time in game"})
                else:
                    return Response({"status": "error, no block turn"})
            else:
                return Response({"status": "error, no block player"})
        else:
            return Response({"status": "error, no block game"})
        return Response({"status": "done"})

"""
------------------------------------------------------------------------------------------------------------------------
                                                       Метод /gameId/game_over                                                      
------------------------------------------------------------------------------------------------------------------------
Принимает POST запрос, в котором приложение сообщает о завершении хода игры


Принимает:

{  
}
------------------------------------------------------------------------------------------------------------------------

Возвращает:

{
    "status": "game_over"
}

------------------------------------------------------------------------------------------------------------------------
Сообщения об ошибках:
"error, gameID does not exist"
------------------------------------------------------------------------------------------------------------------------
Веб-страница должна остановить отсчет времени указанного игрока и отобразить около его пиктограммы его общее время в игре. 
Также нужно обновить общее время игры.
------------------------------------------------------------------------------------------------------------------------
"""

class GameOver(APIView):
    def post(self, request, gameId, format=None):
        game = Games.objects.filter(id = gameId)
        if not game.exists():
            # Так же убедимся, что получен верный gameID, и такая игра существует.
            return Response({"status": "error, gameID does not exist"})
        else:
            game = Games.objects.get(id = gameId)
            async_to_sync(channel_layer.group_send)(
                "user-{}".format(game.get_user()),
                {
                    'type': 'set_game_over',
                }
            )
            return Response({"status": "game_over"})


class Url(APIView):
    def get(self, request, short_url):
        user = Users.objects.filter(short_url = short_url)
        if not user.exists():

            return Response({"no correct url"})
        else:
            user = Users.objects.get(short_url = short_url)
            full_url = user.get_full_url()
            return Response({full_url})

class Clock(APIView):
    def get(self, request, full_url):
        full_url = models.base_url + 'user/' + full_url
        try:
            print(full_url)
            user = Users.objects.get(full_url = full_url)
        except Users.DoesNotExist:
            return HttpResponseNotFound('<h1>No Page Here</h1>')
        games = Games.objects.filter(user_id = user.get_id())
        game_id = games.aggregate(Max('id'))['id__max']
        players = str(Players.objects.filter(game_id = game_id).count())

        colors = list(Players.objects.filter(game_id = game_id).values_list('color', flat = True))

        text_colors = []
        colorA = []
        colorB = []
        for color in colors:
            text_colors.append(color_set[color]["Number"])
            colorA.append(color_set[color]["colorA"])
            colorB.append(color_set[color]["colorB"])


        print(text_colors)
        return render(request, 'Clock.html', context = {
            'colorA': colorA,
            'colorB': colorB,
            'text_colors': text_colors,
            'players': players
        })

class Main(APIView):
    def get(self, request):
        return render(request, 'Main.html')

