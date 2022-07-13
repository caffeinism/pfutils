import click
from kubernetes import client, config

@click.group()
@click.pass_context
def cli(ctx):
    ctx.ensure_object(dict)
    
    
