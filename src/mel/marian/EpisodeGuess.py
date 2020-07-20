import os
import os.path

from mel.marian.util import filename_safety

class EpisodeGuess(object):
  def __init__(self, filename):
    self.filename = filename
    self.season_no = None
    self.episode_no = None
    self.episode_name = None
    self.series_name = None
    self.confidence = 0
    self.destination_filename = filename
    self.extension = os.path.splitext(self.filename)[1].lower()

  def is_video_file(self):
    if self.extension in [".mkv", ".avi"]:
      return True
    return False
  def display_fields(self):
    return [str(self.season_no).zfill(2), str(self.episode_no).zfill(2), self.confidence, self.needs_rename(), self.episode_name, self.filename, self.destination_filename]
  def needs_rename(self):
    return not self.filename == self.destination_filename
  def guesser_text(self):
    return "{0} {1} => {2}".format(self.confidence, self.filename, self.destination_filename)
  def generate_destination_filename(self):
    filename = "{0} - S{1}E{2} - {3}{4}".format(self.series_name, str(self.season_no).zfill(2), str(self.episode_no).zfill(2), self.episode_name, self.extension)
    self.destination_filename = filename_safety(filename)
