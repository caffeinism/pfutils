import os
import shutil
from pfutils.utils.bulk_pool import ProcessPoolExecutor

def copy_func(src, dst):
    try:
        return shutil.copy2(src, dst)
    except PermissionError as e:
        raise FileSystemError(f'cannot write file [{e.filename}]')
    except FileNotFoundError as e:
        raise FileSystemError(f'cannot copy file [{e.filename}]')

def write_func(path, file_size, randomness):
    with open(path, 'wb') as f:
        f.write(b'0123456789abcdef' * 64 * file_size)
    
class FileManager:
    def __init__(self, num_workers, chunk_size):
        self.pool = ProcessPoolExecutor(num_workers, chunksize=chunk_size)
        self.futures = []

    def copy_file(self, src, dst):
        self.pool.submit(copy_func, src, dst)
    
    def remove_file(self, path):
        self.pool.submit(os.remove, path)

    def write_file(self, path, file_size, randomness):
        self.pool.submit(write_func, path, file_size, randomness)

    def flush_and_iter(self):
        return self.pool.flush()

    def __enter__(self):
        return self

    def __exit__(self, *args, **kwargs):
        pass

class FileSystemError(Exception):
    def __init__(self, msg):
        super(Exception, self).__init__(msg)
    
    def __str__(self):
        return f'filesystem error: {super().__str__()}'