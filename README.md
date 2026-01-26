# RNS Announcement Checker

A Python tool to check for RNS (Regulatory News Service) announcements based on your ADVFN portfolio positions.

## Features

- **Automatic Position Detection**: Fetches your positions directly from ADVFN using browser cookies
- **Multiple RNS Sources**: Checks London Stock Exchange, Investegate, and ADVFN for announcements
- **Announcement Categorization**: Automatically categorizes announcements (Results, Trading Update, Dividend, etc.)
- **Watch Mode**: Continuous monitoring with desktop notifications
- **Flexible Input**: Use ADVFN positions, manual symbol list, or a positions file

## Installation

```bash
# Install dependencies
pip install -r requirements.txt
```

### Requirements

- Python 3.9+
- `requests` - HTTP requests
- `beautifulsoup4` - HTML parsing
- `browser-cookie3` - Browser cookie extraction (for ADVFN authentication)
- `python-dateutil` - Date parsing
- `rich` - Terminal formatting (optional but recommended)

## Usage

### Basic Usage (with ADVFN)

1. Log into ADVFN in your web browser
2. Run the checker:

```bash
python rns_checker.py
```

The tool will automatically:
- Extract cookies from your browser
- Fetch your portfolio positions from ADVFN
- Check for RNS announcements for each position

### Manual Symbol Input

```bash
# Check specific symbols
python rns_checker.py --symbols VOD LLOY BP GSK

# Check last 48 hours
python rns_checker.py --symbols VOD LLOY --hours 48
```

### Using a Positions File

Create a `positions.txt` file:

```
VOD,Vodafone Group
LLOY,Lloyds Banking Group
BP
GSK,GlaxoSmithKline
HSBA,HSBC Holdings
```

Then run:

```bash
python rns_checker.py --file positions.txt
```

### Watch Mode (Continuous Monitoring)

```bash
# Check every 5 minutes (default)
python rns_checker.py --watch

# Check every 10 minutes
python rns_checker.py --watch --interval 10

# Watch specific symbols
python rns_checker.py --symbols VOD LLOY --watch
```

Press `Ctrl+C` to stop watch mode.

## Command Line Options

| Option | Short | Description |
|--------|-------|-------------|
| `--symbols` | `-s` | Stock symbols to check (space-separated) |
| `--file` | `-f` | Path to positions file |
| `--hours` | `-H` | Hours to look back (default: 24) |
| `--watch` | `-w` | Enable continuous monitoring |
| `--interval` | `-i` | Check interval in minutes (default: 5) |
| `--simple` | | Use plain text output instead of rich formatting |

## Examples

```bash
# Check ADVFN portfolio for last 24 hours
python rns_checker.py

# Check specific symbols for last 72 hours
python rns_checker.py -s VOD LLOY BP -H 72

# Continuous monitoring of specific stocks
python rns_checker.py -s VOD LLOY GSK --watch --interval 5

# Simple text output (no colors/tables)
python rns_checker.py --simple
```

## Announcement Categories

The tool automatically categorizes announcements:

| Category | Keywords |
|----------|----------|
| Results | result, earning, profit, revenue |
| Trading Update | trading update, trading statement |
| Director Dealing | director, PDMR |
| Dividend | dividend |
| M&A | acquisition, merger, takeover |
| Buyback | share buyback, repurchase |
| AGM | agm, annual general |
| Fundraising | placing, fundraising |
| Contract | contract, award, order |
| Board Change | appointment, resignation |
| Holdings | TR-1, major shareholder |

## Troubleshooting

### "Not logged into ADVFN"

1. Open your browser and log into https://uk.advfn.com
2. Make sure you're using a supported browser (Chrome, Firefox, Edge)
3. Try running the script again

If it still doesn't work, use manual input:
```bash
python rns_checker.py --symbols VOD LLOY BP
```

### "browser_cookie3 not installed"

```bash
pip install browser-cookie3
```

### No announcements found

- Try extending the time range: `--hours 72`
- Verify the symbols are correct (use LSE ticker symbols)
- Some stocks may have fewer announcements

## Module Usage

You can also use the modules directly in your own code:

```python
from advfn_scraper import ADVFNScraper, Position
from rns_fetcher import RNSFetcher, categorize_announcement

# Get positions from ADVFN
scraper = ADVFNScraper()
positions = scraper.get_positions()

# Or create positions manually
positions = [
    Position(symbol="VOD", name="Vodafone Group"),
    Position(symbol="LLOY", name="Lloyds Banking Group"),
]

# Fetch announcements
fetcher = RNSFetcher()
symbols = [p.symbol for p in positions]
announcements = fetcher.get_announcements(symbols, hours=24)

# Process announcements
for ann in announcements:
    category = categorize_announcement(ann.title)
    print(f"[{category}] {ann.symbol}: {ann.title}")
    print(f"  URL: {ann.url}")
```

## Data Sources

The tool checks these sources for RNS announcements:

1. **London Stock Exchange** - Official regulatory announcements
2. **Investegate** - RNS aggregator
3. **ADVFN** - Financial data provider

Announcements are deduplicated across sources.

## License

MIT License - Use freely for personal and commercial purposes.

## Disclaimer

This tool is for informational purposes only. Always verify announcements through official sources before making investment decisions. The tool relies on web scraping which may break if websites change their structure.
