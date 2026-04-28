FROM python:3.12-slim

WORKDIR /code

# Install system dependencies for psycopg2
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Fix Windows line endings and set permissions
RUN apt-get update && apt-get install -y sed && \
    sed -i 's/\r$//' entrypoint.sh && \
    chmod +x entrypoint.sh

CMD ["./entrypoint.sh"]
