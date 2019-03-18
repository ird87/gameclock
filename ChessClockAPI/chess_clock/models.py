import random
import string

from django.db import models
from colorfield.fields import ColorField

from chess_clock.shorting import get_short_url

# base_url = "http://multiplayer-clock.herokuapp.com/"
base_url = "http://127.0.0.1:8000/"

#  -----------------------------------------------------------------------------------------------------------------------------
#  |Player color  |	 Color	      |  GradientA	|  GradientB  |	  Number   |  Time turn	  |  Time turn outline  |  Restangls  |
#  -----------------------------------------------------------------------------------------------------------------------------
#  |   Black	  |   #000000	  |   #3c3c3c	|   #262625	  |   #fefeff  |   #3c3c3c	  |        #c8beb6	    |   #1d1f23   |
#  |   Brown	  |   #a52a2a	  |   #8b4c2a	|   #512c18	  |   #fefeff  |   #6b3a20	  |        #c8beb6	    |   #6b3a20   |
#  |   Orange	  |   #ff8000	  |   #ffcc00	|   #ff8c00	  |   #fefeff  |   #f99900	  |        #c8beb6	    |   #f99900   |
#  |   White	  |   #ffffff	  |   #ffffff	|   #e2e2e1	  |   #1d1f23  |   #a6a6a6	  |        #999999	    |   #bbbbbb   |
#  |   Yellow	  |   #ffff00	  |   #ffeb00	|   #ffa500	  |   #1d1f23  |   #ffe000	  |        #c8beb6	    |   #ffd000   |
#  |   Green	  |   #008000	  |   #83d501	|   #4c9900	  |   #ffffff  |   #5bad00	  |          none	    |   #59a801   |
#  |   Violet	  |   #ee82ee	  |   #cd00f0	|   #b400e8	  |   #ffffff  |   #bd00e0	  |          none	    |   #a100bf   |
#  |   Blue	      |   #0000ff	  |   #03c9ff	|   #028aff	  |   #ffffff  |   #0397ff	  |          none	    |   #038bff   |
#  |   Red	      |   #ff0000	  |   #fd0000	|   #d10000	  |   #ffffff  |   #f20000	  |          none	    |   #bc0000   |
#  -----------------------------------------------------------------------------------------------------------------------------

color_set =\
    {
        "#000000":
            {
                "Player color": "Black",
                "colorA": "#3c3c3c",
                "colorB": "#262625",
                "Number": "#fefeff",
                "Time turn": "#3c3c3c",
                "Time turn outline": "#c8beb6",
                "Restangls": "#1d1f23"
            },
        "#a52a2a":
            {
                "Player color": "Brown",
                "colorA": "#8b4c2a",
                "colorB": "#512c18",
                "Number": "#fefeff",
                "Time turn": "#6b3a20",
                "Time turn outline": "#c8beb6",
                "Restangls": "#6b3a20"
            },
        "#ff8000":
            {
                "Player color": "Orange",
                "colorA": "#ffcc00",
                "colorB": "#ff8c00",
                "Number": "#fefeff",
                "Time turn": "#f99900",
                "Time turn outline": "#c8beb6",
                "Restangls": "#f99900"
            },
        "#ffffff":
            {
                "Player color": "White",
                "colorA": "#ffffff",
                "colorB": "#e2e2e1",
                "Number": "#1d1f23",
                "Time turn": "#a6a6a6",
                "Time turn outline": "#999999",
                "Restangls": "#bbbbbb"
            },
        "#ffff00":
            {
                "Player color": "Yellow",
                "colorA": "#ffed19",
                "colorB": "#ffc600",
                "Number": "#1d1f23",
                "Time turn": "#ffe000",
                "Time turn outline": "#c8beb6",
                "Restangls": "#ffd000"
            },
        "#008000":
            {
                "Player color": "Green",
                "colorA": "#83d501",
                "colorB": "#4c9900",
                "Number": "#ffffff",
                "Time turn": "#5bad00",
                "Time turn outline": "none",
                "Restangls": "#59a801"
            },
        "#ee82ee":
            {
                "Player color": "Violet",
                "colorA": "#cd00f0",
                "colorB": "#b400e8",
                "Number": "#ffffff",
                "Time turn": "#bd00e0",
                "Time turn outline": "none",
                "Restangls": "#a100bf"
            },
        "#0000ff":
            {
                "Player color": "Blue",
                "colorA": "#03c9ff",
                "colorB": "#028aff",
                "Number": "#ffffff",
                "Time turn": "#0397ff",
                "Time turn outline": "none",
                "Restangls": "#038bff"
            },
        "#ff0000":
            {
                "Player color": "Red",
                "colorA": "#fd0000",
                "colorB": "#d10000",
                "Number": "#ffffff",
                "Time turn": "#f20000",
                "Time turn outline": "none",
                "Restangls": "#bc0000"
            },

    }


