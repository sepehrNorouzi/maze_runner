# Maze Runner 🌀

A Django-based maze generation and solving application with high-performance C++ backend for maze algorithms. This project features an intuitive admin interface for creating, managing, and solving mazes using various generation strategies.

## 🎯 Features

- **High-Performance Maze Generation**: C++ implementation with Python bindings for optimal performance
- **Multiple Generation Algorithms**: 
  - **Newest**: Depth-first search behavior (creates long, winding passages)
  - **Random**: Produces more branching, complex mazes
  - **Hybrid**: Combines both strategies with configurable probability
- **Automatic Maze Solving**: BFS-based pathfinding to find the shortest solution
- **Efficient Storage**: Binary compression for storing large mazes (3-bit encoding per cell)
- **Visual Admin Interface**: Interactive maze preview and management
- **RESTful API**: JWT-authenticated endpoints for programmatic access
- **Caching Support**: Redis integration for improved performance

## 🛠️ Technology Stack

- **Backend**: Django 5.2.6 + Python 3.12
- **Database**: PostgreSQL
- **Cache**: Redis
- **C++ Extension**: pybind11 for high-performance maze algorithms
- **Authentication**: JWT (via djangorestframework-simplejwt)
- **Containerization**: Docker & Docker Compose

## 📋 Prerequisites

- Python 3.12+
- PostgreSQL 14+
- Redis 6+
- CMake 3.14+ (for building C++ extensions)
- C++ compiler with C++17 support

## 🚀 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/maze_runner.git
cd maze_runner
```

### 2. Set Up Python Environment

```bash
python3.12 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

### 3. Build C++ Extension

The project includes a high-performance C++ maze generator. Build it using:

```bash
# Configure CMake (using Python 3.12)
cmake -S . -B build -DPython_EXECUTABLE=$(which python3.12)

# Build the extension
cmake --build build --config Release -j

# The compiled module will be available in the build directory
# Copy it to the project's module directory
cp build/maze_generator.*.so maze_runner/cpp_build/
```

### 4. Configure Environment Variables

Copy the sample environment file and configure it:

```bash
cp env.sample .env
```

Edit `.env` with your configuration:

```env
# Base ENV
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
PROJECT_NAME=maze_runner

# Database
POSTGRES_DB=maze_runner_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your-password
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
CONN_MAX_AGE=60

# Redis
REDIS_URI=redis://localhost:6379/1
REDIS_TIMEOUT=3600
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=
REDIS_DB=1
REDIS_KEY_PREFIX=maze_runner

# JWT
ACCESS_TOKEN_LIFETIME=60  # minutes
REFRESH_TOKEN_LIFETIME=7   # days

# Static Files
STATIC_ROOT=static
MEDIA_ROOT=uploads
MEDIA_URL=media/
```

### 5. Database Setup

```bash
# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Collect static files (for production)
python manage.py collectstatic
```

### 6. Run the Development Server

```bash
python manage.py runserver
```

Access the application at `http://localhost:8000`

## 🐳 Docker Deployment

### Using Docker Compose

```bash
# Build and start containers
docker-compose up -d

# Run migrations
docker-compose exec web python manage.py migrate

# Create superuser
docker-compose exec web python manage.py createsuperuser
```

## 📖 Usage

### Admin Interface

1. Navigate to `http://localhost:8000/admin`
2. Login with your superuser credentials
3. Access the Maze section to:
   - Generate new mazes with custom parameters
   - View maze previews with color-coded cells
   - Solve mazes automatically
   - Export maze data as JSON

### Generating a Maze

1. Click "Generate Maze" in the Maze admin
2. Configure parameters:
   - **Algorithm**: Choose generation strategy (Newest/Random/Hybrid)
   - **Width/Height**: Set maze dimensions (10-500 cells)
   - **Hybrid Probability**: For hybrid algorithm (0.0-1.0)
3. Click "Generate Maze"

### Maze Cell Values

- `0`: Empty path (white)
- `1`: Wall (black)
- `2`: Start position (green)
- `3`: Finish position (red)
- `4`: Solution path (amber) - appears after solving

### API Endpoints

```bash
# Authentication
POST /auth/jwt/create/        # Login
POST /auth/jwt/refresh/       # Refresh token
POST /auth/jwt/verify/        # Verify token

# Maze Operations
GET  /maze/                   # List mazes
POST /maze/create/            # Create new maze
GET  /maze/{id}/              # Get maze details
POST /maze/{id}/solve/        # Solve maze
```

## 🏗️ Project Structure

```
maze_runner/
├── maze/                     # Maze app
│   ├── models.py            # Maze model with binary storage
│   ├── admin.py             # Admin interface customization
│   ├── utils.py             # Compression utilities
│   ├── maze_render.py       # HTML maze visualization
│   └── forms.py             # Maze generation forms
├── maze_generator.cpp       # C++ maze generation/solving
├── common/                  # Shared models and utilities
├── user/                    # Custom user model
├── maze_runner/            # Project settings
│   ├── settings.py         # Django settings
│   └── cpp_build/          # C++ extension module location
├── templates/              # Custom admin templates
├── CMakeLists.txt         # CMake configuration
├── requirements.txt       # Python dependencies
└── Dockerfile            # Container configuration
```

## ⚡ Performance Considerations

- **Binary Storage**: Mazes are stored using 3-bit encoding per cell, reducing storage by ~62%
- **C++ Generation**: Core algorithms implemented in C++ for 10-100x speedup
- **Redis Caching**: Frequently accessed configurations cached
- **Batch Operations**: Admin actions support bulk maze operations

## 🧪 Testing

```bash
# Run Django tests
python manage.py test

# Test C++ extension
python -c "from maze_runner.cpp_build import maze_generator; print(maze_generator.generate_maze(21, 'newest'))"
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🐛 Known Issues

- Very large mazes (>500x500) may take several seconds to generate
- Binary storage format is not compatible between different architectures
- Docker build requires manual C++ extension compilation

## 🚧 Roadmap

- [ ] Add more maze generation algorithms (Kruskal's, Prim's, etc.)
- [ ] Implement A* pathfinding for solving
- [ ] Add maze difficulty analysis
- [ ] Create public API for maze generation
- [ ] Add WebSocket support for real-time generation
- [ ] Implement maze export formats (PNG, SVG, PDF)

## 💡 Tips

- For best visual results, keep maze dimensions under 200x200
- Hybrid algorithm with 0.7 probability creates balanced mazes
- Use the bulk solve action for processing multiple mazes efficiently
- The admin preview supports zooming/scrolling for large mazes

## 📧 Support

For issues, questions, or suggestions, please open an issue on GitHub or contact the maintainers.
