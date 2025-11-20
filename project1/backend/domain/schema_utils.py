"""
Schema Utilities - 辅助工具函数
用于从 node_schema 生成代码或验证一致性
"""
from __future__ import annotations

from typing import Dict, Any, List
from .node_schema import NODE_FIELDS, NodeFieldDefinition, get_field_by_name


def generate_pydantic_field_definition(field: NodeFieldDefinition) -> str:
    """生成 Pydantic 字段定义代码"""
    if field.nullable:
        type_str = f"{field.python_type.__name__} | None = None"
    else:
        type_str = f"{field.python_type.__name__}"
        if field.default is not None:
            type_str += f' = "{field.default}"' if isinstance(field.default, str) else f" = {field.default}"
    
    comment = f"  # {field.description}" if field.description else ""
    return f"    {field.name}: {type_str}{comment}"


def generate_sqlalchemy_column_definition(field: NodeFieldDefinition) -> str:
    """生成 SQLAlchemy Column 定义代码"""
    from sqlalchemy import Column, String, Text, Integer, Float, Boolean
    
    # 确定 SQLAlchemy 类型
    if field.sqlalchemy_type == "String":
        sql_type = "String"
    elif field.sqlalchemy_type == "Text":
        sql_type = "Text"
    elif field.sqlalchemy_type == "Integer":
        sql_type = "Integer"
    elif field.sqlalchemy_type == "Float":
        sql_type = "Float"
    elif field.sqlalchemy_type == "Boolean":
        sql_type = "Boolean"
    else:
        sql_type = "String"
    
    args = []
    if not field.nullable:
        args.append("nullable=False")
    if field.indexed:
        args.append("index=True")
    if field.default is not None:
        if isinstance(field.default, str):
            args.append(f'default="{field.default}"')
        else:
            args.append(f"default={field.default}")
    
    comment = f"  # {field.description}" if field.description else ""
    args_str = ", ".join(args) if args else ""
    return f"    {field.name} = Column({sql_type}{', ' + args_str if args_str else ''}){comment}"


def validate_schema_consistency() -> List[str]:
    """验证 schema 定义的一致性，返回错误列表"""
    errors = []
    
    # 检查是否有重复字段名
    names = [f.name for f in NODE_FIELDS]
    duplicates = [name for name in names if names.count(name) > 1]
    if duplicates:
        errors.append(f"重复的字段名: {set(duplicates)}")
    
    # 检查必填字段是否有默认值
    for field in NODE_FIELDS:
        if not field.nullable and field.default is None and field.name != "id":
            errors.append(f"必填字段 {field.name} 应该有默认值或明确标记为 nullable=False")
    
    return errors


def get_fields_for_api() -> List[NodeFieldDefinition]:
    """获取需要在 API 中暴露的字段"""
    return [f for f in NODE_FIELDS if f.in_api]


def get_fields_for_frontend() -> List[NodeFieldDefinition]:
    """获取需要在前端使用的字段"""
    return [f for f in NODE_FIELDS if f.in_frontend]


def print_schema_summary() -> None:
    """打印 schema 摘要（用于调试）"""
    print("=" * 60)
    print("Node Schema Summary")
    print("=" * 60)
    print(f"Total fields: {len(NODE_FIELDS)}")
    print(f"Required fields: {len([f for f in NODE_FIELDS if not f.nullable])}")
    print(f"Indexed fields: {len([f for f in NODE_FIELDS if f.indexed])}")
    print("\nFields:")
    for field in NODE_FIELDS:
        required = "REQUIRED" if not field.nullable else "optional"
        indexed = "INDEXED" if field.indexed else ""
        print(f"  - {field.name}: {field.python_type.__name__} ({required}) {indexed}")
        if field.description:
            print(f"    {field.description}")
    print("=" * 60)

