from django.contrib import admin

# Register your models here.

from .models import Users, Games, Players, Turns

@admin.register(Users)
class GameSessionAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_id', 'full_url', 'short_url')

@admin.register(Games)
class GameSessionAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'active', 'pause', 'total_game_time')

@admin.register(Players)
class GameSessionAdmin(admin.ModelAdmin):
    list_display = ('id', 'game', 'color', 'total_player_time')

@admin.register(Turns)
class GameSessionAdmin(admin.ModelAdmin):
    list_display = ('id', 'player', 'round_number', 'turn_time')




#  CkAskN7Q75M9a92 LHBJkscqxB5matx

