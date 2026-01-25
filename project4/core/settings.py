# Settings 管理器 - 统一管理配置

import json
from pathlib import Path
from dataclasses import dataclass

SETTINGS_FILE = Path(__file__).parent.parent / "settings.json"


@dataclass
class Settings:
    """应用配置"""
    api_url: str = ""
    api_key: str = ""
    model: str = "gpt-3.5-turbo"
    timeout: int = 30
    mock_mode: bool = True  # True 使用模拟数据，False 调用真实 API


_settings: Settings | None = None


def get_settings() -> Settings:
    """获取当前设置（单例）"""
    global _settings
    if _settings is None:
        _settings = load_settings()
    return _settings


def load_settings() -> Settings:
    """从文件加载设置"""
    if SETTINGS_FILE.exists():
        try:
            data = json.loads(SETTINGS_FILE.read_text(encoding='utf-8'))
            return Settings(
                api_url=data.get("api_url", ""),
                api_key=data.get("api_key", ""),
                model=data.get("model", "gpt-3.5-turbo"),
                timeout=data.get("timeout", 30),
                mock_mode=data.get("mock_mode", True)
            )
        except Exception:
            pass
    return Settings()


def save_settings(settings: Settings) -> bool:
    """保存设置到文件"""
    global _settings
    try:
        data = {
            "api_url": settings.api_url,
            "api_key": settings.api_key,
            "model": settings.model,
            "timeout": settings.timeout,
            "mock_mode": settings.mock_mode
        }
        SETTINGS_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding='utf-8')
        _settings = settings
        return True
    except Exception:
        return False


def update_settings(**kwargs) -> Settings:
    """更新部分设置"""
    settings = get_settings()
    for key, value in kwargs.items():
        if hasattr(settings, key):
            setattr(settings, key, value)
    save_settings(settings)
    return settings
