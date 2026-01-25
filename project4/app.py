"""
TextTool - GUI 入口
使用 PyWebView 创建桌面窗口
"""

import webview
import keyboard
import json
import time
from threading import Thread

from core import (
    get_selected_text,
    call_api,
    build_prompt,
    get_history,
    get_settings,
    update_settings,
    Settings,
)
from core.prompt_builder import get_option_names

# 全局 window 引用
_window = None


class Api:
    """暴露给前端的 API"""
    
    def get_options(self):
        """获取所有选项"""
        return [{"key": k, "name": n} for k, n in get_option_names()]
    
    def process_text(self, text: str, option_key: str):
        """处理文字"""
        prompt_data = build_prompt(text, option_key)
        if not prompt_data:
            return {"content": "Invalid option", "valid": False}
        
        raw_response, parse_result = call_api(prompt_data)
        
        history = get_history()
        history.add(
            input_text=text,
            option=prompt_data["config"].name,
            prompt=prompt_data["user"],
            result=raw_response,
            valid=parse_result.success
        )
        
        return {
            "content": raw_response,
            "valid": parse_result.success,
            "metadata": parse_result.metadata
        }
    
    def get_history(self):
        """获取历史记录"""
        history = get_history()
        records = history.get_all()
        return [
            {
                "id": r.id,
                "timestamp": r.timestamp,
                "input_text": r.input_text,
                "option": r.option,
                "result": r.result,
                "valid": r.valid
            }
            for r in records
        ]
    
    def get_record(self, record_id: int):
        """获取单条记录"""
        history = get_history()
        for r in history.records:
            if r.id == record_id:
                return {
                    "id": r.id,
                    "input_text": r.input_text,
                    "option": r.option,
                    "result": r.result,
                    "valid": r.valid
                }
        return None
    
    def get_settings(self):
        """获取设置"""
        s = get_settings()
        return {
            "api_url": s.api_url,
            "api_key": s.api_key,
            "model": s.model,
            "timeout": s.timeout,
            "mock_mode": s.mock_mode
        }
    
    def save_settings(self, data: dict):
        """保存设置"""
        update_settings(
            api_url=data.get("api_url", ""),
            api_key=data.get("api_key", ""),
            model=data.get("model", "gpt-3.5-turbo"),
            timeout=data.get("timeout", 30),
            mock_mode=data.get("mock_mode", True)
        )
        return True
    
    def capture_text(self):
        """手动捕获选中文字（前端调用）"""
        text = get_selected_text()
        return text if text and text.strip() else ""


def on_hotkey():
    """全局热键触发"""
    global _window
    if not _window:
        return
    
    print("[Hotkey] Ctrl+Q triggered")
    
    # 获取选中的文字
    text = get_selected_text()
    print(f"[Hotkey] Captured text: {text[:50] if text else 'None'}...")
    
    # 显示窗口并发送文字
    _window.show()
    _window.restore()
    
    if text and text.strip():
        _window.evaluate_js(f'setInputText({json.dumps(text)})')


def hotkey_listener():
    """热键监听线程"""
    print("[Hotkey] Registering Ctrl+Q...")
    keyboard.add_hotkey('ctrl+q', on_hotkey, suppress=False)
    print("[Hotkey] Listener started, waiting...")
    keyboard.wait()


def main():
    global _window
    
    # 先启动热键监听线程
    hotkey_thread = Thread(target=hotkey_listener, daemon=True)
    hotkey_thread.start()
    
    # 等待热键注册完成
    time.sleep(0.5)
    
    # 创建 API 实例
    api = Api()
    
    # 创建窗口
    _window = webview.create_window(
        title='TextTool',
        url='ui/index.html',
        width=900,
        height=520,
        resizable=True,
        min_size=(800, 400),
        js_api=api
    )
    
    print("[App] Starting webview...")
    
    # 启动 webview（这会阻塞主线程）
    webview.start(debug=True)


if __name__ == '__main__':
    main()
