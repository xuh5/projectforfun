"""CLI entry point for node data generation pipeline."""

import json
import logging
import sys
import time
from pathlib import Path
from typing import Optional

from .config import load_config
from .clients import OpenAIClient, OllamaClient, DeepSeekClient
from .data_fetcher import DataFetcher
from .filter import Filter
from .generator import NodeGenerator
from .progress import ProgressTracker
from .models import NodeData

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


def get_llm_client(config: dict):
    """
    Get LLM client based on configuration.
    
    Args:
        config: Configuration dictionary
        
    Returns:
        LLM client instance
    """
    provider = config["llm_provider"]
    
    if provider == "openai":
        return OpenAIClient(
            api_key=config["openai_api_key"],
            model=config["openai_model"],
        )
    elif provider == "ollama":
        return OllamaClient(
            base_url=config["ollama_base_url"],
            model=config["ollama_model"],
        )
    elif provider == "deepseek":
        return DeepSeekClient(
            api_key=config["deepseek_api_key"],
            model=config["deepseek_model"],
        )
    else:
        raise ValueError(f"Unknown LLM provider: {provider}")


def fetch_phase(data_fetcher: DataFetcher, force_refresh: bool = False, sector: Optional[str] = None) -> list:
    """
    Fetch stock data using two-stage process:
    1. Get stock symbols from Excel file, optionally filtered by sector (saves to symbol_set.json)
    2. Fetch detailed data for symbols (saves to stock_list.json)
    
    Args:
        data_fetcher: DataFetcher instance
        force_refresh: Force re-fetch even if cache exists
        sector: Optional sector name to filter stocks (e.g., "Technology", "Healthcare")
        
    Returns:
        List of stock data dictionaries
    """
    logger.info("=" * 60)
    logger.info("PHASE 1: Fetching Stock Data")
    logger.info("=" * 60)
    
    if not force_refresh:
        cached_data = data_fetcher.load_from_cache()
        if cached_data:
            logger.info(f"Using cached data: {len(cached_data)} stocks")
            return cached_data
    
    # Step 1: Fetch symbols from Excel file (saves to symbol_set.json)
    if sector:
        logger.info(f"Step 1: Fetching stock symbols from Excel (sector: {sector})...")
    else:
        logger.info("Step 1: Fetching stock symbols from Excel (all sectors)...")
    symbols = data_fetcher.fetch_stocks_from_excel(sector=sector)
    logger.info(f"Retrieved {len(symbols)} stock symbols")
    
    # Step 2: Fetch detailed data for symbols (saves to stock_list.json)
    logger.info("Step 2: Fetching detailed stock data...")
    stocks = data_fetcher.fetch_stock_details(symbols=symbols)
    logger.info(f"Fetched {len(stocks)} stocks with complete data")
    
    return stocks


def filter_phase(
    filter_obj: Filter,
    stocks: list,
    progress_tracker: ProgressTracker,
    force_refresh: bool = False
) -> list:
    """
    Filter stocks based on criteria.
    
    Args:
        filter_obj: Filter instance
        stocks: List of stock data dictionaries
        progress_tracker: ProgressTracker instance
        force_refresh: Force re-filter even if cached
        
    Returns:
        List of filtered stock symbols
    """
    logger.info("=" * 60)
    logger.info("PHASE 2: Filtering Stocks")
    logger.info("=" * 60)
    
    # Check if we have cached filtered list in progress
    progress_data = progress_tracker.progress_data
    if not force_refresh and progress_data.get("filtered_stocks"):
        filtered = progress_data["filtered_stocks"]
        logger.info(f"Using cached filtered list: {len(filtered)} stocks")
        return filtered
    
    logger.info("Applying filters...")
    filtered_symbols = filter_obj.filter(stocks)
    logger.info(f"Filtered to {len(filtered_symbols)} stocks")
    
    # Save to progress
    all_symbols = [s["symbol"] for s in stocks]
    progress_tracker.set_stock_lists(all_symbols, filtered_symbols)
    
    return filtered_symbols


def generate_phase(
    generator: NodeGenerator,
    filtered_symbols: list,
    stocks_data: list,
    progress_tracker: ProgressTracker,
    batch_size: int = 50
) -> None:
    """
    Generate node data using LLM.
    
    Args:
        generator: NodeGenerator instance
        filtered_symbols: List of symbols to process
        stocks_data: Original stock data for reference
        progress_tracker: ProgressTracker instance
        batch_size: Number of symbols to process in each batch
    """
    logger.info("=" * 60)
    logger.info("PHASE 3: Generating Node Data")
    logger.info("=" * 60)
    
    # Create symbol to data mapping for quick lookup
    stocks_map = {s["symbol"]: s for s in stocks_data}
    
    # Get pending symbols
    pending = progress_tracker.get_pending(filtered_symbols)
    
    if not pending:
        logger.info("No pending symbols to process!")
        return
    
    logger.info(f"Processing {len(pending)} pending symbols in batches of {batch_size}")
    
    # Process in batches
    total_batches = (len(pending) + batch_size - 1) // batch_size
    
    for batch_num in range(total_batches):
        start_idx = batch_num * batch_size
        end_idx = min(start_idx + batch_size, len(pending))
        batch = pending[start_idx:end_idx]
        
        logger.info(f"\nBatch {batch_num + 1}/{total_batches}: Processing symbols {start_idx + 1}-{end_idx}")
        
        for i, symbol in enumerate(batch):
            stock_data = stocks_map.get(symbol)
            
            if not stock_data:
                logger.warning(f"No data found for symbol: {symbol}, skipping")
                progress_tracker.mark_failed(symbol, "No stock data available")
                continue
            
            company_name = stock_data.get("name", symbol)
            sector_info = stock_data.get("sector")
            
            try:
                logger.info(f"[{i + 1}/{len(batch)}] Generating data for {symbol} ({company_name})")
                
                # Generate node data
                node_data = generator.generate(
                    symbol=symbol,
                    company_name=company_name,
                    sector_info=sector_info
                )
                
                # Mark as completed
                progress_tracker.mark_completed(symbol, node_data)
                
                logger.info(f"✓ Successfully generated data for {symbol}")
                
                # Small delay to avoid rate limiting
                time.sleep(0.5)
                
            except Exception as e:
                logger.error(f"✗ Failed to generate data for {symbol}: {e}")
                progress_tracker.mark_failed(symbol, str(e))
                continue
        
        # Save progress after each batch
        progress_tracker.save()
        stats = progress_tracker.get_statistics()
        logger.info(
            f"Batch complete. Progress: {stats['processed']}/{stats['total']} "
            f"({stats['completion_rate']:.1f}%), "
            f"Failed: {stats['failed']}, "
            f"Pending: {stats['pending']}"
        )


