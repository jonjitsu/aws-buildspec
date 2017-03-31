from helpers import *
from aws_buildspec.executors import *
import os, re
def test_generate_environment_variables_has_defaults():
    defaults = {'CODEBUILD_BUILD_ARN': 'arn:aws:codebuild:region-ID:account-ID:build/codebuild-demo-project:b1e6661e-e4f2-4156-9ab9-82a19EXAMPLE',
           'CODEBUILD_BUILD_ID': 'codebuild-demo-project:b1e6661e-e4f2-4156-9ab9-82a19EXAMPLE',
           'CODEBUILD_BUILD_IMAGE': 'aws/codebuild/java:openjdk-8',
           'CODEBUILD_INITIATOR': 'python-aws-buildspec',
           'CODEBUILD_KMS_KEY_ID': 'arn:aws:kms:region-ID:account-ID:key/key-ID or alias/key-alias',
           'CODEBUILD_SOURCE_REPO_URL': 's3://example-bucket',
           'CODEBUILD_SOURCE_VERSION': '86fa65efcf6dbe582c004b282cd108ba0423e7a2'}
    environ = generate_environment_variables()
    for name, expected in defaults.items():
        assert expected == environ[name]

    assert environ['CODEBUILD_SRC_DIR'] == os.getcwd()


def test_generate_environment_variables_wont_override():
    defaults = {'CODEBUILD_BUILD_ARN': 'arn:aws:codebuild:region-ID:account-ID:build/codebuild-demo-project:b1e6661e-e4f2-4156-9ab9-82a19EXAMPLE',
                'CODEBUILD_BUILD_ID': 'codebuild-demo-project:b1e6661e-e4f2-4156-9ab9-82a19EXAMPLE',
                'CODEBUILD_INITIATOR': 'python-aws-buildspec',
                'CODEBUILD_KMS_KEY_ID': 'arn:aws:kms:region-ID:account-ID:key/key-ID or alias/key-alias',
                'CODEBUILD_SOURCE_REPO_URL': 's3://example-bucket',
                'CODEBUILD_SOURCE_VERSION': '86fa65efcf6dbe582c004b282cd108ba0423e7a2'}

    os.environ['CODEBUILD_BUILD_IMAGE'] = 'TESTVALUE'
    environ = generate_environment_variables('/tmp')

    assert environ['CODEBUILD_BUILD_IMAGE'] == 'TESTVALUE'
    assert environ['CODEBUILD_SRC_DIR'] == '/tmp'
    for name, expected in defaults.items():
        assert expected == environ[name]

def test_DockerExecutor(tmpdir):
    spec = {
        'phases': {
            'build': {
                'commands': ['ls', 'pwd']
            }
        }
    }
    tmpdir.chdir()
    open('file123', 'w').write('abc')
    e = DockerExecutor()
    res = e.execute_phases(['build'], spec)
    assert res.results[1][1] == 'file123\n'
    pwd = re.compile('/tmp/src\d+/src')
    assert pwd.search(res.results[2][1])
