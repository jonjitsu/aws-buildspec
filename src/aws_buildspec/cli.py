"""
Module that contains the command line app.

Why does this file exist, and why not put this in __main__?

  You might be tempted to import things from __main__ later, but that will cause
  problems: the code will get executed twice:

  - When you run `python -maws_buildspec` python will execute
    ``__main__.py`` as a script. That means there won't be any
    ``aws_buildspec.__main__`` in ``sys.modules``.
  - When you import __main__ it will get executed again (as a module) because
    there's no ``aws_buildspec.__main__`` in ``sys.modules``.

  Also see (1) from http://click.pocoo.org/5/setuptools/#setuptools-integration
"""
import click
from click import echo, UsageError
from . import BUILDSPEC_YML
import aws_buildspec.cmd as cmd

# @click.command()
@click.group()
# @click.argument('names', nargs=-1)
def main():
    """ Runs a buildspec.yml

        Examples:
        Runs all defined phases.
        $ buildspec

        Run specific phase(s)
        $ buildspec build
        $ buildspec install build

        It's an error to specifically run an undefined phase.
        $ buildspec install

    """
    # click.echo(repr(names))

@main.command()
@click.option('-f', '--file', metavar='FILE', default=BUILDSPEC_YML)
@click.argument('type', default='full')
def init(type, file):
    """ Creates a buildspec.yml """
    try:
        cmd.init(type, file)
    except IOError:
        raise UsageError('Failed generating buildspec of type: ' + str(type))
    else:
        echo('Generated ' + file)

