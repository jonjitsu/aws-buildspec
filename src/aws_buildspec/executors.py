from .results import ResultLog, STDOUT, STDERR, BUILDSPEC

class ExecutionError(Exception):
    pass

def generate_environment_variables(src_dir=None):
    """
    @TODO Provide a way to read this in through a config or something.

    http://docs.aws.amazon.com/codebuild/latest/userguide/build-env-ref.html
    AWS_DEFAULT_REGION: The AWS region where the build is running (for example, us-east-1). This environment variable is used primarily by the AWS CLI.
    AWS_REGION: The AWS region where the build is running (for example, us-east-1). This environment variable is used primarily by the AWS SDKs.
    CODEBUILD_BUILD_ARN: The Amazon Resource Name (ARN) of the build (for example, arn:aws:codebuild:region-ID:account-ID:build/codebuild-demo-project:b1e6661e-e4f2-4156-9ab9-82a19EXAMPLE).
    CODEBUILD_BUILD_ID: The AWS CodeBuild ID of the build (for example, codebuild-demo-project:b1e6661e-e4f2-4156-9ab9-82a19EXAMPLE).
    CODEBUILD_BUILD_IMAGE: The AWS CodeBuild build image identifier (for example, aws/codebuild/java:openjdk-8).
    CODEBUILD_INITIATOR: The entity that started the build. If AWS CodePipeline started the build, this is the pipeline's name, for example codepipeline/my-demo-pipeline. If an IAM user started the build, this is the user's name, for example MyUserName. If the Jenkins plugin for AWS CodeBuild started the build, this is the string CodeBuild-Jenkins-Plugin.
    CODEBUILD_KMS_KEY_ID: The identifier of the AWS KMS key that AWS CodeBuild is using to encrypt the build output artifact (for example, arn:aws:kms:region-ID:account-ID:key/key-ID or alias/key-alias).
    CODEBUILD_SOURCE_REPO_URL: The URL to the input artifact or source code repository. For Amazon S3, this is s3:// followed by the bucket name and path to the input artifact. For AWS CodeCommit and GitHub, this is the repository's clone URL.
    CODEBUILD_SOURCE_VERSION: For Amazon S3, the version ID associated with the input artifact. For AWS CodeCommit, the commit ID or branch name associated with the version of the source code to be built. For GitHub, the commit ID, branch name, or tag name associated with the version of the source code to be built.
    CODEBUILD_SRC_DIR: The directory path that AWS CodeBuild uses for the build (for example, /tmp/src123456789/src).
    HOME: This environment variable is always set to /root.
    """

    environ = {'CODEBUILD_BUILD_ARN': 'arn:aws:codebuild:region-ID:account-ID:build/codebuild-demo-project:b1e6661e-e4f2-4156-9ab9-82a19EXAMPLE',
           'CODEBUILD_BUILD_ID': 'codebuild-demo-project:b1e6661e-e4f2-4156-9ab9-82a19EXAMPLE',
           'CODEBUILD_BUILD_IMAGE': 'aws/codebuild/java:openjdk-8',
           'CODEBUILD_INITIATOR': 'python-aws-buildspec',
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

import os
from subprocess import Popen, PIPE
class SystemExecutor(BaseExecutor):
    def __init__(self, shell=None):
        self.shell = to_shell(None)
        self.with_system_shell = not shell
        self.environment = generate_environment_variables(os.getcwd())
        exec_environ(self.environment)

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

def volume(host, guest, mode='rw', volumes=None):
    if not volumes:
        volumes = {}
    volumes[host]={'bind': guest, 'mode': mode}
    return volumes

HOUR=60*60
import docker
from time import time
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

        results = ResultLog(out)
        if res['ExitCode'] > 0:
            raise ExecutionError(results)

        return results
