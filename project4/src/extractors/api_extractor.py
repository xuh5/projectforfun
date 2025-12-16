"""API-based extractors for fetching data from web APIs."""

from typing import Iterator, Dict, Any, Optional, List
import logging
import time

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

from ..core import Extractor


logger = logging.getLogger(__name__)


class APIExtractor(Extractor):
    """
    Base class for API extractors.
    
    Config options:
        - url: str - API endpoint URL
        - headers: Dict[str, str] - HTTP headers
        - params: Dict[str, Any] - Query parameters
        - timeout: int - Request timeout in seconds (default: 30)
        - retry_count: int - Number of retries on failure (default: 3)
        - retry_delay: float - Delay between retries in seconds (default: 1)
    """
    
    def __init__(
        self,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
        timeout: int = 30,
        retry_count: int = 3,
        retry_delay: float = 1.0,
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize API extractor.
        
        Args:
            url: API endpoint URL
            headers: HTTP headers
            params: Query parameters
            timeout: Request timeout
            retry_count: Number of retries
            retry_delay: Delay between retries
            config: Additional configuration
        """
        if not HAS_REQUESTS:
            raise ImportError("requests library is required for APIExtractor. Install with: pip install requests")
        
        super().__init__(config)
        self.url = url
        self.headers = headers or {}
        self.params = params or {}
        self.timeout = timeout
        self.retry_count = retry_count
        self.retry_delay = retry_delay
    
    def extract(self) -> Iterator[Dict[str, Any]]:
        """Extract data from API."""
        logger.info(f"Extracting from API: {self.url}")
        
        data = self._fetch_data()
        
        # Handle different response structures
        if isinstance(data, dict):
            # Single record
            yield data
        elif isinstance(data, list):
            # Array of records
            for idx, record in enumerate(data):
                if isinstance(record, dict):
                    record['_source_index'] = idx
                    yield record
                else:
                    logger.warning(f"Skipping non-dict record at index {idx}")
        else:
            raise ValueError(f"Unexpected API response type: {type(data)}")
    
    def _fetch_data(self) -> Any:
        """Fetch data from API with retry logic."""
        last_error = None
        
        for attempt in range(self.retry_count + 1):
            try:
                response = requests.get(
                    self.url,
                    headers=self.headers,
                    params=self.params,
                    timeout=self.timeout
                )
                response.raise_for_status()
                return response.json()
                
            except requests.RequestException as e:
                last_error = e
                if attempt < self.retry_count:
                    logger.warning(f"API request failed (attempt {attempt + 1}/{self.retry_count + 1}): {e}")
                    time.sleep(self.retry_delay)
                else:
                    logger.error(f"API request failed after {self.retry_count + 1} attempts")
        
        raise last_error


class RESTAPIExtractor(APIExtractor):
    """
    REST API extractor with pagination support.
    
    Config options:
        - pagination_type: str - 'offset', 'cursor', or 'page' (default: 'offset')
        - page_size: int - Number of records per page (default: 100)
        - max_pages: int - Maximum pages to fetch (default: None = unlimited)
        - data_path: str - JSON path to records in response (e.g., 'data.items')
        - next_page_path: str - JSON path to next page indicator
    """
    
    def __init__(
        self,
        url: str,
        pagination_type: str = 'offset',
        page_size: int = 100,
        max_pages: Optional[int] = None,
        data_path: Optional[str] = None,
        next_page_path: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
        timeout: int = 30,
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize REST API extractor.
        
        Args:
            url: API endpoint URL
            pagination_type: Type of pagination ('offset', 'cursor', 'page')
            page_size: Records per page
            max_pages: Maximum pages to fetch
            data_path: Path to records in response
            next_page_path: Path to next page indicator
            headers: HTTP headers
            params: Query parameters
            timeout: Request timeout
            config: Additional configuration
        """
        super().__init__(url, headers, params, timeout, config=config)
        self.pagination_type = pagination_type
        self.page_size = page_size
        self.max_pages = max_pages
        self.data_path = data_path
        self.next_page_path = next_page_path
    
    def extract(self) -> Iterator[Dict[str, Any]]:
        """Extract data with pagination support."""
        logger.info(f"Extracting from REST API: {self.url}")
        
        page_count = 0
        offset = 0
        cursor = None
        page = 1
        record_index = 0
        
        while True:
            # Check max pages limit
            if self.max_pages and page_count >= self.max_pages:
                logger.info(f"Reached max pages limit: {self.max_pages}")
                break
            
            # Build params for this page
            params = self.params.copy()
            
            if self.pagination_type == 'offset':
                params['limit'] = self.page_size
                params['offset'] = offset
            elif self.pagination_type == 'page':
                params['page_size'] = self.page_size
                params['page'] = page
            elif self.pagination_type == 'cursor' and cursor:
                params['cursor'] = cursor
                params['limit'] = self.page_size
            
            # Fetch page
            try:
                response = requests.get(
                    self.url,
                    headers=self.headers,
                    params=params,
                    timeout=self.timeout
                )
                response.raise_for_status()
                data = response.json()
            except requests.RequestException as e:
                logger.error(f"Failed to fetch page {page_count + 1}: {e}")
                break
            
            # Extract records from response
            records = self._extract_records(data)
            
            if not records:
                logger.info("No more records found")
                break
            
            # Yield records
            for record in records:
                record['_source_page'] = page_count + 1
                record['_source_index'] = record_index
                record_index += 1
                yield record
            
            # Update pagination vars
            page_count += 1
            offset += len(records)
            page += 1
            
            # Check for next page
            if self.pagination_type == 'cursor':
                cursor = self._get_next_cursor(data)
                if not cursor:
                    break
            elif len(records) < self.page_size:
                # Fewer records than page size means last page
                break
    
    def _extract_records(self, data: Any) -> List[Dict[str, Any]]:
        """Extract records from API response."""
        if self.data_path:
            # Navigate to records using data_path
            current = data
            for key in self.data_path.split('.'):
                if isinstance(current, dict):
                    current = current.get(key, [])
                else:
                    return []
            data = current
        
        if isinstance(data, list):
            return [r for r in data if isinstance(r, dict)]
        elif isinstance(data, dict):
            return [data]
        else:
            return []
    
    def _get_next_cursor(self, data: Dict[str, Any]) -> Optional[str]:
        """Extract next cursor from response."""
        if not self.next_page_path:
            return None
        
        current = data
        for key in self.next_page_path.split('.'):
            if isinstance(current, dict):
                current = current.get(key)
            else:
                return None
        
        return str(current) if current else None

