import sys

if sys.platform.startswith("win"):
  from .nt import *
else:
  from .nix import *

from .board import *
