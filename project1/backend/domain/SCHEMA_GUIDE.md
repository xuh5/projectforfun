# Node Schema 使用指南

## 🎯 单一数据源原则

**重要：** 所有节点字段定义都在 `node_schema.py` 中！

以后要修改节点结构，只需要修改 `node_schema.py` 一个文件，然后按照下面的步骤更新其他文件。

## 📁 文件结构

```
backend/domain/
├── node_schema.py      ← 🎯 单一数据源！只改这里！
├── schema_utils.py     ← 辅助工具函数
├── models.py           ← Domain Model（需要与 schema 保持一致）
└── SCHEMA_GUIDE.md     ← 本文件

backend/database/
└── models.py           ← Database Model（需要与 schema 保持一致）

backend/api/
└── schemas.py          ← API Schemas（需要与 schema 保持一致）

backend/repositories/
└── database_repository.py  ← Repository（需要与 schema 保持一致）
```

## 🔧 如何添加新字段

### 步骤 1: 在 `node_schema.py` 中添加字段定义

```python
# backend/domain/node_schema.py

NODE_FIELDS = [
    # ... 现有字段 ...
    
    # 添加新字段
    NodeFieldDefinition(
        name="status",
        python_type=Optional[str],
        sqlalchemy_type="String",
        nullable=True,
        indexed=True,
        description="Node status: active, inactive, etc.",
    ),
]
```

### 步骤 2: 更新 Domain Model

在 `backend/domain/models.py` 的 `Node` 类中添加：

```python
@dataclass(frozen=True)
class Node:
    # ... 现有字段 ...
    status: Optional[str] = None  # 新增字段
```

### 步骤 3: 更新 Database Model

在 `backend/database/models.py` 的 `NodeModel` 类中添加：

```python
class NodeModel(Base):
    # ... 现有列 ...
    status = Column(String, nullable=True, index=True)  # 新增列
```

### 步骤 4: 更新 API Schema

在 `backend/api/schemas.py` 中更新：

```python
class NodeCreateRequest(BaseModel):
    # ... 现有字段 ...
    status: str | None = None  # 新增字段

class NodeUpdateRequest(BaseModel):
    # ... 现有字段 ...
    status: str | None = None  # 新增字段
```

### 步骤 5: 更新 Repository

在 `backend/repositories/database_repository.py` 中更新：

```python
def _model_to_node(self, model: NodeModel) -> Node:
    return Node(
        # ... 现有字段 ...
        status=model.status,  # 新增映射
    )

def _node_to_model(self, node: Node) -> NodeModel:
    return NodeModel(
        # ... 现有字段 ...
        status=node.status,  # 新增映射
    )

def update_node(self, node_id: str, **updates) -> Optional[Node]:
    # ... 现有更新逻辑 ...
    if "status" in updates:
        model.status = updates["status"]  # 新增更新逻辑
```

### 步骤 6: 数据库迁移

如果数据库已经存在，需要创建迁移：

```bash
# 使用 Alembic 创建迁移（如果配置了）
alembic revision --autogenerate -m "Add status field to nodes"
alembic upgrade head

# 或者重置数据库（开发环境）
python backend/scripts/reset_db.py
```

## 📋 字段定义检查清单

添加新字段时，确保更新以下位置：

- [ ] `backend/domain/node_schema.py` - 添加字段定义
- [ ] `backend/domain/models.py` - 在 `Node` 类中添加字段
- [ ] `backend/database/models.py` - 在 `NodeModel` 中添加 Column
- [ ] `backend/api/schemas.py` - 在 `NodeCreateRequest` 和 `NodeUpdateRequest` 中添加
- [ ] `backend/repositories/database_repository.py` - 更新 `_model_to_node` 和 `_node_to_model`
- [ ] `backend/repositories/database_repository.py` - 在 `update_node` 中添加更新逻辑
- [ ] 数据库迁移（如果数据库已存在）

## 🛠️ 辅助工具

使用 `schema_utils.py` 中的工具函数：

```python
from backend.domain.schema_utils import (
    validate_schema_consistency,
    print_schema_summary,
    get_fields_for_api,
)

# 验证 schema 一致性
errors = validate_schema_consistency()
if errors:
    print("Schema errors:", errors)

# 打印 schema 摘要
print_schema_summary()

# 获取 API 字段
api_fields = get_fields_for_api()
```

## ⚠️ 注意事项

1. **字段名必须一致**：所有层的字段名必须与 `node_schema.py` 中的定义完全一致
2. **类型必须匹配**：Python 类型、SQLAlchemy 类型、Pydantic 类型必须匹配
3. **默认值**：确保所有层的默认值一致
4. **可空性**：确保 `nullable` 设置在所有层都一致
5. **索引**：如果字段需要索引，确保在 Database Model 中添加 `index=True`

## 📚 相关文件

- `backend/domain/node_schema.py` - 字段定义
- `backend/domain/schema_utils.py` - 工具函数
- `backend/domain/models.py` - Domain Model
- `backend/database/models.py` - Database Model
- `backend/api/schemas.py` - API Schemas
- `backend/repositories/database_repository.py` - Repository

