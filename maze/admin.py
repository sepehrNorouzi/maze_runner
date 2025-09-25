import time

from django import forms
from django.contrib import admin, messages
from django.core.exceptions import ValidationError
import json

from django.db.models import QuerySet
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import path
from django.utils.safestring import mark_safe

from maze.maze_render import _render_maze_grid
from maze.models import Maze


class MazeAdminForm(forms.ModelForm):
    maze_grid_input = forms.CharField(
        widget=forms.Textarea(attrs={
            'rows': 10,
            'cols': 50,
            'placeholder': 'Enter maze as JSON array or comma-separated values:\n[[1,0,1,0],[0,1,1,1],[1,1,0,1]]\nor\n1,0,1,0\n0,1,1,1\n1,1,0,1'
        }),
        required=False,
        help_text="Enter maze data as JSON array or newline-separated rows with comma-separated values"
    )

    class Meta:
        model = Maze
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # If editing existing maze, populate the grid input field
        if self.instance.pk and self.instance.maze_binary:
            try:
                grid = self.instance.get_maze_binary()
                self.fields['maze_grid_input'].initial = json.dumps(grid)
            except:
                self.fields['maze_grid_input'].initial = "Error reading binary data"

    def clean_maze_grid_input(self):
        maze_input = self.cleaned_data.get('maze_grid_input', '').strip()

        if not maze_input:
            return None

        try:
            # Try to parse as JSON first
            if maze_input.startswith('['):
                grid = json.loads(maze_input)
            else:
                # Parse as newline-separated, comma-separated format
                lines = maze_input.split('\n')
                grid = []
                for line in lines:
                    if line.strip():
                        row = [int(x.strip()) for x in line.split(',')]
                        grid.append(row)

            # Validate grid
            if not grid:
                raise ValidationError("Empty grid provided")

            # Check if all rows have same length
            row_lengths = [len(row) for row in grid]
            if len(set(row_lengths)) > 1:
                raise ValidationError(f"All rows must have same length. Found lengths: {row_lengths}")

            # Check cell values (must be 0-15 for 4-bit storage)
            for row_idx, row in enumerate(grid):
                for col_idx, cell in enumerate(row):
                    if not isinstance(cell, int) or cell < 0 or cell > 15:
                        raise ValidationError(
                            f"Cell at ({row_idx}, {col_idx}) has invalid value {cell}. Must be integer 0-15.")

            return grid

        except json.JSONDecodeError as e:
            raise ValidationError(f"Invalid JSON format: {e}")
        except ValueError as e:
            raise ValidationError(f"Invalid number format: {e}")
        except Exception as e:
            raise ValidationError(f"Error parsing maze data: {e}")

    def save(self, commit=True):
        instance = super().save(commit=False)

        # If maze grid input was provided, convert it to binary
        maze_grid = self.cleaned_data.get('maze_grid_input')
        if maze_grid:
            instance.height = len(maze_grid)
            instance.width = len(maze_grid[0]) if maze_grid else 0
            instance.set_maze_binary(maze_grid)

        if commit:
            instance.save()
        return instance


