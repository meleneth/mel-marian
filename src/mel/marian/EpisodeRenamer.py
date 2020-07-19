import os
import os.path

from PyInquirer import prompt, print_json, Separator
from tabulate import tabulate

from mel.marian.EpisodeGuess import EpisodeGuess

class EpisodeRenamer(object):
  def __init__(self):
    self.episodes = []
    self.extra_files = []
    self.series_info = False
    self.guesses = []

  def load_media_files(self):
    """Load all files from the current directory."""
    # Import the os module, for the os.walk function

    # Set the directory you want to start from
    rootDir = '.'
    for dirName, subdirList, fileList in os.walk(rootDir):
      print('Found directory: %s' % dirName)
      for fname in fileList:
        guesser = EpisodeGuess(fname)
        if guesser.is_video_file():
          self.guesses.append(guesser)

  def display_guesses(self):
    print(tabulate([[x.confidence, x.filename, x.destination_filename] for x in self.guesses], tablefmt="pretty"))

  def guess_file(self, filename):
    pass

  def guess_episodes(self):
    pass

  def guess_single_season(self):
    pass

  def guess_multiple_seasons(self):
    pass
