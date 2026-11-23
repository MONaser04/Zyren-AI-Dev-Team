"""Allow ``python -m taskcli``."""
from __future__ import annotations

import sys

from taskcli import cli

sys.exit(cli.main())
