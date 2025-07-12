FROM python:3.12-slim
WORKDIR /app

# Install build tools and MySQL client libraries
RUN apt-get update \
    && apt-get install -y gcc default-libmysqlclient-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy application code
COPY . /app

# Install python dependencies
RUN pip install --no-cache-dir \
        Flask==2.2.5 \
        SQLAlchemy \
        mysqlclient

# Default database connection
ENV CH_DBURL mysql://chuser:chpass@db/ch?connect_timeout=1

EXPOSE 5000
CMD ["python", "flaskapp/app.py"]
