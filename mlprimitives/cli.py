# -*- coding: utf-8 -*-

"""MLPrimitives Command Line Interface module."""

import argparse
import logging
import os
import sys
import warnings

from mlblocks import add_primitives_path, get_primitives_paths

from mlprimitives.evaluation import score_pipeline

LOGGER = logging.getLogger(__name__)


def _logging_setup(verbosity=1):
    logger = logging.getLogger()
    log_level = (3 - verbosity) * 10
    fmt = '%(asctime)s - %(levelname)s - %(message)s'
    formatter = logging.Formatter(fmt)
    logger.setLevel(log_level)
    logger.propagate = False

    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)


def _test(args):
    for pipeline in args.pipeline:
        print('Scoring pipeline: {}'.format(pipeline))
        score, stdev = score_pipeline(pipeline, args.splits)
        print('Obtained Score: {:.4f} +/- {:.4f}'.format(score, stdev))


def _list_primitives(base_path, pattern, primitives, parts=None):
    parts = parts or list()
    if os.path.exists(base_path):
        for name in os.listdir(base_path):
            path = os.path.abspath(os.path.join(base_path, name))
            if os.path.isdir(path):
                _list_primitives(path, pattern, primitives, parts + [name])
            else:
                name = '.'.join(parts + [name])
                if pattern in name and name.endswith('.json'):
                    primitives[path] = name[:-5]


def _get_primitives(pattern):
    primitives = dict()
    for base_path in get_primitives_paths():
        _list_primitives(base_path, pattern, primitives)

    return list(sorted(primitives.values()))


def _list(args):
    print('\n'.join(_get_primitives(args.pattern)))


class ArgumentParser(argparse.ArgumentParser):

    def error(self, message):
        sys.stderr.write('\nERROR: {}\n\n'.format(message))
        self.print_help()
        sys.exit(2)


def _get_parser():
    parser = ArgumentParser(
        description='MLPrimitives Command Line Interface')

    parser.add_argument(
        '-p', '--primitives-path', action='append', help=(
            'Path where primitives should be looked for. Use multiple '
            'times in order to add multiple directories'
        )
    )
    parser.add_argument('-v', '--verbose', action='count', default=0)

    subparsers = parser.add_subparsers(title='action', help='Action to perform')
    parser.set_defaults(action=None)

    subparser = subparsers.add_parser('test', help='Test a single pipeline.')
    subparser.set_defaults(action=_test)
    subparser.add_argument('-s', '--splits', default=1, type=int,
                           help='Number of splits to use for Cross Validation')
    subparser.add_argument('pipeline', nargs='+')

    subparser = subparsers.add_parser('list', help='List available primitives')
    subparser.set_defaults(action=_list)
    subparser.add_argument('pattern', nargs='?', default='')

    return parser


def _add_primitives_paths(paths):
    if paths:
        for path in paths:
            add_primitives_path(path)


def _process_common_args(args):
    _add_primitives_paths(args.primitives_path)
    _logging_setup(args.verbose)


def main():
    warnings.filterwarnings('ignore', category=DeprecationWarning)

    parser = _get_parser()
    args = parser.parse_args()
    if not args.action:
        parser.print_help()
        sys.exit(0)

    _process_common_args(args)

    args.action(args)