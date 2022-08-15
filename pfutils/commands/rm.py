import os
import tqdm
import click
import shutil
import random
import multiprocessing
from pathlib import Path
from pfutils.commands.main import cli
from pfutils.utils.chunk import determine_chunk_size
from pfutils.utils.bulk_pool import ProcessPoolExecutor
from pfutils.utils.file_manager import FileManager

@cli.command(help='remove files or directories')
@click.option('-j', '--num-workers', type=int, default=1, help='number of concurrent workers')
@click.option('-r', '--recursive', is_flag=True, help='remove directories and their contents recursively')
@click.option('-c', '--chunk-size', type=int, default=0, help='size of chunk')
@click.option('-y', '--yes', is_flag=True, help='yes I really meant it')
@click.argument('file', nargs=-1)
def rm(file, recursive, num_workers, chunk_size, yes):
    if not yes and not click.confirm('you really meant it?', default=False):
        click.echo('cancel deletation')
        return

    if len(file) < 1:
        click.echo('missing operand')
        return

    for path in file:
        path = Path(path)

        if not os.path.exists(path):
            click.echo(f"cannot remove '{path}': No such file or directory")
            return

        if os.path.isdir(path) and not recursive:
            click.echo(f"cannot remove '{path}': Is a directory")
            return

        if os.path.islink(path):
            raise NotImplementedError

    chunk_size = determine_chunk_size(num_workers) if chunk_size < 1 else chunk_size

    directories = []
    with FileManager(num_workers, chunk_size) as fm:
        for path in file:
            path = Path(path)

            if os.path.isfile(path):
                filenames.append(path)
                return

            for root, dirs, files in os.walk(path):
                root = Path(root)
                directories.append(root)

                for file_ in files:
                    file_ = root / file_
                    fm.remove_file(file_)

        for _ in tqdm.tqdm(fm.flush_and_iter(), desc='file'):
            pass

    for directory in tqdm.tqdm(directories[::-1], desc='directory'):
        os.rmdir(directory)
