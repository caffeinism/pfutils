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

@cli.command(help='remove files or directories')
@click.option('-j', '--num-workers', type=int, default=1, help='number of concurrent workers')
@click.option('-r', '--recursive', is_flag=True, help='remove directories and their contents recursively')
@click.option('-c', '--chunksize', type=int, default=0, help='size of chunk')
@click.argument('file', nargs=-1)
def rm(file, recursive, num_workers, chunksize):
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

    chunksize = determine_chunk_size(num_workers) if chunksize < 1 else chunksize

    directories = []
    with ProcessPoolExecutor(max_workers=num_workers, chunksize=chunksize) as p:
        num_total_tasks = 0
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
                    p.submit(os.remove, file_)
                    num_total_tasks += 1

        for _ in tqdm.tqdm(p.flush(), desc='file', total=num_total_tasks):
            pass

    for directory in tqdm.tqdm(directories[::-1], desc='directory'):
        os.rmdir(directory)
