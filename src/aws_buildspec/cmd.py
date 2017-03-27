import pkgutil
import pkg_resources
from pprint import pprint
from . import BUILDSPEC_YML, load_file, execute_phases, decide_phases, \
    print_results, validate_phases, SystemExecutor, DockerExecutor
from .compat import to_str

def init(type='full', filename=BUILDSPEC_YML):
    """"""
    # data = pkgutil.get_data('buildspec', 'data/template.yml')
    template_name = 'templates/%s.yml' % type
    data = pkg_resources.resource_string('aws_buildspec', template_name)
    with open(filename, 'w') as fp:
        fp.write(to_str(data))

def run(phases, filename=BUILDSPEC_YML, shell=None, docker_image=None):
    """"""
    validate_phases(phases)
    spec = load_file(filename)
    phases = decide_phases(phases, spec)
    if docker_image:
        executor = DockerExecutor(docker_image, shell)
    else:
        executor = SystemExecutor(shell)

    return execute_phases(phases, spec, executor)
