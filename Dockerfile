FROM python:3.11-slim

WORKDIR /app

# Install ytmusicapi
RUN pip install --no-cache-dir ytmusicapi

# Copy the application script
COPY add.py .

# Use ENTRYPOINT to allow passing arguments to add.py
ENTRYPOINT ["python", "add.py"]
