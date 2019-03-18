"""ChessClockAPI URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

from chess_clock import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.Main.as_view()),
    path('game', views.Game.as_view()),
    path('<int:gameId>/play', views.Play.as_view()),
    path('<int:gameId>/pause', views.Pause.as_view()),
    path('<int:gameId>/done', views.Done.as_view()),
    path('<int:gameId>/game_over', views.GameOver.as_view()),
    # path('clock/<int:players>', views.Clock.as_view()),
    path('user/<full_url>', views.Clock.as_view()),
    # path('<short_url>', views.Clock.as_view())

]
