# Cogent House Docker Setup

This repository includes a small example Flask application in `flaskapp/`.
The provided Docker configuration launches the app using **Python 3** and
runs a MySQL server alongside it via Docker Compose.

## Usage

1. Build and start the services:

   ```bash
   docker compose up --build
   ```

   The Flask application will be available on [http://localhost:5000](http://localhost:5000).

2. The database credentials are defined in `docker-compose.yml` and the
   Flask container uses the `CH_DBURL` environment variable to connect.

3. To stop the containers:

   ```bash
   docker compose down
   ```

The MySQL data is stored in a named Docker volume `dbdata` so that data is
preserved between restarts.
