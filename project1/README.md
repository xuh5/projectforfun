# Project For Fun

A full-stack project with Next.js frontend and Python backend.

## Tech Stack

- **Frontend**: Next.js 14 with TypeScript
- **Backend**: Python with FastAPI

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

6. Run the server:
```bash
uvicorn main:app --reload --port 8000
```

The backend API will be available at `http://localhost:8000`
API documentation will be available at `http://localhost:8000/docs`

## Development

- Frontend runs on `http://localhost:3000`
- Backend runs on `http://localhost:8000`
- API requests from frontend to `/api/*` are automatically proxied to the backend

## License

Add license information here.

