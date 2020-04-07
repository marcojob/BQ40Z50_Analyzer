#!/usr/bin/env python3

"""Main script to interface bq40z50 with ev2300"""

__author__ = 'Marco Job'

from array import array
from time import sleep

from src.bq40z50 import BQ40Z50
from src.utils import *

def main():
    bq = BQ40Z50()

    bq.get_summary()

if __name__ == "__main__":
    main()