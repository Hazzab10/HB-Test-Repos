"""
RNS Announcement Fetcher Module

Fetches RNS (Regulatory News Service) announcements from multiple sources:
- London Stock Exchange
- Investegate
- ADVFN
"""

import re
from datetime import datetime, timedelta
from typing import Optional
from dataclasses import dataclass, field

import requests
from bs4 import BeautifulSoup
from dateutil import parser as date_parser


@dataclass
class RNSAnnouncement:
    """Represents an RNS announcement."""
    symbol: str
    title: str
    date: datetime
    source: str
    url: str
    category: str = ""
    is_regulatory: bool = True

    def __str__(self):
        date_str = self.date.strftime("%Y-%m-%d %H:%M")
        return f"[{date_str}] {self.symbol}: {self.title}"

    @property
    def age_hours(self) -> float:
        """Return age of announcement in hours."""
        return (datetime.now() - self.date).total_seconds() / 3600

    @property
    def is_today(self) -> bool:
        """Check if announcement was today."""
        return self.date.date() == datetime.now().date()


class RNSFetcher:
    """Fetches RNS announcements from multiple sources."""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-GB,en;q=0.5',
        })

    def get_announcements(self, symbols: list[str], hours: int = 24) -> list[RNSAnnouncement]:
        """
        Get RNS announcements for the given symbols.

        Args:
            symbols: List of stock symbols to check.
            hours: How many hours back to check (default 24).

        Returns:
            List of RNSAnnouncement objects, sorted by date (newest first).
        """
        all_announcements = []
        cutoff = datetime.now() - timedelta(hours=hours)

        for symbol in symbols:
            # Try multiple sources
            announcements = []

            # Try LSE
            try:
                lse_announcements = self._fetch_lse(symbol, cutoff)
                announcements.extend(lse_announcements)
            except Exception as e:
                print(f"Warning: LSE fetch failed for {symbol}: {e}")

            # Try Investegate
            try:
                investegate_announcements = self._fetch_investegate(symbol, cutoff)
                announcements.extend(investegate_announcements)
            except Exception as e:
                print(f"Warning: Investegate fetch failed for {symbol}: {e}")

            # Try ADVFN
            try:
                advfn_announcements = self._fetch_advfn(symbol, cutoff)
                announcements.extend(advfn_announcements)
            except Exception as e:
                print(f"Warning: ADVFN fetch failed for {symbol}: {e}")

            all_announcements.extend(announcements)

        # Remove duplicates (same symbol + title + similar time)
        unique = self._deduplicate(all_announcements)

        # Sort by date, newest first
        unique.sort(key=lambda x: x.date, reverse=True)

        return unique

    def _fetch_lse(self, symbol: str, cutoff: datetime) -> list[RNSAnnouncement]:
        """Fetch announcements from London Stock Exchange."""
        announcements = []

        # LSE news page URL
        url = f"https://www.londonstockexchange.com/news?tab=news-explorer&filter={symbol}"

        try:
            response = self.session.get(url, timeout=10)
            if response.status_code != 200:
                return announcements

            soup = BeautifulSoup(response.text, 'html.parser')

            # Look for news items
            news_items = soup.find_all(['article', 'div'], class_=re.compile(r'news|announcement', re.I))

            for item in news_items:
                # Extract title
                title_elem = item.find(['h2', 'h3', 'a', 'span'], class_=re.compile(r'title|headline', re.I))
                if not title_elem:
                    continue
                title = title_elem.get_text(strip=True)

                # Extract date
                date_elem = item.find(['time', 'span'], class_=re.compile(r'date|time', re.I))
                if date_elem:
                    try:
                        date_str = date_elem.get('datetime') or date_elem.get_text(strip=True)
                        date = date_parser.parse(date_str, fuzzy=True)
                    except Exception:
                        date = datetime.now()
                else:
                    date = datetime.now()

                if date < cutoff:
                    continue

                # Extract URL
                link = item.find('a', href=True)
                item_url = link['href'] if link else url
                if not item_url.startswith('http'):
                    item_url = f"https://www.londonstockexchange.com{item_url}"

                announcements.append(RNSAnnouncement(
                    symbol=symbol,
                    title=title,
                    date=date,
                    source="LSE",
                    url=item_url
                ))

        except Exception as e:
            pass

        return announcements

    def _fetch_investegate(self, symbol: str, cutoff: datetime) -> list[RNSAnnouncement]:
        """Fetch announcements from Investegate."""
        announcements = []

        # Investegate search URL
        url = f"https://www.investegate.co.uk/Index.aspx?searchtype=3&words={symbol}"

        try:
            response = self.session.get(url, timeout=10)
            if response.status_code != 200:
                return announcements

            soup = BeautifulSoup(response.text, 'html.parser')

            # Look for announcement rows
            rows = soup.find_all('tr')

            for row in rows:
                cells = row.find_all('td')
                if len(cells) < 3:
                    continue

                # Check if this row contains our symbol
                row_text = row.get_text()
                if symbol.upper() not in row_text.upper():
                    continue

                # Try to extract announcement details
                link = row.find('a', href=re.compile(r'Article', re.I))
                if not link:
                    continue

                title = link.get_text(strip=True)

                # Find date cell
                date = None
                for cell in cells:
                    cell_text = cell.get_text(strip=True)
                    try:
                        date = date_parser.parse(cell_text, fuzzy=True, dayfirst=True)
                        if date.year > 2000:  # Sanity check
                            break
                    except Exception:
                        continue

                if not date:
                    date = datetime.now()

                if date < cutoff:
                    continue

                item_url = link.get('href', '')
                if not item_url.startswith('http'):
                    item_url = f"https://www.investegate.co.uk/{item_url}"

                announcements.append(RNSAnnouncement(
                    symbol=symbol,
                    title=title,
                    date=date,
                    source="Investegate",
                    url=item_url
                ))

        except Exception as e:
            pass

        return announcements

    def _fetch_advfn(self, symbol: str, cutoff: datetime) -> list[RNSAnnouncement]:
        """Fetch announcements from ADVFN."""
        announcements = []

        # ADVFN news URL for LSE stocks
        url = f"https://uk.advfn.com/stock-market/london/{symbol}/news/rns"

        try:
            response = self.session.get(url, timeout=10)
            if response.status_code != 200:
                return announcements

            soup = BeautifulSoup(response.text, 'html.parser')

            # Look for news table rows
            news_table = soup.find('table', class_=re.compile(r'news', re.I))
            if news_table:
                rows = news_table.find_all('tr')
            else:
                rows = soup.find_all('tr')

            for row in rows:
                # Skip header rows
                if row.find('th'):
                    continue

                cells = row.find_all('td')
                if len(cells) < 2:
                    continue

                # Look for link to news article
                link = row.find('a', href=re.compile(r'news|announcement', re.I))
                if not link:
                    # Try any link in the row
                    link = row.find('a', href=True)

                if not link:
                    continue

                title = link.get_text(strip=True)
                if not title or len(title) < 5:
                    continue

                # Extract date
                date = None
                for cell in cells:
                    cell_text = cell.get_text(strip=True)
                    # Look for date patterns
                    if re.search(r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}', cell_text):
                        try:
                            date = date_parser.parse(cell_text, fuzzy=True, dayfirst=True)
                            break
                        except Exception:
                            continue
                    elif re.search(r'\d{1,2}:\d{2}', cell_text):
                        # Time only - assume today
                        try:
                            time_part = date_parser.parse(cell_text, fuzzy=True)
                            date = datetime.now().replace(
                                hour=time_part.hour,
                                minute=time_part.minute,
                                second=0, microsecond=0
                            )
                            break
                        except Exception:
                            continue

                if not date:
                    date = datetime.now()

                if date < cutoff:
                    continue

                item_url = link.get('href', '')
                if not item_url.startswith('http'):
                    item_url = f"https://uk.advfn.com{item_url}"

                announcements.append(RNSAnnouncement(
                    symbol=symbol,
                    title=title,
                    date=date,
                    source="ADVFN",
                    url=item_url
                ))

        except Exception as e:
            pass

        return announcements

    def _deduplicate(self, announcements: list[RNSAnnouncement]) -> list[RNSAnnouncement]:
        """Remove duplicate announcements."""
        seen = set()
        unique = []

        for ann in announcements:
            # Create a key based on symbol, title similarity, and rough time
            # Normalize title for comparison
            title_normalized = re.sub(r'\s+', ' ', ann.title.lower().strip())
            title_key = title_normalized[:50]  # First 50 chars
            date_key = ann.date.strftime("%Y-%m-%d %H")  # Hour precision

            key = (ann.symbol.upper(), title_key, date_key)

            if key not in seen:
                seen.add(key)
                unique.append(ann)

        return unique


