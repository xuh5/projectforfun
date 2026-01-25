import keyboard
from config import HOTKEY
from core import (
    get_selected_text,
    call_api,
    show_options,
    get_config_key,
    build_prompt,
    format_parse_result,
    get_history,
    show_history
)


def on_hotkey():
    """热键触发时的处理逻辑"""
    print("\n[触发] 获取选中文字...")
    
    text = get_selected_text()
    if not text.strip():
        print("[提示] 未检测到选中文字")
        return
    
    print(f"[输入] {text[:50]}{'...' if len(text) > 50 else ''}")
    
    # 显示选项让用户选择
    show_options()
    try:
        choice = int(input("\n输入数字选择: "))
    except ValueError:
        print("[取消]")
        return
    
    if choice == 0:
        print("[取消]")
        return
    
    # 获取配置 key
    config_key = get_config_key(choice)
    if not config_key:
        print("[错误] 无效选项")
        return
    
    # 构造专业 prompt
    prompt_data = build_prompt(text, config_key)
    
    print(f"\n[System Prompt]\n{prompt_data['system'][:100]}...")
    print(f"\n[User Prompt]\n{prompt_data['user'][:200]}...")
    print(f"\n[Expected Format] {prompt_data['expected_format']}")
    print("\n[处理] 调用 API 中...")
    
    # 调用 API 并解析
    raw_response, parse_result = call_api(prompt_data)
    
    # 保存到历史记录
    history = get_history()
    history.add(
        input_text=text,
        option=prompt_data["config"].name,
        prompt=prompt_data["user"],
        result=raw_response,
        valid=parse_result.success
    )
    
    print(f"\n[原始返回]\n{raw_response}\n")
    print(format_parse_result(parse_result))
    print("-" * 40)


def on_show_history():
    """显示历史记录"""
    show_history(5)


def main():
    print("=" * 40)
    print("  文字处理工具已启动")
    print(f"  热键: {HOTKEY.upper()} - 处理选中文字")
    print("  热键: CTRL+H - 查看历史记录")
    print("  按 Ctrl+C 退出")
    print("=" * 40)
    
    # 注册热键
    keyboard.add_hotkey(HOTKEY, on_hotkey)
    keyboard.add_hotkey("ctrl+h", on_show_history)
    
    # 保持运行
    keyboard.wait()


if __name__ == "__main__":
    main()
