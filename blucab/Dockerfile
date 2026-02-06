# Base image: Debian with current python 3 version installed
FROM python:3.12

WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY requirements.txt .

# Install required packages
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Process files
RUN ["chmod", "+x", "./entrypoint.sh"]


EXPOSE 8000

# Default command on container startup
ENTRYPOINT ["./entrypoint.sh"]

HEALTHCHECK CMD curl --fail http://localhost:8000/ || exit 1

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
