"""Legacy import alias for the GTK3 runtime."""
import sys
_self = sys.modules[__name__]
from p4vasp.gtk3 import *
sys.modules[__name__] = _self
