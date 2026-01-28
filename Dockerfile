FROM python:3.12-slim

WORKDIR /app

# Install dependencies first for better layer caching
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy app source
COPY . ./

ENV PYTHONUNBUFFERED=1

EXPOSE 5002

# Use gunicorn in container
CMD ["gunicorn", "-w", "2", "-b", "0.0.0.0:5002", "app:app"]
