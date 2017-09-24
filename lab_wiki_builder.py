#!/usr/bin/env python
"""this is the main file for lab wiki builder. it only parses arguments and then pass all arguments in to the
actual underlying function"""

import argparse
import os.path
from json import load
from sys import version_info

from labwikibuilder import builder

assert version_info >= (3, 6), "Python 3.6 or later to run this program!"


def main():
    # define the parser.
    parser = argparse.ArgumentParser(description='build lab wiki website.')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--ref', action='store_true', help='build reference library.')
    group.add_argument('--proj', action='store_true', help='build project library.')
    parser.add_argument('input', help='the root directory of library source files.')
    parser.add_argument('output', default=None, nargs='?',
                        help='the root directory of library output files. If not set, it will be equal to `input`.')
    # parse it
    args = parser.parse_args()

    # also, get the lab builder rc file, from `input/.labwikibuilderrc`
    with open(os.path.join(args.input, '.labwikibuilderrc'), encoding='utf-8') as f:
        labwikibuilderrc_dict = load(f)

    # build it.
    builder.builder(args, labwikibuilderrc_dict)


if __name__ == '__main__':
    main()
