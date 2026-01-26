# API 客户端 - 处理请求和响应

import httpx
from .response_parser import parse_response, ParseResult
from .settings import get_settings


def call_api(prompt_data: dict) -> tuple[str, ParseResult]:
    """
    调用 API 并解析响应
    
    Args:
        prompt_data: 包含 system, user, expected_format 的字典
    
    Returns:
        (raw_response, parse_result)
    """
    settings = get_settings()
    
    # 根据设置决定使用真实 API 还是模拟
    if settings.mock_mode or not settings.api_key:
        raw = _mock_response(prompt_data)
    else:
        raw = _call_real_api(prompt_data, settings)
    
    # 解析验证响应
    result = parse_response(raw, prompt_data["expected_format"])
    
    return raw, result


def _call_real_api(prompt_data: dict, settings) -> str:
    """调用真实 API（自动识别 OpenAI/Claude 格式）"""
    
    # 检测是否是 Claude API
    is_claude = "anthropic" in settings.api_url.lower()
    
    if is_claude:
        return _call_claude_api(prompt_data, settings)
    else:
        return _call_openai_api(prompt_data, settings)


def _call_openai_api(prompt_data: dict, settings) -> str:
    """调用 OpenAI 兼容 API（OpenAI/Grok/Gemini）"""
    headers = {
        "Authorization": f"Bearer {settings.api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": settings.model,
        "messages": [
            {"role": "system", "content": prompt_data["system"]},
            {"role": "user", "content": prompt_data["user"]}
        ]
    }
    
    try:
        with httpx.Client(timeout=settings.timeout) as client:
            resp = client.post(settings.api_url, headers=headers, json=payload)
            resp.raise_for_status()
            data = resp.json()
            
            # OpenAI 格式
            if "choices" in data:
                return data["choices"][0]["message"]["content"]
            
            # 其他格式尝试
            return data.get("result", data.get("content", str(data)))
            
    except httpx.TimeoutException:
        return "[Error] API request timeout"
    except httpx.HTTPStatusError as e:
        return f"[Error] HTTP {e.response.status_code}: {e.response.text[:200]}"
    except Exception as e:
        return f"[Error] {str(e)}"


def _call_claude_api(prompt_data: dict, settings) -> str:
    """调用 Claude (Anthropic) API"""
    headers = {
        "x-api-key": settings.api_key,
        "anthropic-version": "2023-06-01",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": settings.model,
        "max_tokens": 4096,
        "system": prompt_data["system"],
        "messages": [
            {"role": "user", "content": prompt_data["user"]}
        ]
    }
    
    try:
        with httpx.Client(timeout=settings.timeout) as client:
            resp = client.post(settings.api_url, headers=headers, json=payload)
            resp.raise_for_status()
            data = resp.json()
            
            # Claude 格式：content 是数组
            if "content" in data and isinstance(data["content"], list):
                return data["content"][0].get("text", "")
            
            return str(data)
            
    except httpx.TimeoutException:
        return "[Error] API request timeout"
    except httpx.HTTPStatusError as e:
        return f"[Error] HTTP {e.response.status_code}: {e.response.text[:200]}"
    except Exception as e:
        return f"[Error] {str(e)}"


def _mock_response(prompt_data: dict) -> str:
    """测试模式：模拟 API 返回"""
    fmt = prompt_data["expected_format"]
    
    if fmt == "python_code":
        return """```python
import pytest

def test_example():
    \"\"\"Test basic functionality\"\"\"
    assert 1 + 1 == 2

def test_edge_case():
    \"\"\"Test edge case\"\"\"
    assert [] == []
    assert "" == ""
```"""
    
    elif fmt == "table":
        return """## Complexity Analysis

| Function | Time Complexity | Space Complexity |
|----------|----------------|------------------|
| main | O(n) | O(1) |
| helper | O(log n) | O(n) |

**Explanation:**
- `main`: Linear time due to single loop iteration
- `helper`: Logarithmic time with recursive calls"""
    
    elif fmt == "numbered_list":
        return """## Function Analysis

1. **main()**: Entry point of the program
   - Initializes variables
   - Calls helper functions
   
2. **helper()**: Utility function
   - Performs data transformation
   - Returns processed result"""
    
    elif fmt == "code_blocks":
        return """## Usage Examples

### Basic Usage
```python
result = my_function("hello")
print(result)  # Output: "HELLO"
```

### Advanced Usage
```python
# With options
result = my_function("hello", uppercase=True, trim=True)
print(result)  # Output: "HELLO"
```"""
    
    else:  # markdown
        return f"""## Code Explanation

This code implements a solution for the given problem.

### Overview
The main purpose is to process input and return transformed output.

### Key Points
- Uses efficient algorithms
- Handles edge cases properly
- Well-structured code

### Input Sample
```
{prompt_data['user'][:100]}...
```"""
