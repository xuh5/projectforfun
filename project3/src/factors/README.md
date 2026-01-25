# Factor Provider System

可扩展的因子（factors）管理系统，支持多个数据源和动态因子选择。

## 架构设计

### 核心组件

1. **FactorProvider (基类)**
   - 所有因子提供者的抽象基类
   - 定义标准接口：`fetch_factors()` 和 `get_available_factors()`

2. **FactorRegistry (注册中心)**
   - 单例模式，管理所有已注册的因子提供者
   - 提供注册、查询、获取可用因子列表等功能

3. **FactorManager (管理器)**
   - 根据配置文件初始化和管理因子提供者
   - 统一调用多个提供者获取因子
   - 根据配置过滤和合并因子

4. **配置文件 (factor_config.json)**
   - 指定启用的提供者
   - 选择每个提供者使用的因子（可选）

## 使用方法

### 1. 配置因子提供者

编辑 `factor_config.json`:

```json
{
  "enabled_providers": ["yfinance"],
  "factor_selection": {
    "yfinance": ["marketCap", "peRatio", "dividendYield", "sector"]
  },
  "provider_config": {
    "yfinance": {
      "factors_dir": "factors",
      "delay": 1.5
    }
  }
}
```

- `enabled_providers`: 启用的提供者列表
- `factor_selection`: 每个提供者要使用的因子列表（空列表表示使用所有可用因子）
- `provider_config`: 每个提供者的特定配置

### 2. 基本使用

```python
from factors.manager import FactorManager

# 初始化管理器（会自动加载配置）
manager = FactorManager()

# 获取所有可用因子
available_factors = manager.get_available_factors()
print(f"Available factors: {available_factors}")

# 获取多个股票的因子
symbols = ["AAPL", "MSFT", "GOOGL"]
factors_data = manager.fetch_all_factors(symbols)

# factors_data 格式: {symbol: {factor_name: value, ...}, ...}
```

### 3. 在 Filter 中使用

```python
from factors.manager import FactorManager
from filter import Filter

# 创建因子管理器
factor_manager = FactorManager()

# 创建 Filter 并传入管理器
filter_obj = Filter(factor_manager=factor_manager)

# Filter 现在可以动态获取可用因子
available_factors = filter_obj.get_available_factors()

# 使用因子进行过滤
stocks = [...]  # 股票数据列表
filtered = filter_obj.filter(stocks)
```

### 4. 直接使用 Registry

```python
from factors.registry import FactorRegistry
from factors.first_level.yfinance_fetcher import YFinanceFactorFetcher

# 获取注册中心实例
registry = FactorRegistry()

# 创建并注册提供者
yfinance_provider = YFinanceFactorFetcher()
registry.register(yfinance_provider)

# 获取所有可用因子
all_factors = registry.get_all_factors()

# 获取特定提供者的因子
yfinance_factors = registry.get_factors_by_provider("yfinance")
```

## 扩展新的因子提供者

### 步骤 1: 创建提供者类

```python
from factors.base import FactorProvider
from typing import Dict, List, Set

class MyCustomProvider(FactorProvider):
    def __init__(self):
        super().__init__(name="my_custom")
        self._available_factors = {"factor1", "factor2", "factor3"}
    
    def fetch_factors(self, symbols: List[str], **kwargs) -> Dict[str, Dict]:
        # 实现获取因子的逻辑
        factors_data = {}
        for symbol in symbols:
            factors_data[symbol] = {
                "factor1": value1,
                "factor2": value2,
                # ...
            }
        return factors_data
    
    def get_available_factors(self) -> Set[str]:
        return self._available_factors.copy()
```

### 步骤 2: 在 Manager 中注册

修改 `factors/manager.py` 的 `_create_provider` 方法：

```python
def _create_provider(self, name: str, config: dict) -> Optional[FactorProvider]:
    if name == "yfinance":
        # ... existing code ...
    elif name == "my_custom":
        from .my_custom_provider import MyCustomProvider
        return MyCustomProvider()
    # ...
```

### 步骤 3: 在配置中启用

在 `factor_config.json` 中添加：

```json
{
  "enabled_providers": ["yfinance", "my_custom"],
  "factor_selection": {
    "yfinance": ["marketCap", "peRatio"],
    "my_custom": ["factor1", "factor2"]
  }
}
```

## 优势

1. **可扩展**: 轻松添加新的因子提供者，无需修改现有代码
2. **可配置**: 通过配置文件灵活选择使用的因子
3. **解耦**: Filter 不依赖具体提供者，只依赖接口
4. **动态**: Filter 可以动态获取可用因子列表
5. **统一管理**: 所有提供者通过 Registry 统一管理

## 文件结构

```
factors/
├── __init__.py          # 导出主要接口
├── base.py              # FactorProvider 基类
├── registry.py          # FactorRegistry 注册中心
├── manager.py           # FactorManager 管理器
├── factor_config.json   # 配置文件
├── first_level/
│   └── yfinance_fetcher.py  # YFinance 提供者
├── second_level/        # 计算因子（未来）
└── third_level/         # 历史数据因子（未来）
```

