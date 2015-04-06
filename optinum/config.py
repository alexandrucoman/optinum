"""
Global settings.
"""


# pylint: disable=R0903, W0232, C1001


class MISC:

    """Miscellaneous settings."""

    DEBUG = True     # show debugging messages or not
    TRIES = 3        # defaul number of tries


class DAEMON:

    """Daemon specific settings."""

    # default delay between complete processes and intensive iterations
    DELAY = 10
    FINEDELAY = DELAY * 0.1
    # concurrent matter
    WORKERS = 5     # default number of workers
    QSIZE = 0       # default task processor queue size (0 - unlimited)
    # other
    LOOP = True     # process the same tasks indefinitely
