FROM python:3.12-alpine
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apk update \
    && apk add gcc musl-dev postgresql-dev python3-dev libffi-dev gettext


WORKDIR /app


# install dependencies
COPY . .
RUN pip install --upgrade pip setuptools wheel
RUN pip install -r requirements.txt

CMD ["python", "manage.py", "runserver"]
