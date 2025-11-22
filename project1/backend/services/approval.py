from __future__ import annotations

import logging
from typing import Optional, Tuple

import yfinance as yf

from backend.domain import Node, NodeRequest
from backend.repositories import DatabaseGraphRepository

logger = logging.getLogger(__name__)


def is_valid_nasdaq_stock(symbol: str) -> Tuple[bool, Optional[str]]:
    """
    Validate if a symbol is a valid NASDAQ stock using yfinance.
    
    Uses `fast_info` to avoid '429 Too Many Requests' rate limiting.
    """
    if not symbol or not isinstance(symbol, str):
        return False, "Stock symbol must be a non-empty string"
    
    symbol = symbol.strip().upper()
    
    # Basic format check: 1-5 uppercase letters
    if not symbol.isalpha() or len(symbol) < 1 or len(symbol) > 5:
        return False, f"Stock symbol '{symbol}' must be 1-5 uppercase letters"
    
    try:
        ticker = yf.Ticker(symbol)
        
        exchange = ticker.fast_info.get('exchange', '').upper()
        quote_type = ticker.fast_info.get('quoteType', '').upper()
        
        # 调试打印：看看 Yahoo 到底返回了啥
        print(f"Ticker: {symbol} | Exchange: {exchange} | Type: {quote_type}")

        # 如果连 exchange 都没有，说明代码根本不存在
        if not exchange:
             return False, f"Stock symbol '{symbol}' not found"

        # NASDAQ 交易所代码列表 (Yahoo Finance 内部代码)
        nasdaq_exchanges = [
            'NMS',      # Nasdaq National Market System (大盘股如 TSLA, AAPL)
            'NGM',      # Nasdaq Global Market
            'NCM',      # Nasdaq Capital Market
            'NASDAQ',   # 标准代码
        ]
        
        # 3. 校验逻辑
        if exchange in nasdaq_exchanges:
            # 严格模式：只允许普通股票 (EQUITY)，拒绝 ETF (如 QQQ)
            if quote_type and quote_type != 'EQUITY':
                # 如果你需要允许 ETF，请注释掉下面这行
                return False, f"Symbol '{symbol}' is {quote_type}, not a common stock"
            
            # Return company name from yfinance if valid
            long_name = ticker.info.get('longName')
            short_name = ticker.info.get('shortName')
            company_name = long_name or short_name
            return True, company_name
            
        # 代码存在，但不在 NASDAQ (比如在 NYSE)
        if exchange:
            return False, f"Stock symbol '{symbol}' is listed on {exchange}, not NASDAQ"
            
        return False, f"Stock symbol '{symbol}' has unknown exchange data"

    except KeyError as e:
        # yfinance internal error when data is missing (e.g. 'currentTradingPeriod')
        # treat this as symbol not found
        logger.warning(f"yfinance data missing for '{symbol}': {e}")
        return False, f"Stock symbol '{symbol}' not found"

    except Exception as e:
        # ✅ 修复：加上 "as e" 确保能打印出具体错误
        error_str = str(e)
        
        # 虽然 fast_info 很少触发 429，但还是防一手
        if '429' in error_str or 'Too Many Requests' in error_str:
            logger.warning(f"Rate limit hit while validating '{symbol}'.")
            return False, "System busy (Rate Limit), please try again later."
            
        logger.error(f"Error validating stock symbol '{symbol}': {error_str}")
        # 返回具体的错误信息方便调试
        return False, f"System error validating '{symbol}': {error_str}"


def approve_node_request(
    node_request: NodeRequest,
    user: Optional[dict],
    repository: DatabaseGraphRepository,
) -> Tuple[str, Optional[str], Optional[Node]]:
    """
    Automatically approve or reject a node request based on business rules.
    """
    # 1. Check if node_id already exists (Pre-check to save API calls)
    existing_node = repository.get_node(node_request.node_id)
    if existing_node:
        return (
            "rejected",
            f"Node with ID '{node_request.node_id}' already exists",
            None,
        )

    # 2. Check user authentication
    if user is None:
        return ("rejected", "User must be authenticated to create nodes", None)
    
    # 3. Check node type
    if node_request.node_type != "company":
        return (
            "rejected",
            f"Only 'company' type nodes are allowed. Requested type: '{node_request.node_type}'",
            None,
        )
    
    # 4. Check if node_id is a valid NASDAQ stock symbol
    is_valid, company_name_or_error = is_valid_nasdaq_stock(node_request.node_id)
    
    if not is_valid:
        # 使用返回的具体错误信息，而不是笼统的 invalid
        return ("rejected", company_name_or_error, None)
    
    # 5. All checks passed - create the node
    # Use company name from yfinance if available and user didn't provide a label (or to overwrite it)
    # Current logic: If yfinance found a name, use it to overwrite the user provided label or fill it if empty.
    # Since user input might be generic, using official name is better.
    final_label = company_name_or_error if company_name_or_error else node_request.label

    node = Node(
        id=node_request.node_id,
        type=node_request.node_type,
        label=final_label,
        description=node_request.description,
        sector=node_request.sector,
        color=node_request.color,
        metadata=node_request.metadata,
        position=None,  # Position calculated dynamically, not stored
    )
    
    # Assume create_node handles the DB insertion
    created_node = repository.create_node(node)
    
    return ("approved", None, created_node)