class Users(models.Model):
    # Идентификатор пользователя (уникальная строка и не меняется для устройства)
    user_id = models.CharField(verbose_name = "user id", max_length = 300, null = False)
    # URL страницы для данной игры (он не должен меняться для пользователя в будущем при старте новых игр)
    full_url = models.CharField(verbose_name = "url", max_length = 100, default = "full_url")
    # Идентификатор пользователя (уникальная строка и не меняется для устройства)
    short_url = models.CharField(verbose_name = "short url", max_length = 50, default = "short_url")

    def __str__(self):
        return "ID = {0}\nUID = {1}\nFull url = {2}\nShort url = {3}".format(self.id, self.user_id, self.full_url,
                                                                             self.short_url)

    def get_id(self):
        return self.id

    def get_user_id(self):
        return self.user_id

    def set_user_id(self, user_id):
        self.user_id = user_id
        self.save(update_fields = ['user_id'])

    def get_full_url(self):
        return self.full_url

    def set_full_url(self, full_url):
        self.full_url = full_url
        self.save(update_fields = ['full_url'])

    def get_short_url(self):
        return self.short_url

    def set_short_url(self, short_url):
        self.short_url = short_url
        self.save(update_fields = ['short_url'])

    def get_user_JSON(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "full_url": self.full_url,
            "short_url": self.short_url
        }

    def new_user_JSON(self, user_JSON):
        user_id = user_JSON["user_id"]
        user = Users(user_id = user_id)
        full_url = self.create_full_url(user_id, user.id)
        short_url = self.create_short_url(full_url)
        user.save()
        user.set_full_url(full_url)
        user.set_short_url(short_url)
        return user.get_user_JSON()

    def new_user_JSON_get_short_url(self, user_JSON):
        user_id = user_JSON["user_id"]
        user = Users(user_id = user_id)
        user.save()
        full_url = self.create_full_url(user_id, user.id)
        short_url = self.create_short_url(full_url)
        user.set_full_url(full_url)
        user.set_short_url(short_url)
        return {"short_url": user.short_url}

    def create_full_url(self, user_id, id):
        unique_url = "{0}/{1}{2}{3}{4}{5}".format("user", random.choice(string.ascii_letters), id * 3,
                                                  random.choice(string.ascii_letters), user_id[-5:],
                                                  random.choice(string.ascii_letters)).lower()
        full_url = base_url + unique_url
        print("full_url = {0}".format(full_url))
        return full_url

    def create_short_url(self, full_url):
        # short_url = get_short_url(id)
        import pyshorteners

        s = pyshorteners.Shortener('Tinyurl', timeout = 10)
        short_url = s.short(full_url)
        print(short_url)
        return short_url


class Games(models.Model):
    # Пользователь, связывает с моделью User.
    user = models.ForeignKey(Users, verbose_name = "user", on_delete = models.CASCADE)
    # Общее время игры
    total_game_time = models.CharField(verbose_name = "total time", max_length = 10, default = "00:00:00")
    # Включена ли пауза, включена - True, выключена - False.
    pause = models.BooleanField(verbose_name = "pause", default = True)
    # Состояние хода, идет - true, закончился - false
    turn_run = models.BooleanField(verbose_name = "turn run", default = False)
    # Цвет активного игрока
    active = ColorField(verbose_name = "active")  # default = '#FF0000'

    def __str__(self):
        return "ID = {0}\nTotal time = {1}".format(self.id, self.total_game_time)

    def get_id(self):
        return self.id

    def get_user(self):
        return self.user_id

    def get_total_time(self):
        return self.total_game_time

    def set_total_time(self, total_game_time):
        self.total_game_time = total_game_time
        self.save(update_fields = ['total_game_time'])

    def get_pause(self):
        return self.pause

    def set_pause(self, pause):
        self.pause = pause
        self.save(update_fields = ['pause'])

    def get_turn_run(self):
        return self.turn_run

    def set_turn_run(self, turn_run):
        self.turn_run = turn_run
        self.save(update_fields = ['turn_run'])

    def get_active(self):
        return self.active.lower()

    def set_active(self, active):
        self.active = active.lower()
        self.save(update_fields = ['active'])

    def get_game_JSON(self):
        return {
            "id": self.id,
            "user": self.user_id,
            "total_game_time": self.total_game_time
        }

    def new_game_JSON(self, user_JSON, active_player):
        user_id = user_JSON["user_id"]
        user = Users.objects.get(user_id = user_id)
        game = Games(user = user, active = active_player)
        game.save()
        return game.get_game_JSON()

    def new_game_JSON_get_id(self, user_JSON, active_player):
        user_id = user_JSON["user_id"]
        user = Users.objects.get(user_id = user_id)
        game = Games(user = user, active = active_player)
        game.save()
        return {"id": game.id}

    def get_total_time_for_web_api(self):
        total_time = self.total_game_time.split(':')
        return {'h': total_time[0],
                'm': total_time[1],
                's': total_time[2]}


