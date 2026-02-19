#!/usr/bin/env python3
"""
Fetch latest football news from BBC Sport + Sky Sports RSS feeds.
Filters for Premier League team mentions and saves to docs/data/news.json.
Run every 30 minutes via OpenClaw cron.
"""

import json
import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path
from email.utils import parsedate_to_datetime

BASE_DIR = Path(__file__).resolve().parent.parent
OUT_FILE = BASE_DIR / 'docs' / 'data' / 'news.json'
OUT_FILE.parent.mkdir(parents=True, exist_ok=True)

PL_TEAMS = [
    'Arsenal', 'Aston Villa', 'Brentford', 'Brighton', 'Burnley',
    'Chelsea', 'Crystal Palace', 'Everton', 'Fulham', 'Leeds',
    'Liverpool', 'Manchester City', 'Man City', 'Manchester United', 'Man United',
    'Newcastle', 'Nottingham Forest', 'Sunderland', 'Tottenham', 'Spurs',
    'West Ham', 'Wolves', 'Wolverhampton', 'Bournemouth',
    'Premier League', 'Premier League', 'EPL',
]

RSS_FEEDS = [
    {
        'url': 'https://feeds.bbci.co.uk/sport/football/rss.xml',
        'source': 'BBC Sport',
        'source_logo': '🔴',
    },
    {
        'url': 'https://www.theguardian.com/football/rss',
        'source': 'The Guardian',
        'source_logo': '🔵',
    },
]

HEADERS = {'User-Agent': 'Mozilla/5.0 (compatible; KickLabAI/1.0)'}
MRSS_NS = 'http://search.yahoo.com/mrss/'


def parse_rss(feed_info):
    """Fetch and parse an RSS feed, return list of articles."""
    try:
        r = requests.get(feed_info['url'], headers=HEADERS, timeout=10)
        r.raise_for_status()
        root = ET.fromstring(r.content)
        items = root.findall('.//item')
        articles = []
        for item in items:
            title = item.findtext('title', '').strip()
            link = item.findtext('link', '').strip()
            description = item.findtext('description', '').strip()
            pub_date_str = item.findtext('pubDate', '')

            # Get thumbnail
            thumb = item.find(f'{{{MRSS_NS}}}thumbnail')
            enclosure = item.find('enclosure')
            image_url = ''
            if thumb is not None:
                image_url = thumb.attrib.get('url', '')
            elif enclosure is not None and enclosure.attrib.get('type', '').startswith('image'):
                image_url = enclosure.attrib.get('url', '')

            # Parse publish date
            try:
                pub_dt = parsedate_to_datetime(pub_date_str)
                pub_iso = pub_dt.astimezone(timezone.utc).isoformat()
                pub_ago = time_ago(pub_dt)
            except Exception:
                pub_iso = datetime.now(timezone.utc).isoformat()
                pub_ago = 'recently'

            # Strip HTML from description
            import re
            description = re.sub(r'<[^>]+>', '', description).strip()[:200]

            articles.append({
                'title': title,
                'link': link,
                'description': description,
                'image': image_url,
                'published': pub_iso,
                'published_ago': pub_ago,
                'source': feed_info['source'],
                'source_logo': feed_info['source_logo'],
            })
        return articles
    except Exception as e:
        print(f"⚠️  Error fetching {feed_info['source']}: {e}")
        return []


def time_ago(dt):
    """Return human-readable time ago string."""
    now = datetime.now(timezone.utc)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    diff = now - dt
    seconds = int(diff.total_seconds())
    if seconds < 60:
        return 'just now'
    elif seconds < 3600:
        return f'{seconds // 60}m ago'
    elif seconds < 86400:
        return f'{seconds // 3600}h ago'
    else:
        return f'{seconds // 86400}d ago'


def is_relevant(article):
    """Check if article mentions a PL team or Premier League."""
    text = (article['title'] + ' ' + article['description']).lower()
    return any(team.lower() in text for team in PL_TEAMS)


def get_mentioned_teams(article):
    """Return list of PL teams mentioned in the article."""
    text = (article['title'] + ' ' + article['description']).lower()
    found = []
    seen = set()
    for team in PL_TEAMS:
        if team.lower() in text and team not in seen:
            # Normalise team names
            canonical = team.replace('Man City', 'Manchester City') \
                            .replace('Man United', 'Manchester United') \
                            .replace('Spurs', 'Tottenham') \
                            .replace('Wolves', 'Wolverhampton')
            if canonical not in seen:
                found.append(canonical)
                seen.add(canonical)
    return found[:3]  # max 3 team tags


def main():
    print(f"📰 News Fetcher — {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}")
    all_articles = []

    for feed in RSS_FEEDS:
        articles = parse_rss(feed)
        print(f"  {feed['source']}: {len(articles)} articles fetched")
        all_articles.extend(articles)

    # Filter to football/PL relevant
    relevant = [a for a in all_articles if is_relevant(a)]
    # Tag with mentioned teams
    for a in relevant:
        a['teams'] = get_mentioned_teams(a)

    # Deduplicate by title
    seen_titles = set()
    unique = []
    for a in relevant:
        key = a['title'].lower()[:60]
        if key not in seen_titles:
            seen_titles.add(key)
            unique.append(a)

    # Sort by published date (newest first)
    unique.sort(key=lambda x: x['published'], reverse=True)

    # Keep top 30
    unique = unique[:30]

    output = {
        'updated': datetime.now(timezone.utc).isoformat(),
        'count': len(unique),
        'articles': unique,
    }

    with open(OUT_FILE, 'w') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"✅ Saved {len(unique)} articles to {OUT_FILE}")


if __name__ == '__main__':
    main()
