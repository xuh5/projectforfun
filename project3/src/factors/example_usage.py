"""Example usage of the Factor Provider System."""

import logging
import sys
from pathlib import Path

# Add src directory to Python path for imports
src_dir = Path(__file__).parent.parent
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

from factors.manager import FactorManager
from factors.registry import FactorRegistry
from filter import Filter

# Configure logging - simplified
logging.basicConfig(
    level=logging.WARNING,  # Only show warnings and errors
    format='%(levelname)s: %(message)s'
)

logger = logging.getLogger(__name__)


def example_1_basic_usage():
    """Example 1: Basic usage with FactorManager."""
    print("=" * 60)
    print("Example 1: 测试 Factor 系统")
    print("=" * 60)
    
    # Initialize manager (loads config automatically)
    manager = FactorManager()
    manager.initialize_providers()
    
    # Get available factors
    available_factors = manager.get_available_factors()
    print(f"\n✅ 可用因子: {len(available_factors)} 个")
    print(f"   因子列表: {', '.join(sorted(available_factors))}")
    
    # Fetch factors for symbols
    symbols = ["AAPL", "MSFT"]
    print(f"\n📊 获取 {symbols} 的因子数据...")
    factors_data = manager.fetch_all_factors(symbols)
    
    print(f"✅ 成功获取 {len(factors_data)} 个股票的数据")
    if factors_data:
        symbol = list(factors_data.keys())[0]
        print(f"\n📋 {symbol} 的因子示例 (前5个):")
        sample_factors = list(factors_data[symbol].keys())[:5]
        for factor in sample_factors:
            value = factors_data[symbol][factor]
            # Format large numbers
            if isinstance(value, (int, float)) and value > 1000:
                if value > 1_000_000_000:
                    value_str = f"${value/1_000_000_000:.2f}B"
                elif value > 1_000_000:
                    value_str = f"${value/1_000_000:.2f}M"
                else:
                    value_str = f"${value/1_000:.2f}K"
            else:
                value_str = str(value)
            print(f"   • {factor}: {value_str}")


def example_2_with_filter():
    """Example 2: Using FactorManager with Filter and save to Excel."""
    print("\n" + "=" * 60)
    print("Example 2: Filter Stocks and Save Results")
    print("=" * 60)
    
    # Initialize manager
    manager = FactorManager()
    manager.initialize_providers()
    
    # Create filter with manager
    filter_obj = Filter(factor_manager=manager)
    
    # Test symbols
    symbols = ["AAPL", "MSFT", "GOOGL", "AMZN", "META", "TSLA", "NVDA"]
    print(f"\n📊 获取 {len(symbols)} 个股票的因子数据...")
    
    # Fetch actual factor data
    factors_data = manager.fetch_all_factors(symbols)
    print(f"✅ 成功获取 {len(factors_data)} 个股票的数据")
    
    # Create stock data with factors merged in
    stocks = []
    for symbol in symbols:
        if symbol in factors_data:
            stock = {
                "symbol": symbol,
                "name": factors_data[symbol].get("longName", symbol),
                "sector": factors_data[symbol].get("sector", "Unknown")
            }
            # Merge in all factors
            stock.update(factors_data[symbol])
            stocks.append(stock)
    
    # Filter stocks
    print(f"\n🔍 应用过滤条件: marketCap > 5M...")
    filtered_symbols = filter_obj.filter(stocks)
    
    # Get filtered stocks with their factors
    filtered_stocks = [s for s in stocks if s["symbol"] in filtered_symbols]
    
    # Display results
    print(f"\n{'='*60}")
    print(f"📈 过滤结果")
    print(f"{'='*60}")
    print(f"总股票数: {len(stocks)}")
    print(f"通过过滤: {len(filtered_stocks)} ✅")
    print(f"未通过: {len(stocks) - len(filtered_stocks)} ❌")
    
    if filtered_stocks:
        print(f"\n✅ 通过过滤的公司:")
        for stock in filtered_stocks:
            market_cap = stock.get('marketCap', 0)
            market_cap_m = market_cap / 1_000_000  # Convert to millions
            print(f"  • {stock['symbol']:6s} - {stock.get('name', 'N/A')[:40]:40s} | "
                  f"marketCap: ${market_cap_m:,.0f}M | sector: {stock.get('sector', 'N/A')}")
        
        # Save to Excel using manager
        try:
            output_file = "filtered_stocks_with_factors.xlsx"
            manager.save_factors_excel(factors_data, filtered_stocks, output_file)
            print(f"\n💾 已保存到: {output_file}")
        except Exception as e:
            print(f"\n❌ 保存Excel失败: {e}")
    else:
        print("\n⚠️  没有股票通过过滤条件")


def example_3_direct_registry():
    """Example 3: Direct usage of FactorRegistry."""
    print("\n" + "=" * 60)
    print("Example 3: Direct FactorRegistry Usage")
    print("=" * 60)
    
    from factors.first_level.yfinance_fetcher import YFinanceFactorFetcher
    
    # Get registry instance
    registry = FactorRegistry()
    
    # Unregister existing provider if it exists
    if "yfinance" in registry:
        registry.unregister("yfinance")
    
    # Create and register provider
    yfinance_provider = YFinanceFactorFetcher()
    registry.register(yfinance_provider)
    
    # List providers
    providers = registry.list_providers()
    print(f"\nRegistered providers: {providers}")
    
    # Get all factors
    all_factors = registry.get_all_factors()
    print(f"\nAll available factors: {len(all_factors)}")
    
    # Get factors from specific provider
    yfinance_factors = registry.get_factors_by_provider("yfinance")
    print(f"\nYFinance factors: {len(yfinance_factors)}")
    print(f"Sample: {sorted(list(yfinance_factors))[:5]}")


def example_4_custom_factor_selection():
    """Example 4: Custom factor selection via config."""
    print("\n" + "=" * 60)
    print("Example 4: Custom Factor Selection")
    print("=" * 60)
    
    # This would require modifying factor_config.json to select specific factors
    # For example:
    # {
    #   "enabled_providers": ["yfinance"],
    #   "factor_selection": {
    #     "yfinance": ["marketCap", "peRatio", "dividendYield", "sector"]
    #   }
    # }
    
    manager = FactorManager()
    manager.initialize_providers()
    
    # Get only selected factors
    selected_factors = manager.get_available_factors()
    print(f"\nSelected factors from config: {len(selected_factors)}")
    print(f"Factors: {sorted(list(selected_factors))}")


if __name__ == "__main__":
    try:
        # Clear registry between examples to avoid conflicts
        registry = FactorRegistry()
        if registry.list_providers():
            registry.clear()
        
        example_1_basic_usage()
        
        # Clear registry before next example
        registry.clear()
        
        example_2_with_filter()
        
        # Clear registry before next example
        registry.clear()
        
        example_3_direct_registry()
        
        # Clear registry before next example
        registry.clear()
        
        example_4_custom_factor_selection()
        
        print("\n" + "=" * 60)
        print("All examples completed!")
        print("=" * 60)
    except Exception as e:
        logger.error(f"Example failed: {e}", exc_info=True)

