#!/usr/bin/env python
import argparse
import logging
import sys
import os

from tabulate import tabulate
from PyInquirer import prompt, print_json, Separator

from mel.marian import GuideFetcher, EpisodeRenamer, SeriesInfo, EpisodeGuess
from mel.marian.tables import ShowDB, Show, Season, Episode
from mel.marian.episodeguiderename.interactive_meta_edit import InteractiveMetaEdit
from mel.marian.episodeguiderename.interactive_season_rename import InteractiveSeasonRename

def entry_edit(args, seriesname):
  logger = logging.getLogger()
  interactive = InteractiveMetaEdit()
  interactive.set_seriesname(seriesname)
  interactive.go_display_choices()

  while(True):
    logger.info("Current state is: %s", interactive.current_state)
    answer = prompt(interactive.question)
    if answer['choice']:
      answer['choice']()

def entry_season_rename(args, seriesname):
  logger = logging.getLogger()
  interactive = InteractiveSeasonRename()
  interactive.set_seriesname(seriesname)
  interactive.go()

  while(True):
    #logger.info("Current state is: %s", interactive.current_state)
    answer = prompt(interactive.question)
    if answer['choice']:
      answer['choice']()

def entry_default(args, seriesname):
  logger = logging.getLogger()
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

def get_parser():
  parser = argparse.ArgumentParser(description='a program to do great things')
  parser.set_defaults(func=entry_default)
  subparsers = parser.add_subparsers(help='sub-command help')

  renamer_edit_parser = subparsers.add_parser('edit', help='')
  renamer_edit_parser.set_defaults(func=entry_edit)

  renamer_renameseason_parser = subparsers.add_parser('seasonrename', help='')
  renamer_renameseason_parser.set_defaults(func=entry_season_rename)

  return parser

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

  parser = get_parser()
  args = parser.parse_args()

  args.func(args, seriesname)
