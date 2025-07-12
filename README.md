# JMeter Practice API

This FastAPI application exposes simple CRUD endpoints that are convenient for load-testing with tools such as JMeter. It now persists data using a small SQLite database and emits logs for each request. The app is ready for production-style deployments and can handle high concurrency when run with multiple workers.

## Setup

Install the dependencies:

```bash
pip install -r requirements.txt
```

## Running

Launch the app with Uvicorn. Use the `--workers` option to allow several processes to serve requests concurrently. The following example starts four workers, which is generally sufficient for around 100 concurrent requests during JMeter practice:

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

The application stores items in a local SQLite database named `items.db`. The first five items are seeded automatically and cannot be modified or removed. Logging is enabled by default and writes informational messages to the console for each request.

## Available Endpoints

- `POST /login` – dummy authentication returning a token
- `GET /items` – list all items
- `POST /items` – create an item
- `GET /items/{item_id}` – retrieve one item
- `PUT /items/{item_id}` – update an item
- `DELETE /items/{item_id}` – delete an item
- `POST /upload` – upload a file and get its size
- `GET /slow` – simulate a slow request using the `delay` parameter

A root endpoint `/` is also provided to verify the server is running.

