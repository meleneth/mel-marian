import os
import os.path
import re

from PyInquirer import prompt, print_json, Separator
from tabulate import tabulate

from mel.marian.EpisodeGuess import EpisodeGuess
from mel.marian.FilenameGuesser import FilenameGuesser
from mel.marian import PositionalGuesser

class EpisodeRenamer(object):
  def __init__(self):
    self.episodes = []
    self.extra_files = []
    self.series_info = False
    self.guesses = []

  def guess_seasons(self):
    for guess in self.guesses:
      if (m := re.search(r"Season (\d+)", guess.filename)):
        guess.season_no = int(m.group(1))
      if (m := re.search(r"S(\d+)E(\d+)", guess.filename)):
        guess.season_no = int(m.group(1))

  def load_media_files(self):
    """Load all files from the current directory."""
    for dirName, subdirList, fileList in os.walk('.'):
      print('Found directory: %s' % dirName)
      for fname in fileList:
        guesser = EpisodeGuess(fname)
        if guesser.is_video_file():
          self.guesses.append(guesser)

  def display_guesses(self):
    print(tabulate([x.display_fields() for x in self.guesses]))

  def season_guesses(self, season_no):
    return list(filter(lambda x: x.season_no == season_no, self.guesses))

  def guess_series(self, seriesinfo):
    #seriesinfo.display()
    if seriesinfo.is_single_season():
      for guess in self.guesses:
        guess.season_no = 1
    FilenameGuesser().guess(self, seriesinfo)
    PositionalGuesser().guess(self, seriesinfo)
  def any_need_renaming(self):
    for guess in self.guesses:
      if guess.needs_rename():
        return True
    return False

  def confirm_and_move_files(self):
    questions = [{
      'type': 'list',
      'name': 'move_files',
      'message': 'Move files',
      'choices': ['No', 'Yes']
    }]
    answers = prompt(questions)
    if answers['move_files'] == 'Yes':
      self.safely_move_files()

  def safely_move_files(self):
    for guess in self.guesses:
      source = guess.filename
      destination = guess.destination_filename
      if source == destination:
        logging.info("No change for %s" % (source))
        continue
      if os.path.exists(destination):
        logging.info("Destination already exists - ignoring" % (destination))
        continue
      os.rename(source, destination)

  def guess_file(self, filename):
    pass

  def guess_episodes(self):
    pass

  def guess_single_season(self):
    pass

  def guess_multiple_seasons(self):
    pass
