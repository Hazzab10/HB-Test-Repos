#!/usr/bin/env python3
"""
RNS Announcement Checker

Checks for RNS announcements based on your ADVFN portfolio positions.

Usage:
    python rns_checker.py                    # Check using ADVFN positions
    python rns_checker.py --file positions.txt  # Check using file
    python rns_checker.py --symbols VOD LLOY BP  # Check specific symbols
    python rns_checker.py --hours 48         # Check last 48 hours
    python rns_checker.py --watch            # Continuous monitoring mode
"""

import argparse
import sys
import time
from datetime import datetime

from advfn_scraper import ADVFNScraper, Position, load_positions_from_file
from rns_fetcher import RNSFetcher, RNSAnnouncement, categorize_announcement

try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.live import Live
    from rich import box
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False


def print_simple(announcements: list[RNSAnnouncement], positions: list[Position]):
    """Simple text output when rich is not available."""
    print(f"\n{'='*70}")
    print(f"RNS ANNOUNCEMENT CHECKER - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"{'='*70}")

    print(f"\nMonitoring {len(positions)} positions:")
    for pos in positions:
        print(f"  - {pos.symbol}: {pos.name}")

    print(f"\n{'-'*70}")
    print(f"Found {len(announcements)} announcements:")
    print(f"{'-'*70}\n")

    if not announcements:
        print("No recent announcements found.")
        return

    for ann in announcements:
        category = categorize_announcement(ann.title)
        age = ann.age_hours

        if age < 1:
            age_str = f"{int(age * 60)}m ago"
        elif age < 24:
            age_str = f"{int(age)}h ago"
        else:
            age_str = ann.date.strftime("%Y-%m-%d")

        print(f"[{ann.symbol}] {ann.title}")
        print(f"    Category: {category} | Source: {ann.source} | {age_str}")
        print(f"    URL: {ann.url}")
        print()


def print_rich(announcements: list[RNSAnnouncement], positions: list[Position]):
    """Rich formatted output with colors and tables."""
    console = Console()

    # Header
    console.print()
    console.print(Panel.fit(
        f"[bold cyan]RNS Announcement Checker[/bold cyan]\n"
        f"[dim]{datetime.now().strftime('%Y-%m-%d %H:%M')}[/dim]",
        border_style="cyan"
    ))

    # Positions summary
    symbols = ", ".join([p.symbol for p in positions])
    console.print(f"\n[bold]Monitoring {len(positions)} positions:[/bold] {symbols}\n")

    if not announcements:
        console.print("[yellow]No recent announcements found.[/yellow]")
        return

    # Announcements table
    table = Table(
        title=f"[bold green]Found {len(announcements)} Announcements[/bold green]",
        box=box.ROUNDED,
        show_header=True,
        header_style="bold white"
    )

    table.add_column("Time", style="dim", width=12)
    table.add_column("Symbol", style="cyan", width=8)
    table.add_column("Category", style="yellow", width=14)
    table.add_column("Title", style="white", max_width=50)
    table.add_column("Source", style="dim", width=12)

    for ann in announcements:
        category = categorize_announcement(ann.title)
        age = ann.age_hours

        # Format time
        if age < 1:
            time_str = f"[bold red]{int(age * 60)}m ago[/bold red]"
        elif age < 6:
            time_str = f"[bold yellow]{int(age)}h ago[/bold yellow]"
        elif age < 24:
            time_str = f"{int(age)}h ago"
        else:
            time_str = ann.date.strftime("%d/%m %H:%M")

        # Highlight important categories
        if category in ["Results", "Trading Update", "M&A"]:
            category_str = f"[bold]{category}[/bold]"
        else:
            category_str = category

        table.add_row(
            time_str,
            ann.symbol,
            category_str,
            ann.title[:50] + "..." if len(ann.title) > 50 else ann.title,
            ann.source
        )

    console.print(table)

    # Print URLs separately
    console.print("\n[bold]Announcement URLs:[/bold]")
    for i, ann in enumerate(announcements[:10], 1):
        console.print(f"  {i}. [link={ann.url}]{ann.url}[/link]")

    if len(announcements) > 10:
        console.print(f"  ... and {len(announcements) - 10} more")


def watch_mode(positions: list[Position], interval: int = 300, hours: int = 24):
    """
    Continuous monitoring mode.

    Args:
        positions: List of positions to monitor.
        interval: Check interval in seconds (default 5 minutes).
        hours: How many hours back to check.
    """
    fetcher = RNSFetcher()
    symbols = [p.symbol for p in positions]
    seen_announcements = set()

    print(f"\n{'='*60}")
    print("WATCH MODE - Monitoring for new RNS announcements")
    print(f"Checking every {interval // 60} minutes")
    print(f"Positions: {', '.join(symbols)}")
    print(f"Press Ctrl+C to stop")
    print(f"{'='*60}\n")

    try:
        while True:
            try:
                announcements = fetcher.get_announcements(symbols, hours=hours)

                # Filter to only new announcements
                new_announcements = []
                for ann in announcements:
                    key = (ann.symbol, ann.title, ann.date.isoformat())
                    if key not in seen_announcements:
                        seen_announcements.add(key)
                        new_announcements.append(ann)

                if new_announcements:
                    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] "
                          f"*** {len(new_announcements)} NEW ANNOUNCEMENT(S) ***\n")

                    for ann in new_announcements:
                        category = categorize_announcement(ann.title)
                        print(f"  [{ann.symbol}] {ann.title}")
                        print(f"      Category: {category}")
                        print(f"      URL: {ann.url}")
                        print()

                    # System notification (optional)
                    try:
                        import subprocess
                        for ann in new_announcements[:3]:  # Limit notifications
                            subprocess.run([
                                'notify-send',
                                f'RNS: {ann.symbol}',
                                ann.title[:100]
                            ], check=False, capture_output=True)
                    except Exception:
                        pass  # Notifications not available

                else:
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] No new announcements. "
                          f"Next check in {interval // 60} minutes.")

            except Exception as e:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] Error: {e}")

            time.sleep(interval)

    except KeyboardInterrupt:
        print("\n\nWatch mode stopped.")


