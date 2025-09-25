import time

from maze_runner.cpp_build import maze_generator

def create_maze(size, mode, hybrid_prob=0.5):
    return maze_generator.generate_maze(size, mode, hybrid_prob)

def solve_maze(grid):
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
