__version__ = "0.1.2"

from pprint import pprint
import yaml
from subprocess import Popen, PIPE
from .compat import to_str

BUILDSPEC_YML = 'buildspec.yml'
STDOUT=1
STDERR=2
BUILDSPEC=4

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

# class Results(object):
#     def __init__(self):
#         self.results = []
#     def add_output(self, line_or_it):
#         if isinstance(line_or_it, str):
#             self.results.append((STDOUT, line_or_it))
#         else:
#             self.results.extend(stdout(line_or_it))

#     def __str__(self):
#         return '@TODO'

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
        output = line[1].rstrip()
        if line[0] == STDERR:
            yield 'ERR: %s\n' % output
        elif line[0] == STDOUT:
            yield 'OUT: %s\n' % output
        else:
            yield output + '\n'


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
    """
    @TODO: Verify how exactly does codebuild run commands within the container.
    Does it tear down for each line in the buildspec?
    Can i overwrite the containers entrypoint?
    Does codebuild pass everything through the cmd?
    """
    def __init__(self, image='ubuntu', shell=None):
        """"""
        self.image = image
        self.shell = shell if shell else '/bin/sh -c'
        self.client = docker.from_env()
        self.container = None

    def execute_line(self, line):
        """"""
        cmd = self.shell + " '" + line + "'"
        result = self.client \
                     .containers \
                     .run(self.image,
                          command=cmd,
                          stdout=True,
                          stderr=True,
                          remove=True)
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
            results.append((BUILDSPEC, 'Executing %s phase' % phase))
            results += executor.execute_lines(spec['phases'][phase]['commands'])
        else:
            results.append((BUILDSPEC, 'No commands found for phase ' + phase))
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
