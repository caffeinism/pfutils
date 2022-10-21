import os
import tqdm
import click
from pathlib import Path
from pfutils.commands import cli
from pfutils.utils.chunk import determine_chunk_size
from pfutils.utils.file_manager import FileManager, FileSystemError


@cli.command(help='create files and directories for metadata test')
@click.option('--num-directories', type=int, default=1000, help='number of directories (number of labels)')
@click.option('--num-total-files', type=int, default=1281167, help='total number of files (aggregated)')
@click.option('--file-size', type=int, default=100, help='KB per files')
@click.option('-j', '--num-workers', type=int, default=1, help='number of concurrent workers')
@click.option('-c', '--chunk-size', type=int, default=0, help='number of chunks')
@click.argument('target', type=click.Path())
def mdtest(target, num_workers, chunk_size, num_directories, num_total_files, file_size):
    target = Path(target)

    if os.path.isfile(target):
        click.echo(f"'{target}': File exists")
        return

    if os.path.isdir(target) and not click.confirm(f'{target} already exists. you really meant it?', default=False):
        click.echo('cancel operation')
        return

    chunk_size = determine_chunk_size(num_workers) if chunk_size < 1 else chunk_size
    
    target.mkdir(exist_ok=True)
    with FileManager(num_workers, chunk_size) as fm:
        for i in range(num_directories):
            directory_path = target / f'{i:04d}'
            directory_path.mkdir(exist_ok=True)

            num_files = num_total_files // num_directories \
                        + int(i < num_total_files % num_directories)

            for j in range(num_files):
                file_path = directory_path / f'{j:08d}'

                fm.write_file(file_path, file_size, False)

        try:
            for _ in tqdm.tqdm(fm.flush_and_iter()):
                pass
        except FileSystemError as e:
            print(str(e))
