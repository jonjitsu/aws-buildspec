__version__ = "0.1.2"

from pprint import pprint
import yaml
from subprocess import Popen, PIPE
from .compat import to_str

BUILDSPEC_YML = 'buildspec.yml'
STDOUT=1
STDERR=2

def load_file(filename):
    with open(filename, 'r') as fp:
        return yaml.load(fp)

def join_lines(lines):
    return '\n'.join(lines)

import sys
def print_results(results):
    for line in format_results(results):
        sys.stdout.write(line)
    sys.stdout.flush()

class BaseExecutor(object):
    def execute_line(self, line):
        raise NotImplemented('@TODO')
    def execute_lines(self, lines):
        results = []
        for line in lines:
            results += self.execute_line(line)
        return results


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


def to_shell(shell):
    """"""
    if shell:
        return shell.split(' ')
    else:
        return []

class SystemExecutor(BaseExecutor):
    def __init__(self, shell=None):
        self.shell = to_shell(None)
        self.with_system_shell = not shell

    def execute_line(self, line):
        cmd = self.shell + [line]
        process = Popen(cmd, \
                        stdout=PIPE, \
                        stderr=PIPE, \
                        shell=self.with_system_shell)
        process.wait()

        output = stdout(process.stdout) + stderr(process.stderr)
        if process.returncode != 0:
            raise Exception(join_lines(format_results(output)))

        return output

import docker
class DockerExecutor(BaseExecutor):
    def __init__(self, image='ubuntu', shell=None):
        """"""
        self.image = image
        self.shell = shell if shell else '/bin/sh -c'
        self.client = docker.from_env()


    def execute_line(self, line):
        """"""
        cmd = self.shell + " '" + line + "'"
        result = self.client.containers.run(self.image, \
                                            cmd)
        return [(STDOUT, to_str(result))]

def execute_phases(phases, spec, executor):
    """
    Given:
    - a list of phases
    - a buildspec
    Execute phases as per the spec.

    If a phase does not exist it is an error.
    The order of phases is the order of execution.
    """
    results = []
    for phase in phases:
        if phase not in spec['phases']:
            raise Exception('No phase[%s] defined!' % phase)
        if 'commands' in spec['phases'][phase]:
            results += executor.execute_lines(spec['phases'][phase]['commands'])
        else:
            # log warning
            pass
    return results


PHASE_ORDER = {'install':10, 'pre_build':20, 'build':30, 'post_build':40}
def sort_phases(phases):
    """ Sort phases in order defined in AWS buildspec reference """
    sorter = lambda phase: PHASE_ORDER[phase]
    return sorted(phases, key=sorter)

def decide_phases(desired_phases, spec):
    """ Given:
        - a list of the desired phases to run
        - the buildspec
        Return a list of phases to run in the correct order.

        ???Should a missing phase be an error or a warning???
        Empty list for desired_phases means run all defined phases.
    """
    if 'phases' not in spec:
        return []
    if desired_phases:
        phases = []
        for phase in desired_phases:
            if phase in spec['phases']:
                phases.append(phase)
            else:
                raise Exception('Phase [%s] not defined' % phase)
    else:
        phases = [phase for phase, commands in spec['phases'].items()]

    return sort_phases(phases)

def validate_phases(phases):
    """ Given a list of phases throw exception if one is an invalid buildspec
        phase.
    """
    for phase in phases:
        if phase not in PHASE_ORDER:
            raise Exception('Invalid buildspec phase: [%s]' % phase)

def suggest_phase(phase):
    """ Given an invalid phase, suggest the closest ones. (git style) """
