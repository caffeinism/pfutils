import os
import tqdm
import click
import xattr
import shutil
import random
import functools
import multiprocessing
from pathlib import Path
from pfutils.utils.chunk import determine_chunk_size
from pfutils.utils.bulk_pool import ProcessPoolExecutor
from pfutils.commands import cli

copy_func = shutil.copy2

def ret_function(return_value):
    def func(*args, **kwargs):
        return return_value
    return func

class DummyDirEntry:
    def __init__(self, name, path, is_dir, is_file, is_symlink):
        self.name = name
        self.path = path
        self._is_dir = is_dir
        self._is_file = is_file
        self._is_symlink = is_symlink
    
    def __repr__(self):
        return self.path

    def is_dir(self):
        return self._is_dir

    def is_file(self):
        return self._is_file

    def is_symlink(self):
        return self._is_symlink

    @staticmethod
    def from_path(path):
        return DummyDirEntry(path.name, str(path), path.is_dir(), path.is_file(), path.is_symlink())

    @staticmethod
    def from_dir_entry(dir_entry):
        return DummyDirEntry(dir_entry.name, dir_entry.path, dir_entry.is_dir(), dir_entry.is_file(), dir_entry.is_symlink())

def copy_dir(src, dst):
    os.makedirs(dst, exist_ok=True)
    return [(DummyDirEntry.from_dir_entry(it), os.path.join(dst, it.name)) for it in os.scandir(src.path)]

def copy_file(src, dst):
    copy_func(src.path, dst)
    return []

@cli.command(help='copy files and directories')
@click.option('-r', '--recursive', is_flag=True, help='copy directories recursively')
@click.option('-j', '--num-workers', type=int, default=1, help='number of concurrent workers')
@click.option('-c', '--chunksize', type=int, default=0, help='size of chunk')
@click.argument('src', type=click.Path(exists=True))
@click.argument('dst', type=click.Path())
def cp(src, dst, recursive, num_workers, chunksize):
    src = Path(src)
    dst = Path(dst)

    if os.path.isfile(src):
        copy_func(src, dst)
        return

    if os.path.isdir(src) and not recursive:
        click.echo(f"-r not specified; omitting directory '{src}'")
        return

    if os.path.islink(src):
        raise NotImplementedError # TODO: copy symlink recursivly

    chunksize = determine_chunk_size(num_workers) if chunksize < 1 else chunksize

    # with ProcessPoolExecutor(max_workers=num_workers, chunksize=chunksize) as p:
    #     num_total_tasks = 0
    #     for root, dirs, files in os.walk(src):
    #         root = Path(root)
    #         dst_path = dst / root.relative_to(src)
    #         dst_path.mkdir(exist_ok=True) # TODO: copy stat to dir

    #         for file_ in files:
    #             file_ = root / file_
    #             dst_file_path = dst / Path(file_).relative_to(src)
    #             p.submit(copy_func, file_, dst_file_path)
    #             num_total_tasks += 1
        
    #     for _ in tqdm.tqdm(p.flush(), total=num_total_tasks):
    #         pass

    with ProcessPoolExecutor(max_workers=num_workers, chunksize=chunksize) as p:
        p.submit(copy_dir, DummyDirEntry.from_path(src), dst)

        num_total_tasks = 0
        for it in tqdm.tqdm(p.flush_until_end()):
            # print(it)
            for src_, dst_ in it:
                num_total_tasks += 1
                if src_.is_symlink():
                    raise NotImplementedError
                elif src_.is_dir():
                    p.submit(copy_dir, src_, dst_)
                elif src_.is_file():
                    p.submit(copy_file, src_, dst_)