class Players(models.Model):
    # Игра, связывает с моделью Game.
    game = models.ForeignKey(Games, verbose_name = "game", on_delete = models.CASCADE)
    # Цвет игрока
    color = ColorField(verbose_name = "color", null = False)  # default = '#FF0000'
    # Время, затраченное игроком на ходы.
    total_player_time = models.CharField(verbose_name = "player time", max_length = 10, default = "00:00")

    def __str__(self):
        return "ID = {0}\nColor = {1}\nPlayer time = {2}".format(self.id, self.color, self.total_player_time)

    def get_id(self):
        return self.id

    def get_color(self):
        return self.color.lower()

    def set_color(self, color):
        self.color = color.lower()
        self.save(update_fields = ['color'])

    def get_total_player_time(self):
        return self.total_player_time

    def get_total_player_time_for_web_api(self):
        total_player_time = self.total_player_time.split(':')
        return {'m': total_player_time[0],
                's': total_player_time[1]}

    def set_total_player_time(self, total_player_time):
        self.total_player_time = total_player_time
        self.save(update_fields = ['total_player_time'])

    def get_player_JSON(self):
        return {
            "id": self.id,
            "game": self.game_id,
            "color": self.color.lower(),
            "total_player_time": self.total_player_time
        }

    def new_player_JSON(self, game_JSON, color):
        print(game_JSON)
        game_id = game_JSON["id"]
        game = Games.objects.get(id = game_id)
        player = Players(game = game, color = color.lower())
        player.save()
        return player.get_player_JSON()

    def new_player_JSON_without_get(self, game_JSON, color):
        game_id = game_JSON["id"]
        game = Games.objects.get(id = game_id)
        player = Players(game = game, color = color.lower())
        player.save()


class Turns(models.Model):
    # игрок, связывает с моделью Player.
    player = models.ForeignKey(Players, verbose_name = "player", on_delete = models.CASCADE)
    # Номер раунда.
    round_number = models.IntegerField(verbose_name = "round", null = False)
    # Время, затраченное игроком на ход.
    turn_time = models.CharField(verbose_name = "turn time", max_length = 10, null = False)

    def get_id(self):
        return self.id

    def get_player(self):
        return self.player_id

    def set_player(self, player):
        self.player = player
        self.save(update_fields = ['player'])

    def get_round_number(self):
        return self.round_number

    def get_turn_time(self):
        return self.turn_time

    def set_turn_time(self, turn_time):
        self.turn_time = turn_time
        self.save(update_fields = ['turn_time'])

    def get_turn_time_for_web_api(self):
        turn_time = self.turn_time.split(':')
        return {'m': turn_time[0],
                's': turn_time[1]}

    def get_turn_JSON(self):
        return {
            "id": self.id,
            "player": self.player_id,
            "round_number": self.round_number,
            "turn_time": self.turn_time
        }

    def new_turn_JSON(self, player_JSON, turn_JSON):
        player_id = player_JSON["id"]
        player = Players.objects.get(id = player_id)
        turns = Turns.objects.filter(player = player_id).count()
        round_number = turns + 1
        turn_time = turn_JSON["turn_time"]
        turn = Turns(player = player, round_number = round_number, turn_time = turn_time)
        turn.save()
        return turn.get_turn_JSON()

    def new_turn_JSON_get_turn_time(self, gameId, player_JSON, turn_JSON):
        color = player_JSON["color"]
        player = Players.objects.get(color = color, game_id = gameId)
        turns = Turns.objects.filter(player_id = player.get_id()).count()
        round_number = turns + 1
        turn_time = turn_JSON["turn_time"]
        turn = Turns(player = player, round_number = round_number, turn_time = turn_time)
        turn.save()
        return {"turn_time": turn.turn_time}
