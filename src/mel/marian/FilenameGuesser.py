from mel.marian import Guesser

class FilenameGuesser(Guesser):
  def guess(self, renamer, seriesinfo):
      guesses = renamer.guesses
      for episode in seriesinfo.episodes:
        prospective_filename = seriesinfo.episode_filename(episode, guesses[0].extension)
        for guess in guesses:
          if guess.filename == prospective_filename:
            guess.confidence = 75
            guess.episode_no = episode.episode_no
            guess.episode_name = episode.name
            guess.series_name = seriesinfo.name
