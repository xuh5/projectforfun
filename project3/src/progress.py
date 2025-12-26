"""Progress tracking for node generation."""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from .models import NodeData

logger = logging.getLogger(__name__)


class ProgressTracker:
    """Tracks progress of node generation with save/load/resume capability."""
    
    def __init__(self, progress_file: str = "progress.json"):
        """
        Initialize progress tracker.
        
        Args:
            progress_file: Path to progress tracking file
        """
        self.progress_file = Path(progress_file)
        self.progress_data = {
            "all_stocks": [],
            "filtered_stocks": [],
            "processed": {},
            "failed": {},
        }
    
    def load(self) -> Dict:
        """
        Load progress from file.
        
        Returns:
            Progress data dictionary
        """
        if not self.progress_file.exists():
            logger.info("No existing progress file found, starting fresh")
            return self.progress_data
        
        try:
            with open(self.progress_file, "r") as f:
                self.progress_data = json.load(f)
            
            processed_count = len(self.progress_data.get("processed", {}))
            failed_count = len(self.progress_data.get("failed", {}))
            
            logger.info(
                f"Loaded progress: {processed_count} completed, {failed_count} failed"
            )
            return self.progress_data
            
        except Exception as e:
            logger.error(f"Failed to load progress from {self.progress_file}: {e}")
            logger.info("Starting with fresh progress")
            return self.progress_data
    
    def save(self, progress_data: Optional[Dict] = None) -> None:
        """
        Save progress to file.
        
        Args:
            progress_data: Optional progress data to save (uses instance data if not provided)
        """
        if progress_data is not None:
            self.progress_data = progress_data
        
        try:
            # Create parent directory if it doesn't exist
            self.progress_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.progress_file, "w") as f:
                json.dump(self.progress_data, f, indent=2)
            
            processed_count = len(self.progress_data.get("processed", {}))
            failed_count = len(self.progress_data.get("failed", {}))
            
            logger.debug(
                f"Saved progress: {processed_count} completed, {failed_count} failed"
            )
            
        except Exception as e:
            logger.error(f"Failed to save progress to {self.progress_file}: {e}")
    
    def set_stock_lists(self, all_stocks: List[str], filtered_stocks: List[str]) -> None:
        """
        Set the stock lists in progress data.
        
        Args:
            all_stocks: List of all stock symbols
            filtered_stocks: List of filtered stock symbols
        """
        self.progress_data["all_stocks"] = all_stocks
        self.progress_data["filtered_stocks"] = filtered_stocks
        self.save()
    
    def get_pending(self, symbols: List[str]) -> List[str]:
        """
        Get list of symbols that haven't been processed yet.
        
        Args:
            symbols: List of all symbols to check
            
        Returns:
            List of symbols that are pending (not in processed or failed)
        """
        processed = set(self.progress_data.get("processed", {}).keys())
        failed = set(self.progress_data.get("failed", {}).keys())
        completed = processed | failed
        
        pending = [s for s in symbols if s not in completed]
        
        logger.info(
            f"Pending: {len(pending)}, "
            f"Completed: {len(processed)}, "
            f"Failed: {len(failed)}"
        )
        
        return pending
    
    def mark_completed(self, symbol: str, data: NodeData) -> None:
        """
        Mark a symbol as successfully processed.
        
        Args:
            symbol: Stock symbol
            data: Generated NodeData
        """
        self.progress_data.setdefault("processed", {})[symbol] = {
            "status": "completed",
            "data": data.to_dict(),
            "timestamp": datetime.now().isoformat(),
        }
        
        # Remove from failed if it was there (retry success)
        if symbol in self.progress_data.get("failed", {}):
            del self.progress_data["failed"][symbol]
        
        logger.debug(f"Marked {symbol} as completed")
    
    def mark_failed(self, symbol: str, error: str, retry_count: int = 0) -> None:
        """
        Mark a symbol as failed.
        
        Args:
            symbol: Stock symbol
            error: Error message
            retry_count: Number of retry attempts
        """
        self.progress_data.setdefault("failed", {})[symbol] = {
            "status": "failed",
            "error": str(error),
            "retry_count": retry_count,
            "timestamp": datetime.now().isoformat(),
        }
        
        logger.debug(f"Marked {symbol} as failed: {error}")
    
    def get_results(self) -> List[NodeData]:
        """
        Get all successfully processed results.
        
        Returns:
            List of NodeData instances for all completed symbols
        """
        results = []
        
        for symbol, entry in self.progress_data.get("processed", {}).items():
            try:
                node_data = NodeData.from_dict(entry["data"])
                results.append(node_data)
            except Exception as e:
                logger.warning(f"Failed to load result for {symbol}: {e}")
                continue
        
        logger.info(f"Retrieved {len(results)} completed results")
        return results
    
    def get_statistics(self) -> Dict:
        """
        Get progress statistics.
        
        Returns:
            Dictionary with progress statistics
        """
        processed_count = len(self.progress_data.get("processed", {}))
        failed_count = len(self.progress_data.get("failed", {}))
        total_filtered = len(self.progress_data.get("filtered_stocks", []))
        
        pending_count = total_filtered - processed_count - failed_count if total_filtered > 0 else 0
        
        return {
            "total": total_filtered,
            "processed": processed_count,
            "failed": failed_count,
            "pending": pending_count,
            "completion_rate": (
                processed_count / total_filtered * 100
                if total_filtered > 0
                else 0
            ),
        }

