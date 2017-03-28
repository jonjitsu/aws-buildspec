from .helpers import *
import pytest
import pprint
from aws_buildspec import *

def test_load_file():
    content = """---
    version: 0.1
    phases: {}
    """
    expected = {'version': 0.1, 'phases':{}}
    with Tempfile(content) as filename:
        assert load_file(filename) == expected

def test_execute_line():
    e = SystemExecutor()
    res = e.execute_line('echo hello world!')
    assert res == [(STDOUT, 'hello world!\n')]

    res = e.execute_line('echo first; echo second ; false && ls tests || echo failure')
    assert res == [(STDOUT, 'first\n'), (STDOUT, 'second\n'), (STDOUT, 'failure\n')]

    with Tempfile() as filename:
        res = e.execute_line('echo some text > %s && cat %s' % (filename, filename))
        assert res == [(STDOUT, 'some text\n')]

    # with Tempfile() as filename:
    #     res = execute_line('mkdir /tmp/a/fdsa/asdf/asdfasdf/assdf 2>&1 > %s && cat %s || true' % (filename, filename))
    #     assert res == [(STDOUT, 'mkdir: cannot create directory \xe2\x80\x98/tmp/a/fdsa/asdf/asdfasdf/assdf\xe2\x80\x99: No such file or directory\n')]

def test_execute_line_raises_exception():
    e = SystemExecutor()
    with pytest.raises(Exception):
        e.execute_line('false')
    with pytest.raises(Exception):
        e.execute_line('ls -lat /aaslk/asdf/asdf/asd')

def test_execute_lines():
    e = SystemExecutor()
    lines = ['echo hello world!',
             'echo first; echo second ; false && ls tests || echo failure']
    assert e.execute_lines(lines) == [(STDOUT, 'hello world!\n'), (STDOUT, 'first\n'), (STDOUT, 'second\n'), (STDOUT, 'failure\n')]

def test_execute_phases():
    spec = {
        'phases': {
            'install': {
                'commands': ['echo install phase']
            },
            'build': {
                'commands': ['echo build phase']
            }
        }
    }
    e = SystemExecutor()
    assert execute_phases(['install'], spec, e) == [(BUILDSPEC, 'Executing install phase'), (STDOUT, 'install phase\n')]
    assert execute_phases(['build'], spec, e) == [(BUILDSPEC, 'Executing build phase'), (STDOUT, 'build phase\n')]
    assert execute_phases(['install', 'build'], spec, e) == [(BUILDSPEC, 'Executing install phase'),
                                                             (STDOUT, 'install phase\n'),
                                                             (BUILDSPEC, 'Executing build phase'),
                                                             (STDOUT, 'build phase\n')]

    [(STDOUT, 'install phase\n'), (STDOUT, 'build phase\n')]

    with pytest.raises(Exception):
        execute_phases(['install', 'build', 'nonexistant'], spec, e)

from random import shuffle
def test_sort_phases():
    assert sort_phases([]) == []
    assert sort_phases(['install']) == ['install']
    assert sort_phases(['build', 'install']) == ['install', 'build']

    phases_ordered = ['install', 'pre_build', 'build', 'post_build']
    phases = phases_ordered[:]
    for i in range(10):
        assert sort_phases(phases) == phases_ordered
        shuffle(phases)


def test_decide_phases():
    spec = {}
    assert decide_phases([], spec) == []
    spec = {'phases':{}}
    assert decide_phases([], spec) == []

    spec = {
        'phases': {
            'install': {
                'commands': ['echo install phase']
            },
            'build': {
                'commands': ['echo build phase']
            },
            'pre_build': {}
        }
    }
    assert decide_phases([], spec) == ['install', 'pre_build', 'build']

    assert decide_phases(['install'], spec) == ['install']
    assert decide_phases(['build'], spec) == ['build']
    assert decide_phases(['build', 'pre_build'], spec) == ['pre_build', 'build']
    with pytest.raises(Exception):
        decide_phases(['build', 'post_build'], spec)

