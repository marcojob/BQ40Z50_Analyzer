#!/usr/bin/env python3

"""Main script to interface bq40z50 with ev2300"""

__author__ = 'Marco Job'

from argparse import ArgumentParser
from array import array
from time import sleep

from src.bq40z50 import BQ40Z50
from src.utils import *

def main():
    # Handle arguments
    parser = ArgumentParser()
    parser.add_argument('--report', '-r',
                        help='Generate a report of batteries',
                        action='store_true')
    parser.add_argument('--monitor', '-m',
                        help='Monitor a battery',
                        type=str,
                        default='')
    args = parser.parse_args()

    # Actual code
    bq = BQ40Z50()
    if args.report:
        bq.create_summary()
    elif args.monitor:
        bq.create_monitor(args.monitor)
    else:
        print('No argument specified.')

if __name__ == "__main__":
    main()