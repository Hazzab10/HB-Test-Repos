"""
ADVFN Portfolio Scraper Module

Fetches your stock positions from ADVFN using browser cookies for authentication.
"""

import re
from typing import Optional
from dataclasses import dataclass

import requests
from bs4 import BeautifulSoup

try:
    import browser_cookie3
except ImportError:
    browser_cookie3 = None


@dataclass
class Position:
    """Represents a stock position."""
    symbol: str
    name: str
    exchange: str = "LSE"
    quantity: Optional[float] = None

    def __str__(self):
        return f"{self.symbol} ({self.name})"


class ADVFNScraper:
    """Scrapes portfolio positions from ADVFN."""

    PORTFOLIO_URL = "https://uk.advfn.com/p.php?pid=portfolio"
    BASE_URL = "https://uk.advfn.com"

    def __init__(self, cookies: Optional[dict] = None):
        """
        Initialize the scraper.

        Args:
            cookies: Optional dict of cookies. If not provided, will attempt
                    to load from browser.
        """
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-GB,en;q=0.5',
        })

        if cookies:
            self.session.cookies.update(cookies)
        else:
            self._load_browser_cookies()

    def _load_browser_cookies(self):
        """Attempt to load cookies from installed browsers."""
        if browser_cookie3 is None:
            print("Warning: browser_cookie3 not installed. Cannot auto-load cookies.")
            return

        browsers = [
            ('Chrome', browser_cookie3.chrome),
            ('Firefox', browser_cookie3.firefox),
            ('Edge', browser_cookie3.edge),
            ('Opera', browser_cookie3.opera),
        ]

        for name, loader in browsers:
            try:
                cookies = loader(domain_name='.advfn.com')
                self.session.cookies.update(cookies)
                print(f"Loaded cookies from {name}")
                return
            except Exception:
                continue

        print("Warning: Could not load cookies from any browser. You may need to provide them manually.")

    def is_logged_in(self) -> bool:
        """Check if we're logged into ADVFN."""
        response = self.session.get(self.PORTFOLIO_URL, allow_redirects=False)
        # If redirected to login page, we're not logged in
        if response.status_code == 302:
            return False
        if 'login' in response.url.lower():
            return False
        return 'portfolio' in response.text.lower() or 'my positions' in response.text.lower()

    def get_positions(self) -> list[Position]:
        """
        Fetch all positions from the ADVFN portfolio.

        Returns:
            List of Position objects.
        """
        positions = []

        # Try the main portfolio page
        response = self.session.get(self.PORTFOLIO_URL)

        if response.status_code != 200:
            print(f"Error fetching portfolio: HTTP {response.status_code}")
            return positions

        soup = BeautifulSoup(response.text, 'html.parser')

        # ADVFN portfolio page structure - look for stock symbols
        # They typically appear in links with specific patterns

        # Pattern 1: Look for links to quote pages
        quote_links = soup.find_all('a', href=re.compile(r'/p\.php\?pid=qkquote.*symbol='))
        for link in quote_links:
            href = link.get('href', '')
            symbol_match = re.search(r'symbol=([A-Z0-9^:]+)', href)
            if symbol_match:
                raw_symbol = symbol_match.group(1)
                # Parse exchange:symbol format (e.g., "LSE:VOD" or "L^VOD")
                symbol, exchange = self._parse_symbol(raw_symbol)
                name = link.get_text(strip=True) or symbol

                # Avoid duplicates
                if not any(p.symbol == symbol for p in positions):
                    positions.append(Position(
                        symbol=symbol,
                        name=name,
                        exchange=exchange
                    ))

        # Pattern 2: Look for table rows with stock data
        tables = soup.find_all('table')
        for table in tables:
            rows = table.find_all('tr')
            for row in rows:
                cells = row.find_all(['td', 'th'])
                for cell in cells:
                    # Look for ticker symbols (typically uppercase, 2-5 chars)
                    text = cell.get_text(strip=True)
                    if re.match(r'^[A-Z]{2,5}$', text):
                        links = cell.find_all('a')
                        if links:
                            name = text
                            # Try to get full company name from title or nearby cells
                            title = links[0].get('title', '')
                            if title:
                                name = title

                            if not any(p.symbol == text for p in positions):
                                positions.append(Position(
                                    symbol=text,
                                    name=name,
                                    exchange="LSE"
                                ))

        return positions

    def _parse_symbol(self, raw_symbol: str) -> tuple[str, str]:
        """
        Parse a raw symbol string into (symbol, exchange).

        Examples:
            "LSE:VOD" -> ("VOD", "LSE")
            "L^VOD" -> ("VOD", "LSE")
            "VOD" -> ("VOD", "LSE")
        """
        # Handle colon format
        if ':' in raw_symbol:
            parts = raw_symbol.split(':')
            return parts[1], parts[0]

        # Handle caret format (L^VOD = London Stock Exchange)
        if '^' in raw_symbol:
            parts = raw_symbol.split('^')
            exchange_map = {'L': 'LSE', 'N': 'NYSE', 'O': 'NASDAQ', 'A': 'AIM'}
            exchange = exchange_map.get(parts[0], parts[0])
            return parts[1], exchange

        # Default to LSE
        return raw_symbol, "LSE"


def load_positions_from_file(filepath: str) -> list[Position]:
    """
    Load positions from a simple text file.

    File format (one per line):
        SYMBOL,Company Name
        or just:
        SYMBOL

    Args:
        filepath: Path to the positions file.

    Returns:
        List of Position objects.
    """
    positions = []

    with open(filepath, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue

            if ',' in line:
                parts = line.split(',', 1)
                symbol = parts[0].strip().upper()
                name = parts[1].strip()
            else:
                symbol = line.upper()
                name = symbol

            positions.append(Position(symbol=symbol, name=name))

    return positions


if __name__ == "__main__":
    # Test the scraper
    scraper = ADVFNScraper()

    if scraper.is_logged_in():
        print("Successfully connected to ADVFN")
        positions = scraper.get_positions()
        print(f"\nFound {len(positions)} positions:")
        for pos in positions:
            print(f"  - {pos}")
    else:
        print("Not logged into ADVFN. Please log in via your browser first.")
