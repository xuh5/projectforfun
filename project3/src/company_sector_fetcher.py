"""Company sector fetcher for stock information using Excel file as input source with two-stage caching."""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Set
import pandas as pd
import yfinance as yf

logger = logging.getLogger(__name__)

# Valid sectors
VALID_SECTORS = [
    "Technology",
    "Telecommunications",
    "Healthcare",
    "Financials",
    "Real Estate",
    "Consumer Discretionary",
    "Consumer Staples",
    "Industrials",
    "Basic Materials",
    "Energy",
    "Utilities",
]


class CompanySectorFetcher:
    """Fetches company sector data from Excel file with two-stage caching."""
    
    def __init__(
        self, 
        excel_file: str = "stocks.xlsx",
        symbol_set_file: str = "symbol_set.json",
        stock_list_file: str = "stock_list.json"
    ):
        """
        Initialize data fetcher.
        
        Args:
            excel_file: Path to Excel file containing stock data (must have 'symbol' and 'sector' columns)
            symbol_set_file: Path to file storing symbol set with fetch status
            stock_list_file: Path to file storing complete stock data
        """
        self.excel_file = Path(excel_file)
        self.symbol_set_file = Path(symbol_set_file)
        self.stock_list_file = Path(stock_list_file)
        
        if not self.excel_file.exists():
            raise FileNotFoundError(
                f"Excel file not found: {excel_file}. "
                f"Please provide a valid Excel file with 'symbol' and 'sector' columns."
            )
    
    def fetch_stocks_from_excel(self, sector: Optional[str] = None, limit: Optional[int] = None) -> List[str]:
        """
        Step 1: Fetch stock symbols from Excel file, optionally filtered by sector.
        
        Args:
            sector: Sector name to filter by. Must be one of the valid sectors.
                   If None, returns all stocks from Excel.
                   Valid sectors: Technology, Telecommunications, Healthcare, Financials,
                   Real Estate, Consumer Discretionary, Consumer Staples, Industrials,
                   Basic Materials, Energy, Utilities
            limit: Optional limit on number of symbols to fetch (for testing)
            
        Returns:
            List of stock symbols (strings)
            
        Raises:
            ValueError: If sector is not valid
            FileNotFoundError: If Excel file doesn't exist
            KeyError: If Excel file doesn't have required columns ('symbol' and 'sector')
        """
        logger.info(f"Reading stock data from Excel: {self.excel_file}")
        
        # Validate sector if provided
        if sector is not None:
            if sector not in VALID_SECTORS:
                raise ValueError(
                    f"Invalid sector: {sector}. Valid sectors are: {', '.join(VALID_SECTORS)}"
                )
            logger.info(f"Filtering by sector: {sector}")
        
        try:
            # Read Excel file
            df = pd.read_excel(self.excel_file)
            
            # Validate required columns
            required_columns = ['symbol', 'sector']
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                raise KeyError(
                    f"Excel file is missing required columns: {missing_columns}. "
                    f"Found columns: {list(df.columns)}"
                )
            
            # Filter by sector if provided
            if sector is not None:
                df = df[df['sector'].str.strip().str.lower() == sector.strip().lower()]
                logger.info(f"Filtered to {len(df)} stocks in sector '{sector}'")
            
            # Extract symbols and remove duplicates
            symbols_list = df['symbol'].dropna().astype(str).str.strip().str.upper().unique().tolist()
            symbols_list = sorted(symbols_list)  # Sort for consistency
            
            if limit:
                symbols_list = symbols_list[:limit]
            
            logger.info(f"Found {len(symbols_list)} unique stock symbols")
            
            # Step 1: Save symbol set with fetch status
            self._save_symbol_set(symbols_list)
            
            return symbols_list
            
        except FileNotFoundError:
            raise FileNotFoundError(f"Excel file not found: {self.excel_file}")
        except Exception as e:
            logger.error(f"Failed to read Excel file: {e}")
            raise
    
    def _save_symbol_set(self, symbols: List[str]) -> None:
        """
        Step 1: Save symbol set with fetch status.
        
        Format:
        [
            {"symbol": "AAPL", "ticker_fetched": false},
            {"symbol": "MSFT", "ticker_fetched": false},
            ...
        ]
        
        Args:
            symbols: List of stock symbols
        """
        symbol_set_data = [
            {"symbol": symbol, "ticker_fetched": False}
            for symbol in symbols
        ]
        
        try:
            with open(self.symbol_set_file, "w", encoding="utf-8") as f:
                json.dump(symbol_set_data, f, indent=2, ensure_ascii=False)
            logger.info(f"Saved {len(symbol_set_data)} symbols to {self.symbol_set_file}")
        except Exception as e:
            logger.error(f"Failed to save symbol set to {self.symbol_set_file}: {e}")
            raise
    
    def load_symbol_set(self) -> Optional[List[Dict]]:
        """
        Load symbol set from file.
        
        Returns:
            List of symbol dictionaries with fetch status, or None if file doesn't exist
        """
        if not self.symbol_set_file.exists():
            return None
        
        try:
            with open(self.symbol_set_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            logger.info(f"Loaded {len(data)} symbols from {self.symbol_set_file}")
            return data
        except Exception as e:
            logger.error(f"Failed to load symbol set from {self.symbol_set_file}: {e}")
            return None
    
    def fetch_stock_details(self, symbols: Optional[List[str]] = None, limit: Optional[int] = None) -> List[Dict]:
        """
        Step 2: Fetch detailed stock data for symbols.
        
        This method fetches detailed information for each symbol using yfinance
        and stores the complete data in stock_list.json.
        
        Args:
            symbols: List of symbols to fetch. If None, loads from symbol_set_file
            limit: Optional limit on number of stocks to fetch (for testing)
            
        Returns:
            List of dictionaries containing complete stock information:
            - symbol: Stock ticker symbol
            - name: Company name
            - sector: Industry sector
            - industry: More specific industry classification
            - marketCap: Market capitalization
            - exchange: Stock exchange
        """
        logger.info("Fetching detailed stock data...")
        
        # Load symbols if not provided
        if symbols is None:
            symbol_set_data = self.load_symbol_set()
            if symbol_set_data is None:
                raise ValueError(
                    f"Symbol set file {self.symbol_set_file} not found. "
                    "Run fetch_stocks_from_index() first."
                )
            symbols = [item["symbol"] for item in symbol_set_data]
        
        if limit:
            symbols = symbols[:limit]
        
        stocks_data = []
        symbol_set_data = self.load_symbol_set() or []
        symbol_status_map = {item["symbol"]: item for item in symbol_set_data}
        
        # Ensure all symbols are in the status map (for symbols passed as parameters)
        for symbol in symbols:
            if symbol not in symbol_status_map:
                symbol_status_map[symbol] = {"symbol": symbol, "ticker_fetched": False}
        
        logger.info(f"Processing {len(symbols)} symbols...")
        
        for i, symbol in enumerate(symbols):
            try:
                ticker = yf.Ticker(symbol)
                info = ticker.info
                
                # Check if we got valid data
                if not info or "symbol" not in info:
                    logger.warning(f"Invalid data for {symbol}, skipping")
                    symbol_status_map[symbol]["ticker_fetched"] = False
                    continue
                
                # Extract relevant information
                stock_data = {
                    "symbol": symbol,
                    "name": info.get("longName", info.get("shortName", symbol)),
                    "sector": info.get("sector"),
                    "industry": info.get("industry"),
                    "marketCap": info.get("marketCap"),
                    "exchange": info.get("exchange"),
                }
                
                stocks_data.append(stock_data)
                
                # Update symbol set status - mark as successfully fetched
                symbol_status_map[symbol]["ticker_fetched"] = True
                
                if (i + 1) % 10 == 0:
                    logger.info(f"Processed {i + 1}/{len(symbols)} symbols")
                    
            except Exception as e:
                logger.warning(f"Failed to fetch data for {symbol}: {e}")
                # Mark as failed in symbol set
                symbol_status_map[symbol]["ticker_fetched"] = False
                continue
        
        # Save updated symbol set with fetch status (sorted by symbol for consistency)
        updated_symbol_set = sorted(
            list(symbol_status_map.values()),
            key=lambda x: x["symbol"]
        )
        try:
            with open(self.symbol_set_file, "w", encoding="utf-8") as f:
                json.dump(updated_symbol_set, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.warning(f"Failed to update symbol set status: {e}")
        
        # Step 2: Save complete stock data
        self._save_stock_list(stocks_data)
        
        logger.info(f"Successfully fetched data for {len(stocks_data)} stocks")
        return stocks_data
    
    def _save_stock_list(self, stocks_data: List[Dict]) -> None:
        """
        Step 2: Save complete stock data to file.
        
        Args:
            stocks_data: List of stock data dictionaries
        """
        try:
            with open(self.stock_list_file, "w", encoding="utf-8") as f:
                json.dump(stocks_data, f, indent=2, ensure_ascii=False)
            logger.info(f"Saved {len(stocks_data)} stocks to {self.stock_list_file}")
        except Exception as e:
            logger.error(f"Failed to save stock list to {self.stock_list_file}: {e}")
            raise
    
    def load_from_cache(self) -> Optional[List[Dict]]:
        """
        Load complete stock data from cache file (for backward compatibility).
        
        Returns:
            List of stock data dictionaries, or None if cache doesn't exist
        """
        if not self.stock_list_file.exists():
            return None
        
        try:
            with open(self.stock_list_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            logger.info(f"Loaded {len(data)} stocks from cache: {self.stock_list_file}")
            return data
        except Exception as e:
            logger.error(f"Failed to load cache from {self.stock_list_file}: {e}")
            return None


if __name__ == "__main__":
    """Test script for CompanySectorFetcher - run directly to test functionality."""
    import sys
    import argparse
    
    # Configure logging for testing
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Test CompanySectorFetcher with Excel file")
    parser.add_argument(
        "--excel-file",
        type=str,
        default="stocks.xlsx",
        help="Path to Excel file (default: stocks.xlsx)"
    )
    parser.add_argument(
        "--sector",
        type=str,
        default=None,
        help="Filter by sector (e.g., Technology, Healthcare)"
    )
    args = parser.parse_args()
    
    # Initialize fetcher (requires Excel file)
    excel_file = args.excel_file
    print("=" * 60)
    print("CompanySectorFetcher Test Script")
    print("=" * 60)
    print(f"Using Excel file: {excel_file}")
    print()
    
    try:
        fetcher = CompanySectorFetcher(excel_file=excel_file)
    except FileNotFoundError as e:
        print(f"✗ {e}")
        print("\nPlease create an Excel file with 'symbol' and 'sector' columns.")
        print("Example Excel structure:")
        print("  symbol | sector")
        print("  -------|----------------")
        print("  AAPL   | Technology")
        print("  MSFT   | Technology")
        sys.exit(1)
    
    # Test 1: Fetch stock symbols (Step 1)
    print("Test 1: Fetching stock symbols from Excel...")
    if args.sector:
        print(f"  Filtering by sector: {args.sector}")
    print("-" * 60)
    try:
        # Test with optional sector filter
        symbols = fetcher.fetch_stocks_from_excel(sector=args.sector, limit=10)  # Limit to 10 for testing
        print(f"✓ Successfully fetched {len(symbols)} symbols")
        print(f"  First 5 symbols: {symbols[:5]}")
        print()
    except Exception as e:
        print(f"✗ Failed to fetch symbols: {e}")
        sys.exit(1)
    
    # Test 2: Check symbol_set.json
    print("Test 2: Checking symbol_set.json...")
    print("-" * 60)
    symbol_set = fetcher.load_symbol_set()
    if symbol_set:
        print(f"✓ Symbol set loaded: {len(symbol_set)} symbols")
        print(f"  Sample entry: {symbol_set[0] if symbol_set else 'None'}")
        print()
    else:
        print("✗ Symbol set not found")
        print()
    
    # Test 3: Fetch detailed stock data (Step 2)
    print("Test 3: Fetching detailed stock data...")
    print("-" * 60)
    try:
        # Use first 5 symbols for testing (to avoid too many API calls)
        test_symbols = symbols[:5]
        print(f"  Testing with {len(test_symbols)} symbols: {test_symbols}")
        stocks_data = fetcher.fetch_stock_details(symbols=test_symbols)
        print(f"✓ Successfully fetched data for {len(stocks_data)} stocks")
        if stocks_data:
            print(f"  Sample stock data:")
            import json
            print(json.dumps(stocks_data[0], indent=2))
        print()
    except Exception as e:
        print(f"✗ Failed to fetch stock details: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    # Test 4: Check stock_list.json
    print("Test 4: Checking stock_list.json...")
    print("-" * 60)
    cached_data = fetcher.load_from_cache()
    if cached_data:
        print(f"✓ Stock list loaded: {len(cached_data)} stocks")
        print(f"  First stock: {cached_data[0].get('symbol')} - {cached_data[0].get('name')}")
        print()
    else:
        print("✗ Stock list not found")
        print()
    
    # Test 5: Check updated symbol_set.json status
    print("Test 5: Checking updated symbol_set.json (ticker_fetched status)...")
    print("-" * 60)
    updated_symbol_set = fetcher.load_symbol_set()
    if updated_symbol_set:
        fetched_count = sum(1 for item in updated_symbol_set if item.get("ticker_fetched", False))
        total_count = len(updated_symbol_set)
        print(f"✓ Symbol set status: {fetched_count}/{total_count} symbols marked as fetched")
        print(f"  Sample status entries:")
        for item in updated_symbol_set[:5]:
            status = "✓" if item.get("ticker_fetched") else "✗"
            print(f"    {status} {item.get('symbol')}: ticker_fetched={item.get('ticker_fetched')}")
        print()
    
    print("=" * 60)
    print("All tests completed!")
    print("=" * 60)
    print()
    print("Files created:")
    print(f"  - {fetcher.symbol_set_file} (symbol list with fetch status)")
    print(f"  - {fetcher.stock_list_file} (complete stock data)")
    print()

