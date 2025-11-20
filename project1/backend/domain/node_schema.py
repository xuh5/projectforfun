"""
Node Schema Definition - Single Source of Truth (单一数据源)

⚠️ 重要：修改节点结构时，只需要修改这个文件！
以后添加新字段时，只需要在这里添加一行定义。

使用方法：
1. 在这个文件中添加/修改字段定义
2. 其他文件会自动从这个定义生成代码
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Dict, Any, Tuple, List

# SQLAlchemy 类型映射
SQLALCHEMY_TYPE_MAP = {
    str: "String",
    Optional[str]: "String",
    int: "Integer",
    Optional[int]: "Integer",
    float: "Float",
    Optional[float]: "Float",
    bool: "Boolean",
    Optional[bool]: "Boolean",
    Dict[str, Any]: "Text",  # JSON stored as Text
}


@dataclass
class NodeFieldDefinition:
    """节点字段定义"""
    name: str
    python_type: type
    sqlalchemy_type: str  # "String", "Text", "Integer", etc.
    nullable: bool = True
    default: Any = None
    indexed: bool = False
    description: str = ""
    in_api: bool = True  # 是否在 API 中暴露
    in_frontend: bool = True  # 是否在前端使用


# ============================================
# 🎯 节点字段定义 - 只在这里修改！
# ============================================
# 以后要添加新字段，只需要在这里添加一行！
NODE_FIELDS: List[NodeFieldDefinition] = [
    NodeFieldDefinition(
        name="id",
        python_type=str,
        sqlalchemy_type="String",
        nullable=False,
        indexed=True,
        description="Unique identifier",
    ),
    NodeFieldDefinition(
        name="type",
        python_type=str,
        sqlalchemy_type="String",
        nullable=False,
        default="company",
        indexed=True,
        description="Node type: company, person, project, etc.",
    ),
    NodeFieldDefinition(
        name="label",
        python_type=str,
        sqlalchemy_type="String",
        nullable=False,
        indexed=True,
        description="Display name",
    ),
    NodeFieldDefinition(
        name="description",
        python_type=str,
        sqlalchemy_type="Text",
        nullable=False,
        description="Description text",
    ),
    NodeFieldDefinition(
        name="sector",
        python_type=Optional[str],
        sqlalchemy_type="String",
        nullable=True,
        indexed=True,
        description="Industry sector",
    ),
    NodeFieldDefinition(
        name="color",
        python_type=Optional[str],
        sqlalchemy_type="String",
        nullable=True,
        description="Display color",
    ),
    # ============================================
    # 添加新字段示例（取消注释并修改）：
    # ============================================
    # NodeFieldDefinition(
    #     name="status",
    #     python_type=Optional[str],
    #     sqlalchemy_type="String",
    #     nullable=True,
    #     indexed=True,
    #     description="Node status: active, inactive, etc.",
    # ),
    # NodeFieldDefinition(
    #     name="priority",
    #     python_type=Optional[int],
    #     sqlalchemy_type="Integer",
    #     nullable=True,
    #     description="Priority level (1-10)",
    # ),
]

# 计算字段（不存储在数据库，但存在于 Domain Model）
COMPUTED_FIELDS = {
    "metadata": Dict[str, Any],  # 存储在 metadata_json
    "position": Optional[Tuple[float, float, float]],  # 动态计算
}

# 字段名称列表（方便使用）
NODE_FIELD_NAMES = [field.name for field in NODE_FIELDS]
DB_FIELD_NAMES = NODE_FIELD_NAMES + ["metadata_json"]  # metadata 存储在 metadata_json
API_FIELD_NAMES = [field.name for field in NODE_FIELDS if field.in_api]
FRONTEND_FIELD_NAMES = [field.name for field in NODE_FIELDS if field.in_frontend]


def get_field_by_name(name: str) -> NodeFieldDefinition | None:
    """根据字段名获取字段定义"""
    return next((f for f in NODE_FIELDS if f.name == name), None)


def get_required_fields() -> List[NodeFieldDefinition]:
    """获取必填字段列表"""
    return [f for f in NODE_FIELDS if not f.nullable]


def get_indexed_fields() -> List[NodeFieldDefinition]:
    """获取需要索引的字段列表"""
    return [f for f in NODE_FIELDS if f.indexed]

