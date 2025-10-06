from celery import shared_task
from django.utils import timezone
from django.core.files.base import ContentFile


@shared_task
def generate_maze_image(maze_id):
    from maze.models import Maze
    from maze.utils import maze_to_svg

    maze = Maze.objects.get(pk=maze_id)
    svg = maze_to_svg(maze.get_maze_binary())
    filename = f"maze_{maze.creator}_{timezone.now().strftime('%Y%m%d%H%M%S')}.svg"
    maze.maze_image.save(filename, ContentFile(svg), save=True)

@shared_task
def generate_solved_maze_image(maze_id):
    from maze.models import Maze
    from maze.utils import maze_to_svg

    maze = Maze.objects.get(pk=maze_id)
    svg = maze_to_svg(maze.get_solved_maze())
    filename = f"solved_maze_{maze.creator}_{timezone.now().strftime('%Y%m%d%H%M%S')}.svg"
    maze.solved_maze_image.save(filename, ContentFile(svg), save=True)
