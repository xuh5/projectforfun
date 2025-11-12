Project 2 — Acumatica REST API Client (Python)

This project shows how to connect to Acumatica from a local Python script using the contract-based REST API with cookie login. It logs in, fetches a few records, and logs out.

Prerequisites

- Python 3.10+
- Acumatica instance URL and credentials

Setup

1) Create and activate a virtual environment:

Windows (PowerShell)

```powershell
cd "C:\Users\haichen\Desktop\Project For Fun\project2"
python -m venv venv
.\venv\Scripts\Activate.ps1
```

macOS/Linux

```bash
cd "C:/Users/haichen/Desktop/Project For Fun/project2"
python -m venv venv
source venv/bin/activate
```

2) Install dependencies:

```bash
pip install -r requirements.txt
```

3) Configure environment:

Copy `.env.example` to `.env` and fill in your values.

```bash
# Windows
copy .env.example .env

# macOS/Linux
cp .env.example .env
```

4) Run the demo:

```bash
python -m src.demo
```

Expected behavior

- The script logs in via `POST /entity/auth/login`.
- Fetches first 5 customers from `/entity/Default/6.00.001/Customer?$top=5` (adjust version/endpoint as needed).
- Prints the JSON response.
- Logs out via `POST /entity/auth/logout`.

Notes

- If your instance requires OAuth2/OpenID Connect, we can extend the client to use OAuth (client credentials or authorization code) instead of cookie auth.
- The path segment `Default/6.00.001` may vary with your version/custom endpoints. Replace with your site’s endpoint and version.


