# Settings 管理器 - 统一管理配置

import json
import sys
from pathlib import Path
from dataclasses import dataclass


# 支持的模型列表
AVAILABLE_MODELS = [
    {"group": "OpenAI", "models": [
        {"value": "gpt-4o", "name": "GPT-4o"},
        {"value": "gpt-4o-mini", "name": "GPT-4o Mini"},
        {"value": "gpt-4-turbo", "name": "GPT-4 Turbo"},
        {"value": "gpt-3.5-turbo", "name": "GPT-3.5 Turbo"},
    ]},
    {"group": "Claude", "models": [
        {"value": "claude-sonnet-4-20250514", "name": "Claude Sonnet 4"},
        {"value": "claude-3-5-sonnet-20241022", "name": "Claude 3.5 Sonnet"},
        {"value": "claude-3-5-haiku-20241022", "name": "Claude 3.5 Haiku"},
        {"value": "claude-3-opus-20240229", "name": "Claude 3 Opus"},
    ]},
    {"group": "Gemini", "models": [
        {"value": "gemini-pro", "name": "Gemini Pro"},
        {"value": "gemini-1.5-pro", "name": "Gemini 1.5 Pro"},
        {"value": "gemini-1.5-flash", "name": "Gemini 1.5 Flash"},
    ]},
    {"group": "Grok", "models": [
        {"value": "grok-beta", "name": "Grok Beta"},
        {"value": "grok-2", "name": "Grok 2"},
    ]},
]


def get_available_models() -> list:
    """获取可用的模型列表"""
    return AVAILABLE_MODELS


def get_data_dir() -> Path:
    """获取数据目录（兼容打包后的 exe）"""
    if getattr(sys, 'frozen', False):
        # 打包后：使用 exe 所在目录
        return Path(sys.executable).parent
    else:
        # 开发时：使用项目根目录
        return Path(__file__).parent.parent


SETTINGS_FILE = get_data_dir() / "settings.json"


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
