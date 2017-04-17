from collections import Sequence

from .compat import to_str

STDOUT = 1
STDERR = 2
BUILDSPEC = 4


def format_line(line):
        output = line[1].rstrip()
        if line[0] == STDERR:
            return 'ERR: %s' % output
        elif line[0] == STDOUT:
            return 'OUT: %s' % output
        else:
            return output


class ResultLog(Sequence):
    def __init__(self, stdout=[], line_formatter=format_line):
        self.results = []
        self.add(stdout)
        self.line_formatter = line_formatter

    def add_line(self, line, rtype=STDOUT):
        self.results.append((rtype, to_str(line)))

    def add(self, str_or_iter, rtype=STDOUT):
        if isinstance(str_or_iter, type(self)):
            # self.add_line('WTF')
            self.results.extend(str_or_iter.results)
        elif isinstance(str_or_iter, str):
            self.add_line(str_or_iter, rtype)
        else:
            for line in str_or_iter:
                self.add_line(line, rtype)

    def __getitem__(self, index):
        return self.line_formatter(self.results[index])

    def __len__(self):
        return len(self.results)

    def __str__(self):
        sep = '\n'
        return sep.join(self)

    def __repr__(self):
        return str(self)


def stdstream(stream, rtype=STDOUT):
    return [(rtype, to_str(line)) for line in stream]


def stdout(out): return stdstream(out, STDOUT)


def stderr(err): return stdstream(err, STDERR)


def join_lines(lines):
    return '\n'.join(lines)
