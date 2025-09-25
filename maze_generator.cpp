
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include <random>
#include <vector>
#include <string>
#include <algorithm>
#include <chrono>

namespace py = pybind11;

enum Strategy { STR_NEWEST, STR_RANDOM, STR_HYBRID };
struct Pos { int r, c; };

static std::mt19937 rng((unsigned)std::chrono::high_resolution_clock::now().time_since_epoch().count());

bool in_bounds(int r, int c, int n) {
    return r > 0 && r < n-1 && c > 0 && c < n-1;
}

int choose_index(int size, Strategy strat, double hybrid_prob = 0.7) {
    if (size <= 0) return -1;
    if (strat == STR_NEWEST) return size - 1;
    if (strat == STR_RANDOM) return std::uniform_int_distribution<int>(0, size-1)(rng);
    std::uniform_real_distribution<double> d(0.0, 1.0);
    if (d(rng) < hybrid_prob) return size - 1;
    return std::uniform_int_distribution<int>(0, size-1)(rng);
}

std::vector<std::vector<int>> generate_maze_cpp(int n, Strategy strat, double hybrid_prob = 0.7) {
    if (n < 3) n = 3;
    if (n % 2 == 0) ++n;

    std::vector<std::vector<int>> grid(n, std::vector<int>(n, 1));

    int dr[4] = {-2, 2, 0, 0};
    int dc[4] = {0, 0, -2, 2};

    std::uniform_int_distribution<int> dist(0, (n-1)/2 - 1);
    int sr = dist(rng)*2 + 1;
    int sc = dist(rng)*2 + 1;

    grid[sr][sc] = 0;
    std::vector<Pos> cell_list;
    cell_list.push_back({sr, sc});

    while (!cell_list.empty()) {
        int idx = choose_index(static_cast<int>(cell_list.size()), strat, hybrid_prob);
        Pos cur = cell_list[idx];

        std::vector<int> dirs = {0,1,2,3};
        std::shuffle(dirs.begin(), dirs.end(), rng);

        bool carved = false;
        for (int d : dirs) {
            int nr = cur.r + dr[d];
            int nc = cur.c + dc[d];
            if (in_bounds(nr, nc, n) && grid[nr][nc] == 1) {
                grid[nr][nc] = 0;
                grid[cur.r + dr[d]/2][cur.c + dc[d]/2] = 0;
                cell_list.push_back({nr, nc});
                carved = true;
                break;
            }
        }

        if (!carved) {
            cell_list.erase(cell_list.begin() + idx);
        }
    }

    grid[1][1] = 2;
    grid[n-2][n-2] = 3;

    return grid;
}

std::vector<std::vector<int>> generate_maze_py(int n, const std::string &strategy, double hybrid_prob = 0.7) {
    Strategy s = STR_NEWEST;
    if (strategy == "newest") s = STR_NEWEST;
    else if (strategy == "random") s = STR_RANDOM;
    else if (strategy == "hybrid") s = STR_HYBRID;
    else {
        std::string low = strategy;
        std::transform(low.begin(), low.end(), low.begin(), ::tolower);
        if (low == "r") s = STR_RANDOM;
        else if (low == "h") s = STR_HYBRID;
        else s = STR_NEWEST;
    }
    return generate_maze_cpp(n, s, hybrid_prob);
}

// Bindings
PYBIND11_MODULE(maze_generator, m) {
    m.doc() = "Growing Tree maze generator (returns 2D grid with 0=path,1=wall,2=start,3=end)";

    m.def("generate_maze", &generate_maze_py,
          py::arg("n") = 21,
          py::arg("strategy") = "newest",
          py::arg("hybrid_prob") = 0.7,
          R"pbdoc(
            generate_maze(n: int = 21, strategy: str = "newest", hybrid_prob: float = 0.7) -> List[List[int]]

            n: size of the grid (will be made odd if even)
            strategy: "newest", "random", or "hybrid"
            hybrid_prob: probability to pick newest in hybrid mode
          )pbdoc");
}
