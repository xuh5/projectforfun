# Response 解析器 - 验证和结构化 API 返回结果

import re
from dataclasses import dataclass


@dataclass
class ParseResult:
    """解析结果"""
    success: bool
    content: str
    errors: list[str]
    metadata: dict


def parse_response(raw: str, expected_format: str) -> ParseResult:
    """
    解析并验证 API 返回的内容
    
    Args:
        raw: API 原始返回
        expected_format: 期望的格式类型
    
    Returns:
        ParseResult 包含验证结果
    """
    errors = []
    metadata = {}
    
    # 基础检查
    if not raw or not raw.strip():
        return ParseResult(False, "", ["Empty response"], {})
    
    content = raw.strip()
    
    # 根据期望格式进行验证
    if expected_format == "markdown":
        errors.extend(_validate_markdown(content, metadata))
    
    elif expected_format == "numbered_list":
        errors.extend(_validate_numbered_list(content, metadata))
    
    elif expected_format == "code_blocks":
        errors.extend(_validate_code_blocks(content, metadata))
    
    elif expected_format == "table":
        errors.extend(_validate_table(content, metadata))
    
    elif expected_format == "python_code":
        errors.extend(_validate_python_code(content, metadata))
    
    return ParseResult(
        success=len(errors) == 0,
        content=content,
        errors=errors,
        metadata=metadata
    )


def _validate_markdown(content: str, metadata: dict) -> list[str]:
    """验证 markdown 格式"""
    errors = []
    
    # 检查是否有标题
    headers = re.findall(r'^#{1,6}\s+.+', content, re.MULTILINE)
    metadata["header_count"] = len(headers)
    
    # 检查最小长度
    if len(content) < 50:
        errors.append("Response too short for explanation")
    
    return errors


def _validate_numbered_list(content: str, metadata: dict) -> list[str]:
    """验证编号列表格式"""
    errors = []
    
    # 查找编号项 (1. xxx 或 1) xxx)
    items = re.findall(r'^\d+[\.\)]\s+.+', content, re.MULTILINE)
    metadata["item_count"] = len(items)
    
    if len(items) == 0:
        errors.append("No numbered items found")
    
    return errors


def _validate_code_blocks(content: str, metadata: dict) -> list[str]:
    """验证代码块格式"""
    errors = []
    
    # 查找 markdown 代码块
    blocks = re.findall(r'```[\s\S]*?```', content)
    metadata["code_block_count"] = len(blocks)
    
    if len(blocks) == 0:
        errors.append("No code blocks found")
    
    return errors


def _validate_table(content: str, metadata: dict) -> list[str]:
    """验证表格格式"""
    errors = []
    
    # 检查是否有表格行（包含 | 的行）
    table_rows = re.findall(r'^\|.+\|$', content, re.MULTILINE)
    metadata["table_row_count"] = len(table_rows)
    
    # 检查是否有复杂度标记
    has_big_o = bool(re.search(r'O\([^)]+\)', content))
    metadata["has_complexity"] = has_big_o
    
    if not has_big_o:
        errors.append("No O() complexity notation found")
    
    return errors


def _validate_python_code(content: str, metadata: dict) -> list[str]:
    """验证 Python 测试代码"""
    errors = []
    
    # 检查是否有 pytest 测试函数
    test_funcs = re.findall(r'def test_\w+', content)
    metadata["test_count"] = len(test_funcs)
    
    if len(test_funcs) == 0:
        errors.append("No test functions (test_*) found")
    
    # 检查是否有 assert 语句
    asserts = re.findall(r'\bassert\b', content)
    metadata["assert_count"] = len(asserts)
    
    if len(asserts) == 0:
        errors.append("No assert statements found")
    
    return errors


def format_parse_result(result: ParseResult) -> str:
    """格式化解析结果用于显示"""
    output = []
    
    if result.success:
        output.append("[✓] 格式验证通过")
    else:
        output.append("[✗] 格式验证失败")
        for err in result.errors:
            output.append(f"    - {err}")
    
    if result.metadata:
        output.append("[i] 元数据:")
        for k, v in result.metadata.items():
            output.append(f"    - {k}: {v}")
    
    return "\n".join(output)
