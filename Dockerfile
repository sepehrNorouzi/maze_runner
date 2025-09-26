FROM python:3.12-alpine AS builder

RUN apk update && apk add --no-cache \
    g++ \
    cmake \
    make \
    git \
    musl-dev \
    python3-dev

WORKDIR /build

COPY CMakeLists.txt maze_generator.cpp ./

RUN cmake -S . -B build -DPython_EXECUTABLE=/usr/local/bin/python3.12
RUN cmake --build build --config Release -j$(nproc)

FROM python:3.12-alpine

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apk update && apk add --no-cache \
    gcc \
    musl-dev \
    postgresql-dev \
    python3-dev \
    libffi-dev \
    gettext \
    libstdc++ \
    && rm -rf /var/cache/apk/*


WORKDIR /app

COPY --from=builder /build/build/*.so /tmp/

COPY . .

RUN mkdir -p /app/maze_runner/cpp_build && \
    mv /tmp/*.so /app/maze_runner/cpp_build/maze_generator.so && \
    echo "from .maze_generator import *" > /app/maze_runner/cpp_build/__init__.py

RUN mkdir -p /app/static /app/uploads

RUN python manage.py collectstatic --noinput || true


RUN pip install --upgrade pip setuptools wheel
RUN pip install -r requirements.txt

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
