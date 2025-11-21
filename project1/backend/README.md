# Backend (Python)

This is the Python backend using FastAPI with Supabase PostgreSQL and Authentication.

## Prerequisites

- Python 3.10+
- A Supabase project (sign up at [supabase.com](https://supabase.com))

## Supabase Setup

1. Create a new project at [supabase.com](https://supabase.com)
2. Go to your project settings → Database
3. Find your database connection details:
   - Database host (e.g., `xxxxx.supabase.co`)
   - Database password (set during project creation)
   - Database port (default: 5432)
   - Database name (default: `postgres`)
4. Go to Settings → API to find:
   - Project URL (e.g., `https://xxxxx.supabase.co`)
   - `anon` public key (for client-side authentication)
   - `service_role` key (optional, for admin operations - keep secret!)

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

5. Configure your `.env` file with Supabase credentials:
   - Set `DATABASE_URL` with your Supabase PostgreSQL connection string, OR
   - Set individual Supabase database variables (`SUPABASE_DB_HOST`, `SUPABASE_DB_PASSWORD`, etc.)
   - Set `SUPABASE_URL` and `SUPABASE_ANON_KEY` for authentication

   Example `.env`:
   ```env
   DATABASE_URL=postgresql://postgres:[YOUR-PASSWORD]@[YOUR-PROJECT-REF].supabase.co:5432/postgres
   SUPABASE_URL=https://[YOUR-PROJECT-REF].supabase.co
   SUPABASE_ANON_KEY=[YOUR-ANON-KEY]
   ```

6. Initialize the database (creates tables):
   - The database tables will be created automatically on first startup
   - If Supabase credentials are not configured, the app will automatically fall back to SQLite for local development
   - For production, consider using Alembic migrations instead

7. Run the server (from the project root or `backend` directory):
```bash
uvicorn backend.main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`

API documentation will be available at `http://localhost:8000/docs`

## Database Migrations (Alembic)

The project uses Alembic for database migrations. To initialize Alembic (if not already done):

```bash
# From the backend directory
alembic init alembic
```

Then configure `alembic/env.py` to use your database URL from environment variables.

To create a new migration:
```bash
alembic revision --autogenerate -m "Description of changes"
```

To apply migrations:
```bash
alembic upgrade head
```

## Authentication

The backend includes Supabase Authentication integration. JWT tokens are verified using the `get_current_user` dependency.

### Using Authentication in Endpoints

To protect an endpoint, add the authentication dependency:

```python
from backend.auth import get_current_user

@app.get("/api/protected")
async def protected_route(user: dict = Depends(get_current_user)):
    return {"user_id": user["sub"], "email": user.get("email")}
```

### Getting Authentication Tokens

Users authenticate through Supabase Auth (typically via the frontend). The frontend should:
1. Sign up/sign in users using Supabase Auth
2. Include the JWT token in the `Authorization: Bearer <token>` header for protected endpoints

See the Supabase documentation for frontend authentication setup.

## Architecture Overview

- **Domain layer** (`backend/domain`): Immutable dataclasses describing companies, relationships, and graph snapshots.
- **Repositories** (`backend/repositories`): Data providers using SQLAlchemy with Supabase PostgreSQL. The `DatabaseGraphRepository` provides persistent storage.
- **Services** (`backend/services`): Orchestrate repository calls and expose high-level operations the API consumes.
- **API** (`backend/main.py`, `backend/api/schemas.py`): FastAPI routes and response schemas wired through dependency injection in `backend/dependencies.py`.
- **Authentication** (`backend/auth`): Supabase JWT token verification and user authentication dependencies.

The database uses Supabase PostgreSQL with SQLAlchemy ORM. If Supabase credentials are not configured, the app automatically falls back to SQLite for local development. Authentication is handled via Supabase Auth with JWT tokens.

## Testing

Install the optional testing dependencies and run `pytest` from the `backend` directory:

```bash
pip install pytest httpx
pytest
```

