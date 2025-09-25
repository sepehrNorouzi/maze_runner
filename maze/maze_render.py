from django.utils.safestring import mark_safe
import html

def _render_maze_grid(maze, cell_colors, title="Maze", max_px=700, min_cell=6, max_cell=20):
    """
    Helper that renders a maze (2D list) into a responsive CSS-grid HTML snippet.
      - max_px: the preferred maximum pixel width of the grid area before enabling scrolling
      - min_cell, max_cell: bounds for computed cell sizes (px)
    """
    if not maze:
        return "No maze data"

    rows = len(maze)
    cols = len(maze[0]) if rows else 0
    total = rows * cols if rows and cols else 0

    # compute a reasonable cell size so the grid fits roughly into max_px width
    # but keep bounds so it doesn't get impossibly tiny or huge
    if cols > 0:
        approx = max( min(max_cell, max(min_cell, max_px // cols)), min_cell )
    else:
        approx = max_cell
    cell_size = int(approx)

    # CSS & container: fixed max width and height, with overflow auto for very large mazes
    css = f"""
    <style>
    /* Maze preview widget - isolated by class names to avoid global collisions */
    .mz-widget {{ font-family: system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial; }}
    .mz-grid-wrap {{
        max-width: {max_px}px;
        max-height: 600px;
        overflow: auto;
        border: 1px solid #e6e6e6;
        background: #fafafa;
        padding: 8px;
        border-radius: 6px;
    }}
    .mz-grid {{
        display: grid;
        grid-template-columns: repeat({cols}, {cell_size}px);
        grid-auto-rows: {cell_size}px;
        gap: 1px;
        background: #ddd;
    }}
    .mz-cell {{
        width: {cell_size}px;
        height: {cell_size}px;
        box-sizing: border-box;
        border-radius: 2px;
    }}
    .mz-legend {{
        margin-top: 8px;
        display:flex;
        gap:10px;
        flex-wrap:wrap;
        align-items:center;
        font-size:12px;
    }}
    .mz-legend-item {{
        display:inline-flex;
        gap:6px;
        align-items:center;
        background:#fff;
        padding:4px 6px;
        border-radius:6px;
        border:1px solid #eee;
    }}
    .mz-swatch {{
        width:14px; height:14px; border-radius:3px; border:1px solid rgba(0,0,0,0.08);
    }}
    .mz-title {{
        margin-bottom:6px;
        font-weight:600;
        font-size:13px;
    }}
    /* make small mazes look centered */
    .mz-grid-wrap.center {{ display:inline-block; }}
    </style>
    """

    html_parts = [css, f'<div class="mz-widget">']
    html_parts.append(f'<div class="mz-title">{html.escape(title)} — {rows}×{cols}</div>')
    # center tiny grids horizontally (optional)
    wrap_class = "mz-grid-wrap center" if cols <= 30 else "mz-grid-wrap"
    html_parts.append(f'<div class="{wrap_class}">')
    html_parts.append(f'<div class="mz-grid" role="grid" aria-label="{html.escape(title)}">')

    # flatten cells into divs. include title/tooltip for coordinates and value
    for r, row in enumerate(maze):
        for c, cell in enumerate(row):
            color = cell_colors.get(cell, "#cccccc")
            tooltip = f"r={r},c={c},v={cell}"
            # avoid accidental HTML injection
            html_parts.append(
                f'<div class="mz-cell" title="{html.escape(tooltip)}" style="background:{html.escape(color)}"></div>'
            )

    html_parts.append('</div>')  # .mz-grid
    html_parts.append('</div>')  # .mz-grid-wrap

    # legend (ordered)
    html_parts.append('<div class="mz-legend">')
    # show values in specific order if present in cell_colors
    for val, label in [(2, "Start"), (3, "Finish"), (4, "Path"), (0, "Empty"), (1, "Wall")]:
        if val in cell_colors:
            color = cell_colors[val]
            html_parts.append(
                f'<div class="mz-legend-item"><span class="mz-swatch" style="background:{html.escape(color)}"></span>'
                f'<span>{html.escape(label)}</span></div>'
            )
    html_parts.append('</div>')  # legend
    html_parts.append('</div>')  # widget

    return mark_safe("".join(html_parts))
