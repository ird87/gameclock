from rest_framework import serializers
from .models import Users, Games, Players, Turns

# Стандартные ----------------------------------------------------------------------------------------------------------
class UsersSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = ('id', 'user_id', 'full_url', 'short_url')

class GamesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Games
        fields = ('id', 'user_id', 'total_game_time')

class PlayersSerializer(serializers.ModelSerializer):
    class Meta:
        model = Players
        fields = ('id', 'game_id', 'color', 'total_player_time')

class TurnsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Turns
        fields = ('id', 'player_id', 'round_number', 'turn_time')


# Для POST = game ------------------------------------------------------------------------------------------------------
class UsersSerializer_game(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = ('short_url',)

class GamesSerializer_game(serializers.ModelSerializer):
    class Meta:
        model = Games
        fields = ('id',)
