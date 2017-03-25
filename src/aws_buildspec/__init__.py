__version__ = "0.1.0"

from pprint import pprint
import yaml
from subprocess import Popen, PIPE
from .compat import to_str

BUILDSPEC_YML = 'buildspec.yml'

def load_file(filename):
    with open(filename, 'r') as fp:
        return yaml.load(fp)

STDOUT=1
STDERR=2
# @TODO: deal with unicode
def stdstream(stream, type=STDOUT):
    return [(type, to_str(line)) for line in stream]

def stdout(out): return stdstream(out, STDOUT)
def stderr(err): return stdstream(err, STDERR)

def format_results(results):
    for line in results:
        if line[0] == STDERR:
            yield 'ERR: ' + line[1]
        else:
            yield 'OUT: ' + line[1]

def join_lines(lines):
    return '\n'.join(lines)

import sys
def print_results(results):
    for line in format_results(results):
        sys.stdout.write(line)
    sys.stdout.flush()



SHELL='/bin/sh'
SHELL_CMD=[SHELL, '-c']
def execute_line(line, shell=[]):
    """"""
    cmd = shell + [line]
    process = Popen(cmd, stdout=PIPE, stderr=PIPE, shell=not shell)
    process.wait()

    output = stdout(process.stdout) + stderr(process.stderr)
    if process.returncode != 0:
        raise Exception(join_lines(format_results(output)))

    return output


def execute_lines(lines):
    """"""
    results = []
    for line in lines:
        results += execute_line(line)
    return results

def execute_phases(phases, spec):
    """
    Given:
    - a list of phases
    - a buildspec
    Execute phases as per the spec.
    """
    for phase in phases:
        execute_lines(spec['phases'][phase])

