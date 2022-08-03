import os
import tqdm
import click
import shutil
import random
import multiprocessing
from pathlib import Path
from pfutils.commands.main import cli
from concurrent.futures import ProcessPoolExecutor

@cli.command(help='remove files or directories')
@click.option('-j', '--num-workers', type=int, default=1, help='number of concurrent workers')
@click.option('--shuffle', is_flag=True, help='shuffle the file distribution order')
@click.option('-r', '--recursive', is_flag=True, help='remove directories and their contents recursively')
@click.argument('file', nargs=-1)
def rm(file, recursive, num_workers, shuffle):
    if not click.confirm('you really meant it?', default=False):
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

    directories = []
    filenames = []
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
                filenames.append(file_)

    if shuffle:
        random.shuffle(filenames)

    with ProcessPoolExecutor(num_workers) as p:
        chunksize, extra = divmod(len(filenames), num_workers * 10)

        for _ in tqdm.tqdm(p.map(os.remove, filenames, chunksize=chunksize), desc='file', total=len(filenames)):
            pass

    for directory in tqdm.tqdm(directories[::-1], desc='directory'):
        os.rmdir(directory)
