import click
from pfutils.commands.main import cli

@cli.command(help='secure copy (remote file copy program)')
@click.option('-r', '--recursive', is_flag=True, help='delete recursivly')
@click.argument('target', nargs=-1)
def scp(target, recursive):
    raise NotImplementedError