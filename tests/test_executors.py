
from aws_buildspec.executors import generate_environment_variables
import os
# def test_generate_environment_variables_has_defaults():
#     defaults = {'CODEBUILD_BUILD_ARN': 'arn:aws:codebuild:region-ID:account-ID:build/codebuild-demo-project:b1e6661e-e4f2-4156-9ab9-82a19EXAMPLE',
#            'CODEBUILD_BUILD_ID': 'codebuild-demo-project:b1e6661e-e4f2-4156-9ab9-82a19EXAMPLE',
#            'CODEBUILD_BUILD_IMAGE': 'aws/codebuild/java:openjdk-8',
#            'CODEBUILD_INITIATOR': 'python-aws-buildspec',
#            'CODEBUILD_KMS_KEY_ID': 'arn:aws:kms:region-ID:account-ID:key/key-ID or alias/key-alias',
#            'CODEBUILD_SOURCE_REPO_URL': 's3://example-bucket',
#            'CODEBUILD_SOURCE_VERSION': '86fa65efcf6dbe582c004b282cd108ba0423e7a2'}
#     generate_environment_variables()
#     for name, expected in defaults.items():
#         assert expected == os.environ[name]

#     assert os.environ['CODEBUILD_SRC_DIR'] == os.getcwd()


# def test_generate_environment_variables_wont_override():
#     defaults = {'CODEBUILD_BUILD_ARN': 'arn:aws:codebuild:region-ID:account-ID:build/codebuild-demo-project:b1e6661e-e4f2-4156-9ab9-82a19EXAMPLE',
#                 'CODEBUILD_BUILD_ID': 'codebuild-demo-project:b1e6661e-e4f2-4156-9ab9-82a19EXAMPLE',
#                 'CODEBUILD_INITIATOR': 'python-aws-buildspec',
#                 'CODEBUILD_KMS_KEY_ID': 'arn:aws:kms:region-ID:account-ID:key/key-ID or alias/key-alias',
#                 'CODEBUILD_SOURCE_REPO_URL': 's3://example-bucket',
#                 'CODEBUILD_SOURCE_VERSION': '86fa65efcf6dbe582c004b282cd108ba0423e7a2'}

#     os.environ['CODEBUILD_BUILD_IMAGE'] = 'TESTVALUE'
#     generate_environment_variables('/tmp')

#     assert os.environ['CODEBUILD_BUILD_IMAGE'] == 'TESTVALUE'
#     assert os.environ['CODEBUILD_SRC_DIR'] == '/tmp'
#     for name, expected in defaults.items():
#         assert expected == os.environ[name]
