import json
import os
from pprint import pformat
# import vcr
import os
import tempfile

test_dir = os.path.dirname(os.path.realpath(__file__))
fixtures_path = os.path.join(test_dir, 'fixtures')
# cassettes_path = os.path.join(fixtures_path, 'cassettes')
# test_vcr = vcr.VCR(
#     cassette_library_dir=cassettes_path
# )

def fixture(filename):
    return os.path.join(fixtures_path, filename)

def _tempfile(content=None):
    """ Create tempfile and return absolute path. """
    tf = tempfile.NamedTemporaryFile(delete=False)
    if content is not None:
        tf.write(str(content).encode('ascii'))
    tf.close()
    return tf.name

class Tempfile(object):
    def __init__(self, content=None):
        self.tempfile = _tempfile(content)
    def __enter__(self):
        return self.tempfile
    def __exit__(self, type, value, traceback):
        os.remove(self.tempfile)

def from_json(str_data):
    return json.loads(str_data)

def from_noop(str_data):
    return str_data

def get_decoder(filename):
    _, extension = os.path.splitext(filename)
    if extension == '.json':
        return from_json

    return from_noop

def get_contents(filename):
    with open(filename, 'r') as f:
        return f.read()

def path_to_fixture(fixture):
    return os.path.join(fixtures_path, fixture)

def load_fixture(fixture):
    fullpath = path_to_fixture(fixture)
    if not os.path.isfile(fullpath):
        raise Exception('Could not load fixture[%s] @ %s' % (fixture, fixtures_path))

    decoder = get_decoder(fullpath)

    return decoder(get_contents(fullpath))

def serialize(dct, where='dump'):
    with open(where, 'w') as fh:
        fh.write(pformat(dct))

def unserialize(fixture):
    fixture = path_to_fixture(fixture)
    if os.path.isfile(fixture):
        return eval(get_contents(fixture))
    else:
        raise Exception('Could not load fixture[%s]' % (fixture))


def assert_fixture(data, name):
    fixture = path_to_fixture(name)
    if os.path.isfile(fixture):
        expected = eval(get_contents(fixture))
        assert data == expected
    else:
        serialize(data, fixture)
        assert False, "Fixture non existant, creating..."

# my_vcr = vcr.VCR(
#     serializer='json',
#     cassette_library_dir='fixtures/cassettes',
#     record_mode='once',
#     match_on=['uri', 'method'],
# )
