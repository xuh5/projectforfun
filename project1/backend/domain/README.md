# Domain Layer - Node Schema

## 🎯 单一数据源架构

我们已经实现了**单一数据源（Single Source of Truth）**架构，所有节点字段定义都集中在 `node_schema.py` 中。

## 📁 核心文件

### `node_schema.py` - ⭐ 单一数据源
**这是最重要的文件！** 所有节点字段定义都在这里。

以后要添加/修改节点字段，只需要：
1. 在 `node_schema.py` 的 `NODE_FIELDS` 列表中添加/修改字段定义
2. 按照 `SCHEMA_GUIDE.md` 的步骤更新其他文件

### `schema_utils.py` - 辅助工具
提供工具函数用于：
- 验证 schema 一致性
- 生成代码片段
- 获取字段列表

### `models.py` - Domain Model
Domain 层的 Node 类定义。字段应该与 `node_schema.py` 保持一致。

## 🚀 快速开始

### 查看当前字段定义

```python
from backend.domain.node_schema import NODE_FIELDS

for field in NODE_FIELDS:
    print(f"{field.name}: {field.python_type.__name__} ({'required' if not field.nullable else 'optional'})")
```

### 验证 schema 一致性

```python
from backend.domain.schema_utils import validate_schema_consistency

errors = validate_schema_consistency()
if errors:
    print("Errors:", errors)
else:
    print("Schema is consistent!")
```

### 打印 schema 摘要

```python
from backend.domain.schema_utils import print_schema_summary

print_schema_summary()
```

## 📖 详细文档

查看 `SCHEMA_GUIDE.md` 了解如何添加新字段。

## ⚠️ 重要提示

1. **永远先修改 `node_schema.py`**
2. **然后按照 `SCHEMA_GUIDE.md` 更新其他文件**
3. **使用 `validate_schema_consistency()` 验证一致性**

