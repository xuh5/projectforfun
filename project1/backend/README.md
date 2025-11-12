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

5. Run the server:
```bash
uvicorn main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`

API documentation will be available at `http://localhost:8000/docs`

