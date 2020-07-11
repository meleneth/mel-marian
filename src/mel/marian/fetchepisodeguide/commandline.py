#!/usr/bin/env python
import argparse
import logging
import sys

from mel.marian import GuideFetcher

def main():
  logging.basicConfig(format="%(asctime)s %(levelname)s: %(message)s",
    datefmt="%m/%d/%Y %I:%M:%S %p",
    level=logging.INFO,
    stream=sys.stdout)
  logger = logging.getLogger()

  seriesname = " ".join(sys.argv[1:])
  logger.info("%s" % (seriesname))
