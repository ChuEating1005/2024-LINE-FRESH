FROM python:3.9
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
ENV PYTHONUNBUFFERED=1
CMD python manage.py migrate && gunicorn backend.wsgi:application --bind 0.0.0.0:$PORT
