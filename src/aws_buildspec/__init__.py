__version__ = "0.1.0"

import yaml

def load_file(filename):
    with open(filename, 'r') as fp:
        return yaml.load(fp)
