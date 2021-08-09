import os
import os.path

import flexmock
from bs4 import BeautifulSoup

from mel.marian.episodeguiderename.commandline import get_parser
from mel.marian.episodeguiderename.commandline import entry_default
from mel.marian.episodeguiderename.commandline import entry_edit
from mel.marian.episodeguiderename.interactive_season_rename import InteractiveSeasonRename

from mel.marian.EpisodeRenamer import EpisodeRenamer
from mel.marian.EpisodeGuess import EpisodeGuess

def test_interactive_season_rename_long_involved_test():
  isr = InteractiveSeasonRename()
  eg = EpisodeGuess("Foo Season 1 track 4.mkv")
  episode = flexmock(filename=lambda: 'Foo S01E01 Pilot.mkv')

  isr.guesses = [eg]
  isr.episodes = [episode]

  result = isr.unmatched_episodes()

  assert result == [episode]
