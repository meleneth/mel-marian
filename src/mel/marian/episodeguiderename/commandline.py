#!/usr/bin/env python
import argparse
import logging
import sys
import os

from tabulate import tabulate
from PyInquirer import prompt, print_json, Separator

from mel.marian import GuideFetcher, EpisodeRenamer, SeriesInfo, EpisodeGuess
from mel.marian.tables import ShowDB, Show, Season, Episode

def main():
  logging.basicConfig(
    format="%(asctime)s %(levelname)s: %(message)s",
    datefmt="%m/%d/%Y %I:%M:%S %p",
    level=logging.INFO,
    stream=sys.stdout
  )
  logger = logging.getLogger()

  cwd = os.getcwd()
  logger.info("Starting run in directory: %s" % (cwd))
  seriesname = os.path.basename(cwd)
  logger.info("Using '%s' as series name" % (seriesname))

  ShowDB.connect(seriesname)
  if ShowDB.db_existed:
   logger.info("Found series info DB")
  else:
    fetcher = GuideFetcher()
    fetcher.find_guide(seriesname)
    fetcher.save_guide_db(seriesname)
  seriesinfo = SeriesInfo(seriesname).load_show()
  seriesinfo.interactive_db_audit_seriesdata()
  seriesinfo.load_episodes()
  renamer = EpisodeRenamer()
  renamer.load_media_files()
  renamer.guess_series(seriesinfo)
  renamer.display_guesses()
  if renamer.any_need_renaming():
    renamer.confirm_and_move_files()
