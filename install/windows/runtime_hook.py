"""Supply writable no-op streams for legacy callbacks in windowed builds."""
import os
import sys

for name in ('stdout', 'stderr'):
    if getattr(sys, name) is None:
        setattr(sys, name, open(os.devnull, 'w', encoding='utf-8'))
