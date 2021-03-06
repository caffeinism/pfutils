import os
import tqdm
import click
import shutil
import random
import multiprocessing
from pathlib import Path
from pfutils.commands import cli

def copy(path):
    src, dst = path
    shutil.copy(src, dst)

@cli.command(help='copy files and directories')
@click.option('-r', '--recursive', is_flag=True, help='copy directories recursively')
@click.option('-j', '--num-workers', type=int, default=1, help='number of concurrent workers')
@click.option('--shuffle', is_flag=True, help='shuffle the file distribution order')
@click.argument('src', type=click.Path(exists=True))
@click.argument('dst', type=click.Path())
def cp(src, dst, recursive, num_workers, shuffle):
    src = Path(src)
    dst = Path(dst)

    if os.path.isfile(src):
        shutil.copy(src, dst)
        return

    if os.path.isdir(src) and not recursive:
        click.echo(f"-r not specified; omitting directory '{src}'")
        return

    if os.path.islink(src):
        raise NotImplementedError

    operation = []
    for root, dirs, files in os.walk(src):
        root = Path(root)
        dst_path = dst / root.relative_to(src)
        dst_path.mkdir(exist_ok=True)

        for file_ in files:
            file_ = root / file_
            dst_file_path = dst / Path(file_).relative_to(src)
            operation.append((file_, dst_file_path))

    if shuffle:
        random.shuffle(operation)

    with multiprocessing.Pool(num_workers) as p:
        for _ in tqdm.tqdm(p.imap_unordered(copy, operation), total=len(operation)):
            pass