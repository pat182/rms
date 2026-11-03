# RMS Backend

Restaurant Management System backend built with FastAPI, SQLAlchemy async, and PostgreSQL.

## Requirements

- Python 3.15
- PostgreSQL
- FastAPI 0.162.0
- uv

For the Docker development setup, install Docker Desktop instead of installing Python and uv locally.

## Run locally

1. Copy `.env.example` to `.env` and set the PostgreSQL connection values:

   ```text
   DB_HOST=localhost
   DB_PORT=5432
   DB_NAME=rms
   DB_USER=postgres
   DB_PASSWORD=your-local-postgres-password
   ```

   Create the database named in `DB_NAME` before continuing. Update other settings as needed for your environment. Do not use the example secret key in a deployed environment.

2. Install the project dependencies:

   ```powershell
   uv sync
   ```

3. Apply database migrations:

   ```powershell
   uv run alembic upgrade head
   ```

4. Start the development server:

   ```powershell
   uv run uvicorn app.main:app --reload
   ```

The API is available at <http://localhost:8000>. Interactive API documentation is at <http://localhost:8000/docs>.

## Run with Docker Compose

Copy `.env.example` to `.env`, configure the database settings, and ensure the database is reachable from Docker. The Compose configuration connects to a database on the host machine using `host.docker.internal`.

Start the development configuration:

```powershell
docker compose -f compose.yaml -f compose.dev.yaml up --build
```

The development container applies migrations on startup and runs the API with reload enabled. Source files, migrations, and uploads are mounted into the container. Open <http://localhost:8000/docs> for the API documentation.

Stop the containers with `Ctrl+C`, or run:

```powershell
docker compose -f compose.yaml -f compose.dev.yaml down
```

## Run tests

With the project environment installed, run:

```powershell
uv run pytest tests/ -v
```
