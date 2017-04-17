import docker
import os
from subprocess import Popen, PIPE
from time import time

from .results import ResultLog, STDERR, BUILDSPEC
from .compat import to_str

HOUR = 60*60


class ExecutionError(Exception):
    pass


def generate_environment_variables(src_dir=None):
    """
    @TODO Provide a way to read this in through a config or something.

    http://docs.aws.amazon.com/codebuild/latest/userguide/build-env-ref.html
    """

    environ = {'CODEBUILD_BUILD_ARN':
               'arn:aws:codebuild:region-ID:account-ID:build/codebuild-demo-project:b1e6661e-e4f2-4156-9ab9-82a19EXAMPLE',
               'CODEBUILD_BUILD_ID': 'codebuild-demo-project:b1e6661e-e4f2-4156-9ab9-82a19EXAMPLE',
               'CODEBUILD_BUILD_IMAGE': 'aws/codebuild/java:openjdk-8',
               'CODEBUILD_INITIATOR': 'aws-buildspec',
               'CODEBUILD_KMS_KEY_ID': 'arn:aws:kms:region-ID:account-ID:key/key-ID or alias/key-alias',
               'CODEBUILD_SOURCE_REPO_URL': 's3://example-bucket',
               'CODEBUILD_SOURCE_VERSION': '86fa65efcf6dbe582c004b282cd108ba0423e7a2'}
    for name, _ in environ.items():
        value = os.environ.get(name)
        if value:
            environ[name] = value

    if src_dir:
        environ['CODEBUILD_SRC_DIR'] = src_dir
    else:
        environ['CODEBUILD_SRC_DIR'] = os.getcwd()
    return environ


def exec_environ(environ):
    for name, value in environ.items():
        if isinstance(value, str):
            os.environ[name] = value
        else:
            # warning
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


class SystemExecutor(BaseExecutor):
    def __init__(self, shell=None):
        self.shell = to_shell(None)
        self.with_system_shell = not shell
        self.environment = generate_environment_variables(os.getcwd())
        exec_environ(self.environment)

    def execute_line(self, line):
        cmd = self.shell + [line]
        process = Popen(cmd,
                        stdout=PIPE,
                        stderr=PIPE,
                        shell=self.with_system_shell)
        process.wait()

        results = ResultLog(process.stdout)
        results.add(process.stderr, STDERR)
        if process.returncode != 0:
            raise ExecutionError(results)

        return results


def volume(host, guest, mode='rw', volumes=None):
    if not volumes:
        volumes = {}
    volumes[host] = {'bind': guest, 'mode': mode}
    return volumes


class DockerExecutor(BaseExecutor):
    """
    @TODO: Verify how exactly does codebuild run commands within the container.
    Does it tear down for each line in the buildspec?
    Can i overwrite the containers entrypoint?
    Does codebuild pass everything through the cmd?


    working_dir: /tmp/src123123/src
    """
    def __init__(self, image='ubuntu', shell=None, timeout=1*HOUR, **docker_opts):
        """"""
        def to_shell(shell):
            if isinstance(shell, str):
                return shell.split(' ')
            return shell

        self.image = image
        self.shell = to_shell(shell) if shell else ['/bin/sh', '-c']
        self.container_id = None
        cli = self.api = docker.APIClient()
        working_dir = '/tmp/src%d/src' % time()
        docker_opts = {
            'working_dir': working_dir,
            'environment': generate_environment_variables(working_dir),
            'volumes': [working_dir],
            'host_config': cli.create_host_config(
                binds=[os.getcwd() + ':' + working_dir]
            ),
            'command': self.SLEEP_CMD % timeout,
            'detach': True,
        }
        self.docker_opts = docker_opts

    SLEEP_CMD = 'sleep %d'

    def start_container(self):
        if not self.container_id:
            response = self.api.create_container(self.image, **self.docker_opts)
            self.container_id = response[u'Id']
            if response[u'Warnings']:
                # @TODO: logging
                pass
            self.api.start(self.container_id)
        return self.container_id

    def __del__(self):
        if self.container_id:
            cid = self.container_id
            self.api.kill(cid)
            self.api.remove_container(cid)
            # @TODO cleanup any volumes/networks
            # is this safe?
            # self.api.prune_volumes()

    def execute_line(self, line):
        """"""
        # @TODO proper quoting of line
        cmd = self.shell + [line]
        cid = self.start_container()
        eid = self.api.exec_create(cid, cmd)['Id']
        out = self.api.exec_start(exec_id=eid)
        res = self.api.exec_inspect(eid)

        results = ResultLog(to_str(out))
        if res['ExitCode'] > 0:
            raise ExecutionError(results)

        return results
