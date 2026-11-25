"""Offline neutral-atom reference, independent of optional scientific libraries."""
from functools import lru_cache
import json
from pathlib import Path


@lru_cache(maxsize=4)
def _read(root):
    try:
        data=json.loads((Path(root)/'data/resources/atomic_states.json').read_text(encoding='utf-8'))
        if not isinstance(data,dict) or not isinstance(data.get('elements'),dict) or not isinstance(data.get('source'),dict):raise ValueError('Invalid reference format')
        return data
    except (OSError,ValueError):return dict(source={},elements={})


def reference(symbol):
    import p4vasp
    data=_read(str(p4vasp.p4vasp_home))
    return dict(data['elements'].get(symbol,{}),source=data['source'])


@lru_cache(maxsize=4)
def _crystals(root):
    try:
        data=json.loads((Path(root)/'data/resources/crystal_states.json').read_text(encoding='utf-8'))
        if not isinstance(data,dict) or not isinstance(data.get('elements'),dict):
            raise ValueError('Invalid crystal reference format')
        return data['elements']
    except (OSError,ValueError):
        return {}


def crystal_reference(symbol):
    """Qualified condensed-phase reference; never used to generate atomic inputs."""
    import p4vasp
    record=_crystals(str(p4vasp.p4vasp_home)).get(symbol,{})
    return dict(record) if isinstance(record,dict) else {}
