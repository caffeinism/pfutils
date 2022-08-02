import click
from pfutils.commands.main import cli

@cli.command(help='estimate file space usage')
@click.argument('target', nargs=-1)
def du(target):
    raise NotImplementedError