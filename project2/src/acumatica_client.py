import contextlib
import httpx
from dataclasses import dataclass
from typing import Any, Dict, Optional
import os
from dotenv import load_dotenv
from pathlib import Path


@dataclass
class AcumaticaConfig:
    base_url: str
    username: str
    password: str
    tenant: Optional[str] = None
    branch: Optional[str] = None
    locale: Optional[str] = None


class AcumaticaClient:
    """
    Minimal Acumatica REST client using cookie-based auth (/entity/auth/login).
    Works across many versions; if your instance enforces OAuth2, we can extend this.
    """

    def __init__(self, config: AcumaticaConfig):
        if config.base_url.endswith("/"):
            self.base_url = config.base_url[:-1]
        else:
            self.base_url = config.base_url
        self.config = config
        self._client = httpx.Client(timeout=30.0, follow_redirects=True)
        self._logged_in = False

    def login(self) -> None:
        payload: Dict[str, Any] = {
            "name": self.config.username,
            "password": self.config.password,
        }
        if self.config.tenant:
            payload["tenant"] = self.config.tenant
        if self.config.branch:
            payload["branch"] = self.config.branch
        if self.config.locale:
            payload["locale"] = self.config.locale

        resp = self._client.post(f"{self.base_url}/entity/auth/login", json=payload)
        resp.raise_for_status()
        self._logged_in = True

    def logout(self) -> None:
        if not self._logged_in:
            return
        with contextlib.suppress(Exception):
            self._client.post(f"{self.base_url}/entity/auth/logout")
        self._logged_in = False

    def get(self, path: str, params: Optional[Dict[str, Any]] = None) -> httpx.Response:
        if not self._logged_in:
            raise RuntimeError("Not logged in. Call login() first.")
        url = f"{self.base_url}{path if path.startswith('/') else '/' + path}"
        resp = self._client.get(url, params=params)
        resp.raise_for_status()
        return resp

    def close(self) -> None:
        self.logout()
        self._client.close()

    def __enter__(self) -> "AcumaticaClient":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()


def load_config_from_env() -> AcumaticaConfig:
    # Always load .env from the project root (one level above src/)
    env_path = Path(__file__).resolve().parents[1] / ".env"
    load_dotenv(dotenv_path=env_path)
    base_url = os.getenv("ACUMATICA_BASE_URL", "").strip()
    username = os.getenv("ACUMATICA_USERNAME", "").strip()
    password = os.getenv("ACUMATICA_PASSWORD", "").strip()
    tenant = os.getenv("ACUMATICA_TENANT", "") or None
    branch = os.getenv("ACUMATICA_BRANCH", "") or None
    locale = os.getenv("ACUMATICA_LOCALE", "") or None
    if not base_url or not username or not password:
        raise ValueError("ACUMATICA_BASE_URL, ACUMATICA_USERNAME, and ACUMATICA_PASSWORD are required in .env")
    return AcumaticaConfig(
        base_url=base_url,
        username=username,
        password=password,
        tenant=tenant,
        branch=branch,
        locale=locale,
    )


