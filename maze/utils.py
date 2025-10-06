import time
from typing import List, Optional, Tuple



def create_maze(size, mode, hybrid_prob=0.5):
    from maze_runner.cpp_build import maze_generator
    return maze_generator.generate_maze(size, mode, hybrid_prob)


def solve_maze(grid):
    from maze_runner.cpp_build import maze_generator
    _t0 = time.time_ns()
    g = maze_generator.solve_maze(grid)
    _t1 = time.time_ns()
    print("SOLVED in: ", _t1 - _t0)
    return g


def bit_pack_2d(grid):
    if not grid:
        return (0).to_bytes(4, "big") + (0).to_bytes(4, "big")

    rows, cols = len(grid), len(grid[0])
    flat = [v for row in grid for v in row]

    bits_per_val = 3
    bitstring = 0
    for v in flat:
        if v < 0 or v > 7:
            raise ValueError(f"Value {v} out of range (must be 0–7)")
        bitstring = (bitstring << bits_per_val) | v

    header = rows.to_bytes(4, "big") + cols.to_bytes(4, "big")
    num_bits = len(flat) * bits_per_val
    num_bytes = (num_bits + 7) // 8
    packed = bitstring.to_bytes(num_bytes, "big")

    return header + packed


def unbit_pack_2d(_binary):
    rows = int.from_bytes(_binary[:4], "big")
    cols = int.from_bytes(_binary[4:8], "big")
    packed = _binary[8:]

    if rows == 0 or cols == 0:
        return []

    bits_per_val = 3
    total_values = rows * cols
    bitstring = int.from_bytes(packed, "big")

    flat = []
    for i in range(total_values):
        shift = (total_values - 1 - i) * bits_per_val
        val = (bitstring >> shift) & ((1 << bits_per_val) - 1)
        flat.append(val)

    result = [flat[i * cols:(i + 1) * cols] for i in range(rows)]
    return result



def maze_to_svg(
        grid: List[List[int]],
        cell_size: int = 30,
        wall_color: str = "#141414",
        path_color: str = "#7a211b",
        bg_color: str = "#ddd",
        start_color: str = "#2ecc71",
        finish_color: str = "#e74c3c",
        stroke_color: Optional[str] = None,
        stroke_width: int = 0,
) -> str:
    """
    Convert a 2D maze grid to an SVG string (and optionally write to filename).

    Parameters
    ----------
    grid : List[List[int]]
        2D list where 0=empty, 1=wall, 2=start, 3=finish
    cell_size : int
        Pixel size for each cell
    wall_color, bg_color, start_color, finish_color, path_color : str
        CSS color strings for elements
    stroke_color : Optional[str]
        Color for rectangle outlines; None => no stroke
    stroke_width : int
        Stroke width for rectangles


    Returns
    -------
    svg : str
        The SVG document as a string.
    """
    if not grid or not any(grid):
        raise ValueError("Grid must be a non-empty 2D list")

    # Ensure rectangular grid
    rows = len(grid)
    cols = max(len(r) for r in grid)
    for r in grid:
        if len(r) != cols:
            # make rows same length by padding with 0 (empty)
            r += [0] * (cols - len(r))

    width = cols * cell_size
    height = rows * cell_size

    stroke_attr = ""
    if stroke_color and stroke_width > 0:
        stroke_attr = f' stroke="{stroke_color}" stroke-width="{stroke_width}"'
    elif stroke_width > 0:  # stroke color not provided, default to #000
        stroke_attr = f' stroke="#000" stroke-width="{stroke_width}"'

    parts = []
    # header
    parts.append(f'<?xml version="1.0" encoding="UTF-8"?>')
    parts.append(f'<svg xmlns="http://www.w3.org/2000/svg" '
                 f'width="{width}" height="{height}" viewBox="0 0 {width} {height}">')

    parts.append(f'<rect x="0" y="0" width="{width}" height="{height}" fill="{bg_color}" />')

    for r in range(rows):
        for c in range(cols):
            val = grid[r][c]
            x = c * cell_size
            y = r * cell_size
            if val == 1:
                parts.append(
                    f'<rect x="{x}" y="{y}" width="{cell_size}" height="{cell_size}" '
                    f'fill="{wall_color}"{stroke_attr} />'
                )
            elif val == 4:
                parts.append(
                    f'<rect x="{x}" y="{y}" width="{cell_size - 1}" height="{cell_size - 1}" '
                    f'fill="{path_color}"{stroke_attr} />'
                )

    def star_path(cx: float, cy: float, r_outer: float, r_inner: float, points: int = 5) -> str:
        from math import sin, cos, pi
        coords = []
        angle = -pi / 2  # start at top
        step = pi / points
        for i in range(2 * points):
            r = r_outer if i % 2 == 0 else r_inner
            x = cx + r * cos(angle)
            y = cy + r * sin(angle)
            coords.append(f"{x},{y}")
            angle += step
        return " ".join(coords)

    # draw start/finish on top of walls (if any)
    marker_margin = cell_size * 0.15
    radius = (cell_size / 2) - marker_margin
    for r in range(rows):
        for c in range(cols):
            val = grid[r][c]
            cx = c * cell_size + cell_size / 2
            cy = r * cell_size + cell_size / 2
            if val == 2:  # start: green circle
                parts.append(
                    f'<circle cx="{cx}" cy="{cy}" r="{radius}" fill="{start_color}" />'
                )
            elif val == 3:  # finish: red star polygon
                r_outer = radius
                r_inner = radius * 0.45
                pts = star_path(cx, cy, r_outer, r_inner, points=5)
                parts.append(f'<polygon points="{pts}" fill="{finish_color}" />')

    parts.append("</svg>")
    svg = "\n".join(parts)
    return svg