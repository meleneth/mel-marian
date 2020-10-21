import os
import os.path

import flexmock
from bs4 import BeautifulSoup

from mel.marian.episodeguiderename.commandline import get_parser
from mel.marian.episodeguiderename.commandline import entry_default
from mel.marian.episodeguiderename.commandline import entry_edit
from mel.marian.EpisodeRenamer import EpisodeRenamer
from mel.marian.EpisodeGuess import EpisodeGuess

def test_argparser_handles_basic_case():
  parser = get_parser()
  args = parser.parse_args([])
  assert args.func == entry_default

def test_argparser_handles_edit():
  parser = get_parser()
  args = parser.parse_args(['edit'])
  assert args.func == entry_edit

def test_episoderenamer_guess_seasons():
  er = EpisodeRenamer()
  eg = EpisodeGuess("Foo Season 1 track 4.mkv")
  er.guesses = [eg]

  er.guess_seasons()

  assert eg.season_no == 1

def test_episoderenamer_guess_seasons_short_form():
  er = EpisodeRenamer()
  eg = EpisodeGuess("Foo S01E45 track 4.mkv")
  er.guesses = [eg]

  er.guess_seasons()

  assert eg.season_no == 1
