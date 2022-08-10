import os
import tqdm
import click
import xattr
import shutil
import random
import multiprocessing
from pathlib import Path
from pfutils.utils.chunk import determine_chunk_size
from pfutils.utils.bulk_pool import ProcessPoolExecutor
from pfutils.commands import cli
from _pfutil import copy_files

copy_func = shutil.copy2

@cli.command(help='copy files and directories')
@click.option('-r', '--recursive', is_flag=True, help='copy directories recursively')
@click.option('-j', '--num-workers', type=int, default=1, help='number of concurrent workers')
@click.option('-c', '--num-blocks', type=int, default=0, help='number of chunks')
@click.option('-L', '--dereference', is_flag=True, help='always follow symbolic links in SRC')
@click.argument('src', type=click.Path(exists=True))
@click.argument('dst', type=click.Path())
def cp(src, dst, recursive, num_workers, num_blocks, dereference):
    src = Path(src)
    dst = Path(dst)

    if os.path.islink(src):
        os.symlink(os.readlink(src), dst)
        return

    if os.path.isfile(src):
        copy_func(src, dst)
        return

    if os.path.isdir(src) and not recursive:
        click.echo(f"-r not specified; omitting directory '{src}'")
        return

    operation, directories = [], []
    for root, dirs, files in os.walk(src):
        root = Path(root)
        dst_path = dst / root.relative_to(src)
        dst_path.mkdir(exist_ok=True)
        directories.append((root, dst_path))

        for file_ in files:
            file_ = root / file_
            dst_file_path = dst / Path(file_).relative_to(src)
            operation.append((file_, dst_file_path))

    if num_blocks < 1:
        num_blocks = num_workers

    src_paths, dst_paths = zip(*operation)

    try:
        for _ in tqdm.tqdm(copy_files(src_paths, dst_paths, num_workers, num_blocks)):
            pass
    except Exception:
        print('exceptionhaha')
    for src_directory, dst_directory in directories:
        shutil.copystat(src_directory, dst_directory)