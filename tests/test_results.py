from aws_buildspec.results import *
from .helpers import *
import pytest
import pprint
import os



def test_ResultLog_is_iterable():
    data = list('abcde')
    results = ResultLog(data)
    expected = ['OUT: a', 'OUT: b', 'OUT: c', 'OUT: d', 'OUT: e']
    actual = [line for line in results]
    assert actual == expected

def test_ResultLog_has_length():
    results = ResultLog()
    assert len(results)==0

    results = ResultLog(list('1234'))
    assert len(results)==4

def test_ResultLog__add_line():
    results = ResultLog()
    for i in range(5):
        results.add_line('line' + str(i))

    expected = ['OUT: line0', 'OUT: line1', 'OUT: line2', 'OUT: line3', 'OUT: line4']
    actual = [line for line in results]
    assert actual == expected

    results = ResultLog('line1')
    results.add('line2', STDERR)
    results.add('line3', BUILDSPEC)
    expected = ['OUT: line1', 'ERR: line2', 'line3']
    actual = [line for line in results]
    assert actual == expected

def test_ResultLog_can_add_different_types():
    results = ResultLog()
    sequence = ['line'+str(i) for i in range(5)]
    results.add(sequence)

    expected = ['OUT: line0', 'OUT: line1', 'OUT: line2', 'OUT: line3', 'OUT: line4']
    actual = list(results)
    assert actual == expected

    results2 = ResultLog()
    for line in sequence:
        results2.add(line)
    actual = list(results2)
    assert actual == expected

    results.add(results2)
    expected = ['OUT: line0', 'OUT: line1', 'OUT: line2', 'OUT: line3', 'OUT: line4',
                'OUT: line0', 'OUT: line1', 'OUT: line2', 'OUT: line3', 'OUT: line4']
    actual = list(results)
    assert actual == expected

def test_ResultLog_to_str():
    results = ResultLog()
    sequence = ['line'+str(i) for i in range(5)]
    results.add(sequence)

    expected = 'OUT: line0\nOUT: line1\nOUT: line2\nOUT: line3\nOUT: line4'
    actual = str(results)
    assert actual == expected