def categorize_announcement(title: str) -> str:
    """
    Categorize an RNS announcement based on its title.

    Returns category like: "Results", "Trading Update", "Director Dealing", etc.
    """
    title_lower = title.lower()

    categories = [
        (["result", "earning", "profit", "loss", "revenue"], "Results"),
        (["trading update", "trading statement"], "Trading Update"),
        (["director", "pdmr"], "Director Dealing"),
        (["dividend"], "Dividend"),
        (["acquisition", "merger", "takeover"], "M&A"),
        (["share buyback", "repurchase"], "Buyback"),
        (["agm", "annual general"], "AGM"),
        (["placing", "fundrais", "equity raise"], "Fundraising"),
        (["contract", "award", "order"], "Contract"),
        (["board change", "appointment", "resignation"], "Board Change"),
        (["holding", "tr-1", "major shareholder"], "Holdings"),
    ]

    for keywords, category in categories:
        if any(kw in title_lower for kw in keywords):
            return category

    return "General"


if __name__ == "__main__":
    # Test the fetcher
    fetcher = RNSFetcher()

    test_symbols = ["VOD", "LLOY", "BP"]
    print(f"Fetching RNS announcements for: {', '.join(test_symbols)}")

    announcements = fetcher.get_announcements(test_symbols, hours=72)

    print(f"\nFound {len(announcements)} announcements:")
    for ann in announcements[:10]:  # Show first 10
        category = categorize_announcement(ann.title)
        print(f"  [{category}] {ann}")
