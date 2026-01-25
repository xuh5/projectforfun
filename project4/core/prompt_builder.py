# Prompt 构造器 - 基于主流 prompt engineering 实践

from dataclasses import dataclass


@dataclass
class PromptConfig:
    """Prompt 配置"""
    name: str
    system_prompt: str
    user_template: str
    output_format: str  # 期望的输出格式描述
    examples: list[dict] = None  # few-shot 示例


# 定义各选项的专业 prompt 配置
PROMPT_CONFIGS = {
    "explain_code": PromptConfig(
        name="Explain whole code",
        system_prompt="You are an expert programmer. Explain code clearly and concisely.",
        user_template="""Please explain the following code:

```
{text}
```

Requirements:
1. Explain the overall purpose
2. Describe the main logic flow
3. Note any important patterns or techniques used""",
        output_format="markdown",
        examples=None
    ),
    
    "explain_functions": PromptConfig(
        name="Explain Each Function",
        system_prompt="You are an expert code reviewer. Analyze each function in detail.",
        user_template="""Analyze each function in the following code:

```
{text}
```

For EACH function, provide:
- Function name
- Purpose
- Parameters and return value
- Key logic

Format your response as a numbered list.""",
        output_format="numbered_list",
        examples=None
    ),
    
    "make_examples": PromptConfig(
        name="Make example for selected functions",
        system_prompt="You are a technical writer creating code examples.",
        user_template="""Create usage examples for the following code:

```
{text}
```

Requirements:
1. Provide practical, runnable examples
2. Include comments explaining each step
3. Show both basic and edge cases""",
        output_format="code_blocks",
        examples=None
    ),
    
    "complexity": PromptConfig(
        name="Analyze Time/Space Complexity",
        system_prompt="You are an algorithm expert. Analyze complexity precisely.",
        user_template="""Analyze the time and space complexity of the following code:

```
{text}
```

For each function, provide:
- Time Complexity: O(?)
- Space Complexity: O(?)
- Explanation of why

Format as a table or structured list.""",
        output_format="table",
        examples=None
    ),
    
    "unit_tests": PromptConfig(
        name="Generate Unit Tests",
        system_prompt="You are a QA engineer. Write comprehensive unit tests.",
        user_template="""Generate unit tests for the following code:

```
{text}
```

Requirements:
1. Use pytest framework
2. Cover normal cases, edge cases, and error cases
3. Include descriptive test names
4. Add comments explaining what each test verifies""",
        output_format="python_code",
        examples=None
    ),
}


def build_prompt(text: str, config_key: str) -> dict:
    """
    构造完整的 API 请求 prompt
    
    Returns:
        dict with 'system', 'user', 'expected_format'
    """
    config = PROMPT_CONFIGS.get(config_key)
    if not config:
        return None
    
    return {
        "system": config.system_prompt,
        "user": config.user_template.format(text=text),
        "expected_format": config.output_format,
        "config": config
    }


def get_option_keys() -> list[str]:
    """获取所有选项的 key 列表"""
    return list(PROMPT_CONFIGS.keys())


def get_option_names() -> list[tuple[str, str]]:
    """获取所有选项的 (key, name) 列表"""
    return [(k, v.name) for k, v in PROMPT_CONFIGS.items()]