def output_phase(progress_tracker: ProgressTracker, output_dir: str = "output") -> None:
    """
    Export final results to output files.
    
    Args:
        progress_tracker: ProgressTracker instance
        output_dir: Output directory path
    """
    logger.info("=" * 60)
    logger.info("PHASE 4: Exporting Results")
    logger.info("=" * 60)
    
    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Get all results
    results = progress_tracker.get_results()
    
    if not results:
        logger.warning("No results to export!")
        return
    
    # Export as JSON array
    output_file = output_path / f"nodes_{len(results)}_items.json"
    
    try:
        results_dicts = [node.to_dict() for node in results]
        
        with open(output_file, "w") as f:
            json.dump(results_dicts, f, indent=2)
        
        logger.info(f"✓ Exported {len(results)} nodes to {output_file}")
        
        # Also export statistics
        stats = progress_tracker.get_statistics()
        stats_file = output_path / "generation_stats.json"
        
        with open(stats_file, "w") as f:
            json.dump(stats, f, indent=2)
        
        logger.info(f"✓ Exported statistics to {stats_file}")
        
        # Print summary
        logger.info("\n" + "=" * 60)
        logger.info("GENERATION COMPLETE")
        logger.info("=" * 60)
        logger.info(f"Total processed: {stats['processed']}")
        logger.info(f"Failed: {stats['failed']}")
        logger.info(f"Success rate: {stats['completion_rate']:.1f}%")
        logger.info(f"Output file: {output_file}")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"Failed to export results: {e}")


def main(
    resume: bool = False,
    batch_size: int = 50,
    output_dir: str = "output",
    force_refresh: bool = False,
    test_mode: bool = False,
    excel_file: str = "stocks.xlsx",
    sector: Optional[str] = None
) -> None:
    """
    Main pipeline execution.
    
    Args:
        resume: Resume from progress file
        batch_size: Batch size for processing
        output_dir: Output directory
        force_refresh: Force refresh of cached data
        test_mode: Test mode (process only first 20 stocks)
        excel_file: Path to Excel file containing stock data
        sector: Optional sector name to filter stocks (e.g., "Technology", "Healthcare")
    """
    try:
        # Load configuration
        logger.info("Loading configuration...")
        config = load_config()
        logger.info(f"Using LLM provider: {config['llm_provider']}")
        
        # Initialize components
        logger.info("Initializing components...")
        llm_client = get_llm_client(config)
        data_fetcher = DataFetcher(excel_file=excel_file)
        filter_obj = Filter()
        generator = NodeGenerator(llm_client)
        progress_tracker = ProgressTracker()
        
        # Load existing progress if resuming
        if resume:
            logger.info("Resuming from previous progress...")
            progress_tracker.load()
        
        # Phase 1: Fetch
        stocks = fetch_phase(data_fetcher, force_refresh=force_refresh, sector=sector)
        
        if test_mode:
            logger.info("TEST MODE: Limiting to first 20 stocks")
            stocks = stocks[:20]
        
        # Phase 2: Filter
        filtered_symbols = filter_phase(
            filter_obj, stocks, progress_tracker, force_refresh=force_refresh
        )
        
        if not filtered_symbols:
            logger.error("No stocks passed the filter!")
            return
        
        # Phase 3: Generate
        generate_phase(
            generator, filtered_symbols, stocks, progress_tracker, batch_size
        )
        
        # Phase 4: Output
        output_phase(progress_tracker, output_dir)
        
    except KeyboardInterrupt:
        logger.info("\n\nInterrupted by user. Progress has been saved.")
        logger.info("Run with --resume to continue from where you left off.")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Pipeline failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate node data for project1")
    parser.add_argument(
        "--resume",
        action="store_true",
        help="Resume from previous progress"
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=50,
        help="Batch size for processing (default: 50)"
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="output",
        help="Output directory (default: output)"
    )
    parser.add_argument(
        "--force-refresh",
        action="store_true",
        help="Force refresh of cached data"
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help="Test mode: process only first 20 stocks"
    )
    parser.add_argument(
        "--excel-file",
        type=str,
        default="stocks.xlsx",
        help="Path to Excel file containing stock data (default: stocks.xlsx)"
    )
    parser.add_argument(
        "--sector",
        type=str,
        default=None,
        help="Filter stocks by sector (e.g., Technology, Healthcare, Financials)"
    )
    
    args = parser.parse_args()
    
    main(
        resume=args.resume,
        batch_size=args.batch_size,
        output_dir=args.output_dir,
        force_refresh=args.force_refresh,
        test_mode=args.test,
        excel_file=args.excel_file,
        sector=args.sector
    )

