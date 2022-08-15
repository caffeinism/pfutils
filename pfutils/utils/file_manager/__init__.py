try:
    from _pfutil import FileManager, FileSystemError
    print('c')
except ModuleNotFoundError as e:
    from pfutils.utils.file_manager.file_manager import FileManager, FileSystemError
    print('p')