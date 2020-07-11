#!/usr/bin/env python
import argparse
import logging
import sys

def main():
  logging.basicConfig(format="%(asctime)s %(levelname)s: %(message)s",
    datefmt="%m/%d/%Y %I:%M:%S %p",
    level=logging.INFO,
    steam=sys.stdout)
  logger = logging.getLogger()

  parser = argparse.ArgumentParser(description='a program to do great things')
  subparsers = parser.add_subparsers(help='sub-command help')

  args = parser.parse_args()
  parser.func(args)