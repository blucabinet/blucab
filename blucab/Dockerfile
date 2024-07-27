# Base image: Debian with current python 3 version installed
FROM python:3

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

# Default command on container startup
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
