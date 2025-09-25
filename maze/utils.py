from maze_runner.cpp_build import maze_generator

def create_maze(size, mode, hybrid_prob=0.5):
    return maze_generator.generate_maze(size, mode, hybrid_prob)
