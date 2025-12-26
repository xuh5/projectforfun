# Project3 - Node Data Generator

Generates company node data for project1 using NASDAQ stock information and LLM-powered descriptions.

## Overview

This tool fetches NASDAQ stocks, filters them by criteria, and uses LLM to generate rich node data including:
- Company descriptions (2-3 sentences)
- Primary sector classification
- Multiple sector tags (for metadata)

## Features

- **Multi-LLM Support**: Use OpenAI, Ollama (local/free), or DeepSeek
- **Progress Tracking**: Resume from interruptions, track success/failure
- **Batch Processing**: Process stocks in configurable batches
- **Caching**: Cache fetched data to avoid redundant API calls
- **Flexible Filtering**: Customizable stock filtering (TODO: implement criteria)

## Setup

### 1. Install Dependencies

```bash
cd project3
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate

pip install -r requirements.txt
```

### 2. Configure LLM Provider

Create a `.env` file in the `project3` directory:

**Option A: OpenAI** (Paid)
```env
LLM_PROVIDER=openai
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4o-mini
```

**Option B: Ollama** (Free, Local)
```env
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2
```

Install Ollama: https://ollama.com/download
```bash
ollama pull llama3.2
```

**Option C: DeepSeek** (Very Cheap)
```env
LLM_PROVIDER=deepseek
DEEPSEEK_API_KEY=your_deepseek_api_key_here
DEEPSEEK_MODEL=deepseek-chat
```

## Usage

### Basic Usage (Test Mode)

Test with a small batch (20 stocks):

```bash
python -m src.main --test
```

### Generate Full Dataset

```bash
python -m src.main
```

### Resume After Interruption

```bash
python -m src.main --resume
```

### Custom Batch Size

```bash
python -m src.main --batch-size 100
```

### Custom Output Directory

```bash
python -m src.main --output-dir my_output
```

### Force Refresh Data

Re-fetch stock data and re-filter:

```bash
python -m src.main --force-refresh
```

## CLI Arguments

- `--resume`: Resume from previous progress
- `--batch-size N`: Batch size for processing (default: 50)
- `--output-dir DIR`: Output directory (default: "output")
- `--force-refresh`: Force refresh of cached data
- `--test`: Test mode (process only first 20 stocks)

## Pipeline Stages

### 1. Fetch Phase
- Fetches NASDAQ stock data using yfinance
- Caches to `stock_list.json` for reuse
- Extracts: symbol, company name, sector, industry

### 2. Filter Phase
- Applies filtering criteria (TODO: implement custom logic)
- Currently accepts all stocks with valid data
- Results saved in progress file

### 3. Generate Phase
- Processes stocks in batches
- For each stock, LLM generates:
  - Company description
  - Primary sector
  - Multiple sector tags
- Progress saved after each batch
- Supports resume on interruption

### 4. Output Phase
- Exports to `output/nodes_*.json`
- Format compatible with project1 NodeCreateRequest
- Includes generation statistics

## Output Format

Generated nodes match project1's schema:

```json
{
  "id": "NVDA",
  "type": "company",
  "label": "NVIDIA Corporation",
  "description": "NVIDIA Corporation is a leading technology company...",
  "sector": "Technology",
  "color": null,
  "metadata": {
    "sectors": ["Semiconductor", "AI", "GPU", "Data Center"]
  }
}
```

## File Structure

```
project3/
├── src/
│   ├── models.py         # NodeData dataclass
│   ├── data_fetcher.py   # yfinance integration
│   ├── filter.py         # Stock filtering
│   ├── generator.py      # LLM-powered generation
│   ├── progress.py       # Progress tracking
│   ├── main.py           # CLI entry point
│   ├── config.py         # Configuration loader
│   └── clients/          # LLM clients
├── stock_list.json       # Cached stock data
├── progress.json         # Progress tracking
└── output/               # Generated results
    ├── nodes_*.json      # Node data
    └── generation_stats.json
```

## Progress Tracking

Progress is saved to `progress.json`:

```json
{
  "all_stocks": ["AAPL", "MSFT", ...],
  "filtered_stocks": ["NVDA", "AMD", ...],
  "processed": {
    "NVDA": {
      "status": "completed",
      "data": {...},
      "timestamp": "2024-01-01T10:00:00"
    }
  },
  "failed": {
    "SYMBOL": {
      "status": "failed",
      "error": "...",
      "retry_count": 1
    }
  }
}
```

## Customization

### Implement Custom Filter

Edit `src/filter.py` to add filtering logic:

```python
def filter(self, stocks: List[Dict]) -> List[str]:
    filtered = []
    for stock in stocks:
        # Add your criteria
        if stock.get("sector") in ["Technology", "Communication Services"]:
            if stock.get("marketCap", 0) > 1000000000:  # $1B+
                filtered.append(stock["symbol"])
    return filtered
```

### Customize LLM Prompts

Edit prompts in `src/generator.py`:
- `_build_system_prompt()`: System instructions
- `_build_user_prompt()`: User prompt with context

## Error Handling

- **yfinance errors**: Skips symbol, logs warning
- **LLM errors**: Marks as failed, logs error
- **Network errors**: Retries with exponential backoff
- **Keyboard interrupt**: Saves progress, exits gracefully

## Tips

1. **Start with test mode**: Validate setup with `--test` flag
2. **Monitor progress**: Check `progress.json` for statistics
3. **Resume on interruption**: Use `--resume` to continue
4. **Cost optimization**: Use Ollama for free local generation
5. **Rate limiting**: Adjust batch size if hitting API limits

## Troubleshooting

### "OPENAI_API_KEY is required"
Create `.env` file with your API key.

### "Cannot connect to Ollama"
Make sure Ollama is running: `ollama serve`

### "yfinance fetch failed"
Check internet connection, try with smaller batch.

### Progress file corrupted
Delete `progress.json` and restart (will lose progress).

## Next Steps

1. Implement custom filtering in `src/filter.py`
2. Adjust batch size based on API limits
3. Generate full dataset (may take hours for thousands of stocks)
4. Import generated nodes into project1

## License

For educational and development purposes.

