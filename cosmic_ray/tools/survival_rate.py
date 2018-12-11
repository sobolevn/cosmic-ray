"Tool for printing the survival rate in a session."

import docopt

from cosmic_ray.work_db import use_db


def survival_rate():
    """cr-rate

    Usage: cr-rate <session-file>

    Calculate the survival rate of a session.
    """
    arguments = docopt.docopt(survival_rate.__doc__, version='cr-rate 1.0')
    with use_db(arguments['<session-file>']) as db:
        rate = _calculate_survival_rate(db) 

    print('{:.2f}'.format(rate))


def _calculate_survival_rate(work_db):
    """Calcuate the survival rate for the results in a WorkDB.
    """
    kills = sum(r.is_killed for _, r in work_db.results)
    num_results = work_db.num_results

    if not num_results:
        return 0

    return (1 - kills / num_results) * 100
