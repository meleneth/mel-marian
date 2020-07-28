from mel.marian import Guesser

class PositionalGuesser(Guesser):
  def guess(self, renamer, seriesinfo):
    for guess, episode in zip(renamer.guesses, seriesinfo.episodes):
      if not guess.confidence:
        guess.confidence = 50
        guess.episode_no = episode.episode_no
        guess.episode_name = episode.name
        guess.series_name = seriesinfo.show.name
        guess.generate_destination_filename()
