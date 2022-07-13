import click
from iictl.utils.parse import is_valid_object_name

def verify_object_name(object_name):
    if not is_valid_object_name(object_name):
        click.echo(f'{object_name} is not valid object name. object name must consist of lowercase letters, hyphens, and numbers.')
        exit(1)