from django import forms
from django.contrib import admin
from django.core.exceptions import ValidationError
import json

from django.utils.safestring import mark_safe

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

    list_display = ['id', 'creator', 'dimensions', 'binary_size', 'created_time']
    list_filter = ['creator', 'created_time']
    readonly_fields = ['created_time', 'updated_time', 'maze_preview', 'maze_binary']
    raw_id_fields = ['creator']

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
        ('Metadata', {
            'fields': ('created_time', 'updated_time'),
            'classes': ('collapse',)
        })
    )

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

        # Define colors for each cell type
        cell_colors = {
            0: '#ffffff',  # Empty - white
            1: '#000000',  # Wall - black
            2: '#00ff00',  # Start - green
            3: '#ff0000',  # Finish - red
        }

        html = ['<table style="border-collapse: collapse; font-family: monospace;">']

        for row in maze:
            html.append('<tr>')
            for cell in row:
                color = cell_colors.get(cell, '#cccccc')  # Default to gray if unknown value
                html.append(
                    f'<td style="width: 20px; height: 20px; background-color: {color}; border: 1px solid #ddd;"></td>')
            html.append('</tr>')

        html.append('</table>')

        # Add a legend
        html.append('<div style="margin-top: 10px; font-size: 12px;">')
        html.append('<strong>Legend:</strong> ')
        html.append('<span style="background-color: #ffffff; color: #000000; border: 1px solid #000; padding: 2px 4px;">Empty</span> ')
        html.append('<span style="background-color: #000000; color: white; padding: 2px 4px;">Wall</span> ')
        html.append('<span style="background-color: #00ff00; color: black; padding: 2px 4px;">Start</span> ')
        html.append('<span style="background-color: #ff0000; color: black; padding: 2px 4px;">Finish</span>')
        html.append('</div>')

        return mark_safe(''.join(html))


    maze_preview.short_description = "Maze Preview"

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)

        if not obj:
            form.base_fields['creator'].initial = request.user

        return form

    def save_model(self, request, obj, form, change):
        if not change and not obj.creator:
            obj.creator = request.user
        super().save_model(request, obj, form, change)

    actions = ['export_as_json', 'validate_maze_data']

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

