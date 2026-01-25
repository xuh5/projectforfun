import time
import pyperclip
import keyboard


def get_selected_text() -> str:
    """模拟 Ctrl+C 获取当前选中的文字"""
    # 保存原剪贴板内容
    original = pyperclip.paste()
    
    # 模拟 Ctrl+C
    keyboard.send("ctrl+c")
    time.sleep(0.1)  # 等待复制完成
    
    # 读取选中的文字
    selected = pyperclip.paste()
    
    # 恢复原剪贴板（可选）
    # pyperclip.copy(original)
    
    return selected if selected != original else ""
