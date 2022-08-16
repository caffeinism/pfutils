import logging as _logging

try:
    from _pfutil import FileManager, FileSystemError
    _logging.info("use c++ thread implement")
except ModuleNotFoundError as e:
    from pfutils.utils.file_manager.file_manager import FileManager, FileSystemError
    _logging.info("use python process implement")
