"""Allow running yap as `python -m yap`."""

import sys
from yap.cli import main

sys.exit(main())
