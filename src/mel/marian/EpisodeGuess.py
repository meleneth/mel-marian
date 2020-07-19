import os
import os.path

class EpisodeGuess(object):
  def __init__(self, filename):
    self.filename = filename
    self.season_no = None
    self.episode_no = None
    self.episode_name = None
    self.confidence = 0
    self.destination_filename = filename

  def is_video_file(self):
    extension = os.path.splitext(self.filename)[1]
    print("Extension is %s" % (extension))
    if extension.lower() in [".mkv", ".avi"]:
      return True
    return False

  def guesser_text(self):
      return "%s %s => %s" % (self.confidence, self.filename, self.destination_filename)
