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

copy_func = shutil.copy2

@cli.command(help='copy files and directories')
@click.option('-r', '--recursive', is_flag=True, help='copy directories recursively')
@click.option('-j', '--num-workers', type=int, default=1, help='number of concurrent workers')
@click.option('-c', '--chunksize', type=int, default=0, help='size of chunk')
@click.option('-L', '--dereference', is_flag=True, help='always follow symbolic links in SRC')
@click.argument('src', type=click.Path(exists=True))
@click.argument('dst', type=click.Path())
def cp(src, dst, recursive, num_workers, chunksize, dereference):
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

    chunksize = determine_chunk_size(num_workers) if chunksize < 1 else chunksize

    directories = []
    with ProcessPoolExecutor(max_workers=num_workers, chunksize=chunksize) as p:
        num_total_tasks = 0
        for root, dirs, files in os.walk(src, followlinks=dereference):
            root = Path(root)
            dst_path = dst / root.relative_to(src)
            dst_path.mkdir(exist_ok=True)
            directories.append((root, dst_path))

            for file_ in files:
                file_ = root / file_
                dst_file_path = dst / Path(file_).relative_to(src)
                p.submit(copy_func, file_, dst_file_path)
                num_total_tasks += 1
        
        for _ in tqdm.tqdm(p.flush(), total=num_total_tasks):
            pass

    for src_directory, dst_directory in directories:
        shutil.copystat(src_directory, dst_directory)