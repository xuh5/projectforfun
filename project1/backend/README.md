# Backend (Python)

This is the Python backend using FastAPI.

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
```

2. Activate the virtual environment:
```bash
# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Copy `env.example` to `.env` and configure:
```bash
# Windows
copy env.example .env

# macOS/Linux
cp env.example .env
```

5. Run the server (from the project root or `backend` directory):
```bash
uvicorn backend.main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`

API documentation will be available at `http://localhost:8000/docs`

## Architecture Overview

- **Domain layer** (`backend/domain`): Immutable dataclasses describing companies, relationships, and graph snapshots.
- **Repositories** (`backend/repositories`): Data providers. The default `MockGraphRepository` generates deterministic synthetic data and can be swapped for a real data source.
- **Services** (`backend/services`): Orchestrate repository calls and expose high-level operations the API consumes.
- **API** (`backend/main.py`, `backend/api/schemas.py`): FastAPI routes and response schemas wired through dependency injection in `backend/dependencies.py`.

To replace the mock data source, implement a new repository satisfying `GraphRepositoryProtocol` and update `get_graph_repository()` in `backend/dependencies.py` to return it. The service and API layers will continue working unchanged.

## Testing

Install the optional testing dependencies and run `pytest` from the `backend` directory:

```bash
pip install pytest httpx
pytest
```

