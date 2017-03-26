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
from . import BUILDSPEC_YML, load_file, execute_phases, decide_phases, \
    print_results, validate_phases
import aws_buildspec.cmd as cmd
import os

# @click.command()
@click.group()
# @click.argument('phases', nargs=-1)
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

        @TODO make run subcommand the default command
    """
    # click.echo(repr(phases))

@main.command()
@click.option('-f', '--file', metavar='FILE', default=BUILDSPEC_YML,
              help='buildspec.yml file')
@click.argument('type', default='full')
def init(type, file):
    """ Generate a buildspec.yml """
    try:
        cmd.init(type, file)
    except IOError:
        raise UsageError('Failed generating buildspec of type: ' + str(type))
    else:
        echo('Generated ' + file)


@main.command()
@click.option('-f', '--file', metavar='FILE', default=BUILDSPEC_YML,
              help='buildspec.yml file')
@click.argument('phases', nargs=-1)
def run(phases, file):
    """ Run 1+ phases within the buildspec.yml """
    if not os.path.isfile(file):
        raise UsageError('%s does not exist.' % str(file))

    try:
        # echo(repr(phases))
        phases = list(phases)
        validate_phases(phases)
        spec = load_file(file)
        phases = decide_phases(phases, spec)
        results = execute_phases(phases, spec)
        print_results(results)
    except Exception as e:
        raise UsageError(str(e))
