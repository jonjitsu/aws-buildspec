from .results import ResultLog, STDOUT, STDERR, BUILDSPEC

class ExecutionError(Exception):
    pass

class BaseExecutor(object):
    def execute_line(self, line):
        raise NotImplemented('@TODO')
    def execute_lines(self, lines):
        results = ResultLog()
        for line in lines:
            results.add(self.execute_line(line))
        return results

    def execute_phases(self, phases, spec):
        """
        Given:
        - a list of phases
        - a buildspec
        Execute phases as per the spec.

        If a phase does not exist it is an error.
        The order of phases is the order of execution.
        """
        results = ResultLog()
        for phase in phases:
            if phase not in spec['phases']:
                raise Exception('No phase[%s] defined!' % phase)
            if 'commands' in spec['phases'][phase]:
                results.add('Executing %s phase' % str(phase), BUILDSPEC)
                results.add(self.execute_lines(spec['phases'][phase]['commands']))
            else:
                results.add('No commands found for phase ' + str(phase), BUILDSPEC)
        return results


def to_shell(shell):
    """"""
    if shell:
        return shell.split(' ')
    else:
        return []

from subprocess import Popen, PIPE
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

        results = ResultLog(process.stdout)
        results.add(process.stderr, STDERR)
        if process.returncode != 0:
            raise ExecutionError(results)

        return results


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
        return stdout(result)

