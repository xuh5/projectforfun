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

5. Copy `env.example` to `.env` and configure if needed:
```bash
# Windows
copy env.example .env

# macOS/Linux
cp env.example .env
```

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

## Development

- Frontend runs on `http://localhost:3000`
- Backend runs on `http://localhost:8000`
- API requests from frontend to `/api/*` are automatically proxied to the backend

## License

Add license information here.

