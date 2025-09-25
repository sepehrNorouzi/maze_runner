from django.conf import settings
from django.core.validators import MaxValueValidator
from django.db import models

from common.models import BaseModel


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

    def set_maze_binary(self, grid):
        flat = [v for row in grid for v in row]
        bitstring = 0
        for v in flat:
            bitstring = (bitstring << 2) | v

        rows, cols = len(grid), len(grid[0]) if grid else 0
        header = rows.to_bytes(4, "big") + cols.to_bytes(4, "big")

        num_bits = len(flat) * 2
        num_bytes = (num_bits + 7) // 8
        packed = bitstring.to_bytes(num_bytes, "big")
        self.maze_binary = header + packed

    def get_maze_binary(self):
        """Unpack binary data back to 2D grid"""
        if not self.maze_binary:
            return []

        rows = int.from_bytes(self.maze_binary[:4], "big")
        cols = int.from_bytes(self.maze_binary[4:8], "big")
        packed = self.maze_binary[8:]

        bitstring = int.from_bytes(packed, "big")
        total_values = rows * cols

        flat = []
        for i in range(total_values):
            shift = (total_values - 1 - i) * 2
            val = (bitstring >> shift) & 0b11
            flat.append(val)

        result = [flat[i * cols:(i + 1) * cols] for i in range(rows)]
        return result

    def __str__(self):
        return f'{self.creator} - {self.id}'