def main():
    parser = argparse.ArgumentParser(
        description="Check for RNS announcements based on your ADVFN positions",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                           Check using ADVFN portfolio
  %(prog)s --symbols VOD LLOY        Check specific symbols
  %(prog)s --file positions.txt      Load positions from file
  %(prog)s --hours 48                Check last 48 hours
  %(prog)s --watch                   Continuous monitoring mode
  %(prog)s --watch --interval 10     Check every 10 minutes

Position file format (one per line):
  VOD,Vodafone Group
  LLOY,Lloyds Banking Group
  BP
        """
    )

    # Input options
    input_group = parser.add_mutually_exclusive_group()
    input_group.add_argument(
        '--symbols', '-s',
        nargs='+',
        help="Stock symbols to check (e.g., VOD LLOY BP)"
    )
    input_group.add_argument(
        '--file', '-f',
        help="File containing positions (one per line: SYMBOL,Name)"
    )

    # Time options
    parser.add_argument(
        '--hours', '-H',
        type=int,
        default=24,
        help="How many hours back to check (default: 24)"
    )

    # Watch mode
    parser.add_argument(
        '--watch', '-w',
        action='store_true',
        help="Enable continuous monitoring mode"
    )
    parser.add_argument(
        '--interval', '-i',
        type=int,
        default=5,
        help="Check interval in minutes for watch mode (default: 5)"
    )

    # Output options
    parser.add_argument(
        '--simple',
        action='store_true',
        help="Use simple text output instead of rich formatting"
    )

    args = parser.parse_args()

    # Get positions
    positions = []

    if args.symbols:
        # Use provided symbols
        positions = [Position(symbol=s.upper(), name=s.upper()) for s in args.symbols]
        print(f"Using {len(positions)} provided symbols")

    elif args.file:
        # Load from file
        try:
            positions = load_positions_from_file(args.file)
            print(f"Loaded {len(positions)} positions from {args.file}")
        except FileNotFoundError:
            print(f"Error: File not found: {args.file}")
            sys.exit(1)
        except Exception as e:
            print(f"Error loading positions file: {e}")
            sys.exit(1)

    else:
        # Try to fetch from ADVFN
        print("Attempting to fetch positions from ADVFN...")
        scraper = ADVFNScraper()

        if scraper.is_logged_in():
            positions = scraper.get_positions()
            if positions:
                print(f"Found {len(positions)} positions in your ADVFN portfolio")
            else:
                print("No positions found in your ADVFN portfolio.")
                print("You can manually specify symbols with --symbols or use a file with --file")
                sys.exit(1)
        else:
            print("\nNot logged into ADVFN.")
            print("\nOptions:")
            print("  1. Log into ADVFN in your browser, then run this script again")
            print("  2. Use --symbols to specify stocks: python rns_checker.py --symbols VOD LLOY BP")
            print("  3. Use --file with a positions file: python rns_checker.py --file positions.txt")
            print("\nCreate a positions.txt file with one symbol per line:")
            print("  VOD,Vodafone Group")
            print("  LLOY,Lloyds Banking Group")
            print("  BP")
            sys.exit(1)

    if not positions:
        print("No positions to check. Exiting.")
        sys.exit(1)

    # Watch mode
    if args.watch:
        watch_mode(positions, interval=args.interval * 60, hours=args.hours)
        return

    # Single check mode
    print("\nFetching RNS announcements...")
    fetcher = RNSFetcher()
    symbols = [p.symbol for p in positions]
    announcements = fetcher.get_announcements(symbols, hours=args.hours)

    # Output results
    if args.simple or not RICH_AVAILABLE:
        print_simple(announcements, positions)
    else:
        print_rich(announcements, positions)


if __name__ == "__main__":
    main()
