# 历史记录管理 - 最多保存10条

import json
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path

MAX_RECORDS = 10
HISTORY_FILE = Path(__file__).parent.parent / "history.json"


@dataclass
class Record:
    """单条记录"""
    id: int
    timestamp: str
    input_text: str
    option: str
    prompt_preview: str
    result: str
    valid: bool


class History:
    """历史记录管理器"""
    
    def __init__(self):
        self.records: list[Record] = []
        self._next_id = 1
        self._load()
    
    def add(self, input_text: str, option: str, prompt: str, result: str, valid: bool) -> Record:
        """添加新记录"""
        record = Record(
            id=self._next_id,
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            input_text=input_text[:100],  # 截断保存
            option=option,
            prompt_preview=prompt[:200],
            result=result[:500],
            valid=valid
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
    
    def clear(self):
        """清空所有记录"""
        self.records = []
        self._save()
    
    def _save(self):
        """保存到文件"""
        data = [asdict(r) for r in self.records]
        HISTORY_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2))
    
    def _load(self):
        """从文件加载"""
        if HISTORY_FILE.exists():
            try:
                data = json.loads(HISTORY_FILE.read_text())
                self.records = [Record(**r) for r in data]
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
        status = "✓" if r.valid else "✗"
        print(f"#{r.id} [{r.timestamp}] {r.option}")
        print(f"   输入: {r.input_text[:40]}...")
        print(f"   结果: {r.result[:60]}... [{status}]")
        print()
