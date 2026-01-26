# 历史记录管理 - 最多保存10条

import json
import sys
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path

MAX_RECORDS = 10


def get_data_dir() -> Path:
    """获取数据目录（兼容打包后的 exe）"""
    if getattr(sys, 'frozen', False):
        # 打包后：使用 exe 所在目录
        return Path(sys.executable).parent
    else:
        # 开发时：使用项目根目录
        return Path(__file__).parent.parent


HISTORY_FILE = get_data_dir() / "history.json"


@dataclass
class ActionResult:
    """单个 action 的结果"""
    option: str
    content: str
    valid: bool


@dataclass
class Record:
    """单条记录（可包含多个 action 结果）"""
    id: int
    timestamp: str
    input_text: str
    options: list[str]           # 多个 action keys
    results: list[dict]          # 多个结果 [{option, content, valid}, ...]
    all_valid: bool              # 是否全部成功
    
    # 兼容旧格式的属性
    @property
    def option(self) -> str:
        return self.options[0] if self.options else ""
    
    @property
    def result(self) -> str:
        return self.results[0].get("content", "") if self.results else ""
    
    @property
    def valid(self) -> bool:
        return self.all_valid


class History:
    """历史记录管理器"""
    
    def __init__(self):
        self.records: list[Record] = []
        self._next_id = 1
        self._load()
    
    def add(self, input_text: str, options: list[str], results: list[dict]) -> Record:
        """添加新记录（支持多个 action）
        
        Args:
            input_text: 输入文本
            options: action key 列表
            results: 结果列表 [{option, content, valid}, ...]
        """
        # 截断内容
        truncated_results = [
            {
                "option": r.get("option", ""),
                "content": r.get("content", "")[:500],
                "valid": r.get("valid", False)
            }
            for r in results
        ]
        
        all_valid = all(r.get("valid", False) for r in results)
        
        record = Record(
            id=self._next_id,
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            input_text=input_text[:100],
            options=options,
            results=truncated_results,
            all_valid=all_valid
        )
        
        self.records.append(record)
        self._next_id += 1
        
        # 超过10条删除最早的
        if len(self.records) > MAX_RECORDS:
            self.records = self.records[-MAX_RECORDS:]
        
        self._save()
        return record
    
    def get_all(self) -> list[Record]:
        """获取所有记录（最新的在前）"""
        return list(reversed(self.records))
    
    def get_latest(self, n: int = 5) -> list[Record]:
        """获取最近 n 条记录"""
        return list(reversed(self.records[-n:]))
    
    def delete(self, record_id: int) -> bool:
        """删除指定记录"""
        for i, r in enumerate(self.records):
            if r.id == record_id:
                self.records.pop(i)
                self._save()
                return True
        return False
    
    def clear(self):
        """清空所有记录"""
        self.records = []
        self._next_id = 1
        self._save()
    
    def _save(self):
        """保存到文件"""
        data = []
        for r in self.records:
            data.append({
                "id": r.id,
                "timestamp": r.timestamp,
                "input_text": r.input_text,
                "options": r.options,
                "results": r.results,
                "all_valid": r.all_valid
            })
        HISTORY_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2))
    
    def _load(self):
        """从文件加载（兼容旧格式）"""
        if HISTORY_FILE.exists():
            try:
                data = json.loads(HISTORY_FILE.read_text())
                self.records = []
                for r in data:
                    # 兼容旧格式：单个 option/result
                    if "option" in r and "options" not in r:
                        r["options"] = [r.get("option", "")]
                        r["results"] = [{
                            "option": r.get("option", ""),
                            "content": r.get("result", ""),
                            "valid": r.get("valid", False)
                        }]
                        r["all_valid"] = r.get("valid", False)
                    
                    self.records.append(Record(
                        id=r["id"],
                        timestamp=r["timestamp"],
                        input_text=r["input_text"],
                        options=r.get("options", []),
                        results=r.get("results", []),
                        all_valid=r.get("all_valid", False)
                    ))
                
                if self.records:
                    self._next_id = max(r.id for r in self.records) + 1
            except Exception:
                self.records = []


# 全局实例
_history = None


def get_history() -> History:
    """获取历史记录管理器单例"""
    global _history
    if _history is None:
        _history = History()
    return _history


def show_history(n: int = 5):
    """显示最近 n 条记录"""
    records = get_history().get_latest(n)
    
    if not records:
        print("\n[历史] 暂无记录")
        return
    
    print(f"\n[历史] 最近 {len(records)} 条记录:")
    print("-" * 50)
    
    for r in records:
        status = "✓" if r.all_valid else "✗"
        actions = ", ".join(r.options)
        print(f"#{r.id} [{r.timestamp}] [{actions}]")
        print(f"   输入: {r.input_text[:40]}...")
        for res in r.results:
            res_status = "✓" if res.get("valid") else "✗"
            content = res.get("content", "")[:50]
            print(f"   - {res.get('option')}: {content}... [{res_status}]")
        print()
