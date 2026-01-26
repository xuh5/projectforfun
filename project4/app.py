"""
Fork CodeReview - GUI 入口
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
    get_available_models,
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
        """处理单个文字（兼容旧调用）"""
        result = self.process_batch(text, [option_key])
        if result["results"]:
            return result["results"][0]
        return {"content": "Invalid option", "valid": False}
    
    def process_batch(self, text: str, option_keys: list):
        """批量处理多个 action"""
        results = []
        
        for option_key in option_keys:
            prompt_data = build_prompt(text, option_key)
            if not prompt_data:
                results.append({
                    "option": option_key,
                    "content": "Invalid option",
                    "valid": False
                })
                continue
            
            raw_response, parse_result = call_api(prompt_data)
            results.append({
                "option": prompt_data["config"].name,
                "content": raw_response,
                "valid": parse_result.success,
                "metadata": parse_result.metadata
            })
        
        # 保存到历史记录
        history = get_history()
        history.add(
            input_text=text,
            options=option_keys,
            results=results
        )
        
        return {"results": results}
    
    def get_history(self):
        """获取历史记录"""
        history = get_history()
        records = history.get_all()
        return [
            {
                "id": r.id,
                "timestamp": r.timestamp,
                "input_text": r.input_text,
                "options": r.options,
                "results": r.results,
                "all_valid": r.all_valid,
                # 兼容旧格式
                "option": r.option,
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
                    "options": r.options,
                    "results": r.results,
                    "all_valid": r.all_valid,
                    # 兼容旧格式
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
    
    def get_models(self):
        """获取可用的模型列表"""
        return get_available_models()
    
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
    
    def delete_record(self, record_id: int):
        """删除单条历史记录"""
        history = get_history()
        return history.delete(record_id)
    
    def clear_history(self):
        """清空所有历史记录"""
        history = get_history()
        history.clear()
        return True


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
        title='Fork CodeReview',
        url='ui/index.html',
        width=1100,
        height=750,
        resizable=True,
        min_size=(900, 750),
        js_api=api
    )
    
    print("[App] Starting webview...")
    
    # 启动 webview（这会阻塞主线程）
    webview.start(debug=True)


if __name__ == '__main__':
    main()
