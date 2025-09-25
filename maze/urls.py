from django.urls import path
from maze.views import MazeCreateView

urlpatterns = [
    path('create/', MazeCreateView.as_view(), name='maze-create' ),
]
