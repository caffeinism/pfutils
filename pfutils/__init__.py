import logging as _logging
import os as _os

_log_level = _os.environ.get('LOG_LEVEL', 'WARNING')
_logging.basicConfig(level=_log_level)