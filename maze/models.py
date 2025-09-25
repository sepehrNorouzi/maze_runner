from django.conf import settings
from django.core.validators import MaxValueValidator
from django.db import models
from django.utils import timezone

from common.models import BaseModel
from maze.utils import unbit_pack_2d, bit_pack_2d, solve_maze


class Maze(BaseModel):
    class GrowingTreeAlgoType(models.TextChoices):
        NEWEST = 'NEWEST', 'Newest'
        RANDOM = 'RANDOM', 'Random'
        HYBRID = 'HYBRID', 'Hybrid'

    creator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Creator")
    height = models.PositiveIntegerField(default=100, verbose_name="Height")
    width = models.PositiveIntegerField(default=100, verbose_name="Width")
    growing_tree_algorithm_choice = models.CharField(choices=GrowingTreeAlgoType.choices,
                                                     default=GrowingTreeAlgoType.NEWEST, )
    hybrid_prob = models.FloatField(default=0.0, verbose_name="Hybrid Probability", validators=[MaxValueValidator(1.0)])

    maze_binary = models.BinaryField(null=True, blank=True, verbose_name="Binary data")
    solved = models.BooleanField(default=False, verbose_name="Solved")
    solved_maze = models.BinaryField(null=True, blank=True, verbose_name="Solved Maze")
    solved_time = models.DateTimeField(null=True, blank=True, verbose_name="Solved Time")


    def set_maze_binary(self, grid):
        if self.maze_binary:
            return
        packed = bit_pack_2d(grid)
        self.maze_binary = packed
        self.save()

    def get_maze_binary(self):
        """Unpack binary data back to 2D grid"""
        if not self.maze_binary:
            return []

        return unbit_pack_2d(self.maze_binary)

    def set_solved_maze(self, grid):
        if self.solved_maze:
            return
        self.solved = True
        self.solved_time = timezone.now()
        self.solved_maze = bit_pack_2d(grid)
        self.save()

    def get_solved_maze(self):
        if not self.solved_maze:
            return []
        return unbit_pack_2d(self.solved_maze)

    def solve(self):
        if self.solved:
            return
        solved_grid = solve_maze(self.get_maze_binary())
        self.set_solved_maze(solved_grid)

    def un_solve(self):
        if not self.solved:
            return
        self.solved = False
        self.solved_time = None
        self.solved_maze = None
        self.save()

    def __str__(self):
        return f'{self.creator} - {self.id}'
