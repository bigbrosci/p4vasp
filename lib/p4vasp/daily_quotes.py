"""Offline public-domain quotations selected by local calendar date."""
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


def quote_for_day(records, today=None):
    return records[((today or date.today()).toordinal()-1) % len(records)]
