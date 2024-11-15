FROM python:3.11-slim

WORKDIR /app

COPY . .

RUN apt-get update && apt-get install -y \
    libpq-dev gcc --no-install-recommends && \
    rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip && pip install -r requirements.txt

RUN python manage.py collectstatic --noinput

CMD ["gunicorn", "LINE_BOT.wsgi:application", "--bind", "0.0.0.0:8000"]
