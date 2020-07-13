#!/usr/bin/env python
import argparse
import logging
import sys
import os

from tabulate import tabulate
from PyInquirer import prompt, print_json, Separator

from mel.marian import GuideFetcher, EpisodeRenamer, SeriesInfo, EpisodeGuess

def main():
  logging.basicConfig(format="%(asctime)s %(levelname)s: %(message)s",
    datefmt="%m/%d/%Y %I:%M:%S %p",
    level=logging.INFO,
    stream=sys.stdout)
  logger = logging.getLogger()

  cwd = os.getcwd()
  logger.info("Starting run in directory: %s" % (cwd))
  seriesname = os.path.basename(cwd)
  logger.info("Using '%s' as series name" % (seriesname))
  series_info_filename = os.path.join(cwd, "%s.json" % (seriesname))
  if os.path.exists(series_info_filename):
    logger.info("Found series info .json")
  else:
    fetcher = GuideFetcher()
    fetcher.find_guide(seriesname)
    fetcher.save_guide(seriesname)
  seriesinfo = SeriesInfo(seriesname).load_episode_info(series_info_filename)
  seriesinfo.interactive_audit_seriesdata()
  logger.info("---- back in script land ----")
  print(tabulate([[x['season_no'], x['episode_no'], x['name']] for x in seriesinfo.episodes], tablefmt="pretty"))