@admin.register(Maze)
class MazeAdmin(admin.ModelAdmin):
    form = MazeAdminForm

    list_display = ['id', 'creator', 'dimensions', 'binary_size', 'created_time', 'solved', 'solved_time']
    list_filter = ['creator', 'created_time']
    readonly_fields = [
        'created_time', 'updated_time', 'maze_preview', 'maze_binary',
        'solved_maze_preview', 'solved_maze_grid', 'solved_maze', 'solved_time', 'solved']
    raw_id_fields = ['creator']

    @admin.action()
    def solve_maze(self, request, qs: QuerySet(Maze)):
        for obj in qs:
            obj.solve()
        messages.info(request, message="{} Maze(s) solved successfully.".format(len(qs)))

    solve_maze.short_description = "Solve selected mazes."

    @admin.action()
    def un_solve_maze(self, request, qs: QuerySet(Maze)):
        for obj in qs:
            obj.un_solve()
        messages.info(request, message="{} Maze(s) UN-solved successfully.".format(len(qs)))

    un_solve_maze.short_description = "Un-Solve selected mazes."

    fieldsets = (
        ('Basic Information', {
            'fields': ('creator', 'height', 'width')
        }),
        ('Maze Data', {
            'fields': ('maze_grid_input', 'maze_binary'),
            'description': 'Enter maze data in the text area above, or upload binary data directly.'
        }),
        ('Preview', {
            'fields': ('maze_preview',),
            'classes': ('collapse',)
        }),
        ('Solved Data', {
            'fields': ('solved', 'solved_time', 'solved_maze', 'solved_maze_preview', 'solved_maze_grid'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_time', 'updated_time'),
            'classes': ('collapse',)
        })
    )

    def response_change(self, request, obj):
        if "_solve" in request.POST:
            t0 = time.time_ns()
            obj.solve()
            t1 = time.time_ns()
            self.message_user(request, "Maze {} solved successfully in {} nano seconds.".format(obj, str(t1 - t0)))
            return HttpResponseRedirect(".")
        elif '_un_solve' in request.POST:
            t0 = time.time_ns()
            obj.un_solve()
            t1 = time.time_ns()
            self.message_user(request, "Maze {} un-solved successfully in {} nano seconds.".format(obj, str(t1 - t0)))
            return HttpResponseRedirect(".")
        return super().response_change(request, obj)

    def dimensions(self, obj):
        return f"{obj.width} × {obj.height}"

    dimensions.short_description = "Dimensions"

    def binary_size(self, obj):
        if obj.maze_binary:
            size_bytes = len(obj.maze_binary)
            if size_bytes < 1024:
                return f"{size_bytes} bytes"
            elif size_bytes < 1024 * 1024:
                return f"{size_bytes / 1024:.1f} KB"
            else:
                return f"{size_bytes / (1024 * 1024):.1f} MB"
        return "No data"

    binary_size.short_description = "Binary Size"

    def maze_preview(self, obj: Maze):
        """
        Display a visual preview of the maze in Django admin.

        Assumes obj has a 'maze' attribute containing a 2D array where:
        - 0 = empty space (white)
        - 1 = wall (black)
        - 2 = start (green)
        - 3 = finish (red)
        """
        if not hasattr(obj, 'maze_binary') or not obj.maze_binary:
            return "No maze data"

        maze = obj.get_maze_binary()

        cell_colors = {
            0: '#ffffff',  # Empty - white
            1: '#1f2937',  # Wall - near-black (so not harsh)
            2: '#10b981',  # Start - green (Tailwind emerald-500)
            3: '#ef4444',  # Finish - red (Tailwind red-500)
        }

        return _render_maze_grid(maze, cell_colors)

    maze_preview.short_description = "Maze Preview"

    def solved_maze_preview(self, obj: Maze):
        if not obj.solved or not obj.solved_maze:
            return 'No solved maze data'
        maze = obj.get_solved_maze()

        # colors with distinct path color
        cell_colors = {
            0: '#ffffff',  # Empty - white
            1: '#0f172a',  # Wall - very dark
            2: '#10b981',  # Start - green
            3: '#ef4444',  # Finish - red
            4: '#f59e0b',  # Path - amber/orange for good contrast
        }

        return _render_maze_grid(maze, cell_colors, title="Solved Maze")

    solved_maze_preview.short_description = "Solved Maze Preview"

    def solved_maze_grid(self, obj: Maze):
        if not obj.solved or not obj.solved_maze:
            return 'No solved maze data'
        return obj.get_solved_maze()

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)

        if not obj:
            form.base_fields['creator'].initial = request.user

        return form

    def save_model(self, request, obj, form, change):
        if not change and not obj.creator:
            obj.creator = request.user
        super().save_model(request, obj, form, change)

    actions = ['export_as_json', 'validate_maze_data', 'solve_maze', 'un_solve_maze']

    def export_as_json(self, request, queryset):
        """Export selected mazes as JSON"""
        from django.http import JsonResponse

        export_data = []
        for maze in queryset:
            try:
                grid = maze.get_maze_binary()
                export_data.append({
                    'id': maze.id,
                    'creator': maze.creator.username,
                    'width': maze.width,
                    'height': maze.height,
                    'grid': grid
                })
            except Exception as e:
                export_data.append({
                    'id': maze.id,
                    'error': str(e)
                })

        response = JsonResponse(export_data, safe=False)
        response['Content-Disposition'] = 'attachment; filename="mazes_export.json"'
        return response

    export_as_json.short_description = "Export selected mazes as JSON"

    def validate_maze_data(self, request, queryset):
        """Validate binary data integrity"""
        from django.contrib import messages

        valid_count = 0
        invalid_count = 0

        for maze in queryset:
            try:
                grid = maze.get_maze_binary()
                if grid and len(grid) == maze.height and len(grid[0]) == maze.width:
                    valid_count += 1
                else:
                    invalid_count += 1
            except:
                invalid_count += 1

        messages.success(request, f'Validation complete: {valid_count} valid, {invalid_count} invalid mazes.')

    validate_maze_data.short_description = "Validate maze binary data"

