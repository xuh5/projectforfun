# 选项层 - 基于 prompt_builder 的配置

from .prompt_builder import get_option_names, get_option_keys


def show_options():
    """显示选项列表"""
    print("\n请选择操作：")
    for i, (key, name) in enumerate(get_option_names()):
        print(f"  [{i + 1}] {name}")
    print("  [0] 取消")


def get_config_key(choice: int) -> str | None:
    """根据选择获取配置 key"""
    keys = get_option_keys()
    if choice < 1 or choice > len(keys):
        return None
    return keys[choice - 1]
