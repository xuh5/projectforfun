# Project For Fun

A full-stack project with Next.js frontend and Python backend.

## Tech Stack

- **Frontend**: Next.js 14 with TypeScript
- **Backend**: Python with FastAPI

## Quick Start

Get the application running in just 2 steps:

### 1. Install Dependencies

**Backend:**
```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate

pip install -r requirements.txt

# Seed the database (first time only)
python scripts/seed_db.py

cd ..
```

**Frontend:**
```bash
cd frontend
npm install
cd ..
```

### 2. Start Servers

Open two terminal windows and run:

**Terminal 1 - Backend:**
```bash
# Windows
start-backend.bat

# macOS/Linux
chmod +x start-backend.sh
./start-backend.sh
```

**Terminal 2 - Frontend:**
```bash
# Windows
start-frontend.bat

# macOS/Linux
chmod +x start-frontend.sh
./start-frontend.sh
```

That's it! The application will be available at:
- Frontend: `http://localhost:3000`
- Backend API: `http://localhost:8000`
- API Docs: `http://localhost:8000/docs`

### First Time Setup

**Database Setup:**
- The database is automatically initialized on first backend startup
- To populate with sample data, run: `cd backend && python scripts/seed_db.py`
- To reset the database: `cd backend && python scripts/reset_db.py`

## Project Structure

```
.
├── frontend/          # Next.js application
├── backend/           # Python FastAPI application
├── .gitignore
├── .editorconfig
└── README.md
```

## Getting Started

### Prerequisites

- Node.js 18+ and npm/yarn
- Python 3.8+

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
# or
yarn install
```

3. Run the development server:
```bash
npm run dev
# or
yarn dev
```

The frontend will be available at `http://localhost:3000`

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment:
```bash
python -m venv venv
```

3. Activate the virtual environment:
```bash
# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

4. Install dependencies:
```bash
pip install -r requirements.txt
```

5. Set up environment variables:

**Backend** - Create a `.env` file in the `backend/` directory with:
```env
SUPABASE_URL=your_supabase_project_url
SUPABASE_ANON_KEY=your_supabase_anon_key
# Optional: For admin operations
SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key
```

**Frontend** - Create a `.env.local` file in the `frontend/` directory with:
```env
NEXT_PUBLIC_SUPABASE_URL=your_supabase_project_url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key
```

You can find these values in your Supabase project settings under API.

6. Seed the database (first time only):
```bash
python scripts/seed_db.py
```

7. Run the server:
```bash
# From project1/ directory
uvicorn backend.main:app --reload --port 8000

# Or use the startup script from project1/ directory
# Windows: start-backend.bat
# macOS/Linux: ./start-backend.sh
```

The backend API will be available at `http://localhost:8000`
API documentation will be available at `http://localhost:8000/docs`

## Authentication

This project uses Supabase for authentication with Google OAuth (Gmail login).

### Setup

1. **Supabase Configuration:**
   - Set up a Supabase project at https://supabase.com
   - Enable Google OAuth provider in Authentication > Providers
   - Configure your Google OAuth credentials in Supabase
   - Add your redirect URL: `http://localhost:3000/auth/callback`

2. **Environment Variables:**
   - Add Supabase credentials to both backend and frontend `.env` files (see setup instructions above)

3. **Usage:**
   - Users can sign in via the "Sign In" button in the navigation
   - After authentication, API requests automatically include the auth token
   - The backend validates tokens using the `get_current_user` dependency

### Protecting Backend Endpoints

To protect an endpoint, add the `get_current_user` dependency:

```python
from backend.auth import get_current_user

@app.post("/api/protected")
async def protected_route(user: dict = Depends(get_current_user)):
    return {"user_id": user["id"], "email": user["email"]}
```

## Development

- Frontend runs on `http://localhost:3000`
- Backend runs on `http://localhost:8000`
- API requests from frontend to `/api/*` are automatically proxied to the backend
- Authentication tokens are automatically included in API requests when users are logged in

## License

Add license information here.

