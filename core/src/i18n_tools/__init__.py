"""
The i18n tools package.

This version will be updated automatically when releasing.
See: scripts/update_app_version.sh
"""

__version__ = "0.0.1"

## Others:
from i18n_tools.adapters.cli.app import i18n_cli as i18n_cli
from i18n_tools.apps import *  # noqa: F403
from i18n_tools.shared import main_func as main_func
