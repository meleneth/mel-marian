from mel.marian import Guesser

class PositionalGuesser(Guesser):
  def guess(self, renamer, seriesinfo):
    for season_no in seriesinfo.season_numbers():
      guesses = renamer.season_guesses(season_no)
      episodes = seriesinfo.season_episodes(season_no)
      print(guesses)
      print(episodes)
      for guess, episode in zip(renamer.guesses, episodes):
        if not guess.confidence:
          guess.confidence = 50
          guess.episode_no = episode['episode_no']
          guess.episode_name = episode['name']
          guess.series_name = seriesinfo.name
          guess.generate_destination_filename()
