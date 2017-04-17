__version__ = "0.2.0"

import yaml

BUILDSPEC_YML = 'buildspec.yml'


def load_file(filename):
    with open(filename, 'r') as fp:
        return yaml.load(fp)


PHASE_ORDER = {'install': 10, 'pre_build': 20, 'build': 30, 'post_build': 40}


def sort_phases(phases):
    """ Sort phases in order defined in AWS buildspec reference """
    def sorter(phase):
        return PHASE_ORDER[phase]

    return sorted(phases, key=sorter)


def decide_phases(desired_phases, spec):
    """ Given:
        - a list of the desired phases to run
        - the buildspec
        Return a list of phases to run in the correct order.

        ???Should a missing phase be an error or a warning???
        Empty list for desired_phases means run all defined phases.
    """
    if 'phases' not in spec:
        return []
    if desired_phases:
        phases = []
        for phase in desired_phases:
            if phase in spec['phases']:
                phases.append(phase)
            else:
                raise Exception('Phase [%s] not defined' % phase)
    else:
        phases = [phase for phase, commands in spec['phases'].items()]

    return sort_phases(phases)


def validate_phases(phases):
    """ Given a list of phases throw exception if one is an invalid buildspec
        phase.
    """
    for phase in phases:
        if phase not in PHASE_ORDER:
            raise Exception('Invalid buildspec phase: [%s]' % phase)


def suggest_phase(phase):
    """ Given an invalid phase, suggest the closest ones. (git style) """
