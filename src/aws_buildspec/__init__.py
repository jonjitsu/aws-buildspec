__version__ = "0.1.0"

from pprint import pprint
import yaml
from subprocess import Popen, PIPE

BUILDSPEC_YML = 'buildspec.yml'

def load_file(filename):
    with open(filename, 'r') as fp:
        return yaml.load(fp)

STDOUT=1
STDERR=2
# @TODO: deal with unicode
def stdstream(stream, type=STDOUT):
    return [(type, line) for line in stream]

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
def execute_line(line):
    """"""
    cmd = SHELL_CMD + [line]
    process = Popen(cmd, stdout=PIPE, stderr=PIPE)
    process.wait()

    output = stdout(process.stdout) + stderr(process.stderr)
    if process.returncode != 0:
        raise Exception(join_lines(format_results(output)))

    return output

    # result = subprocess.call(SHELL_CMD + [line], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    # if result.returncode != 0:
    #     pass

    # result = subprocess.check_output(['/bin/sh', '-c', line], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # if result.stdout:
    #     output = stdout(result.stdout)
    # if result.stderr:
    #     output += stderr(result.stderr)

    # return output

def execute_commands(lines):
    """"""
    for line in lines:
        execute_line(line)

def execute_phases(phases, spec):
    """
    Given:
    - a list of phases
    - a buildspec
    Execute phases as per the spec.
    """
    for phase in phases:
        execute_commands(spec['phases'][phase])

