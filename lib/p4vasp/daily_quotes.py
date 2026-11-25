"""Offline daily quotations and aphorisms selected by local calendar date."""
from contextlib import closing
from datetime import date
import json
from pathlib import Path
import p4vasp

FALLBACK = {'text': '千里之行，始于足下。', 'source': '老子·第六十四章',
            'url': 'https://ctext.org/text.pl?if=en&node=11655&remap=gb&show=parallel'}


def load_quotes():
    try:
        path = Path(p4vasp.p4vasp_home)/'data/quotes/daily.json'
        records = json.loads(path.read_text(encoding='utf-8'))
        if not isinstance(records, list) or not records: raise ValueError('Empty quote catalog')
        if not all(isinstance(row, dict) and all(isinstance(row.get(key), str) and row[key].strip()
                   for key in ('text', 'source', 'url')) for row in records):
            raise ValueError('Invalid quote catalog')
        return records
    except (OSError, ValueError):
        return [FALLBACK.copy()]


def load_schedule():
    """Read the bundled calendar once without creating or changing the database."""
    try:
        import sqlite3
    except ImportError:
        return {}

    path = Path(p4vasp.p4vasp_home) / 'data/quotes/daily.sqlite3'
    try:
        with closing(sqlite3.connect(path.resolve().as_uri() + '?mode=ro', uri=True)) as db:
            db.row_factory = sqlite3.Row
            rows = db.execute("""
                SELECT publish_date, quote AS text, author AS source, work,
                       translator, locator, source_url AS url, reflection_question
                FROM daily_quotes
            """)
            return {row['publish_date']: dict(row, language='en') for row in rows}
    except (OSError, sqlite3.Error):
        return {}


def quote_for_day(records, today=None, *, schedule=None):
    today = today or date.today()
    if schedule and today.isoformat() in schedule:
        return schedule[today.isoformat()]
    return records[(today.toordinal()-1) % len(records)]
