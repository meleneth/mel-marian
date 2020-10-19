"""Select a season, then interactively assign media files"""
import logging
from functools import partial
import sys
import os
import subprocess

from PyInquirer import prompt, print_json, Separator
from statemachine import StateMachine, State
from tabulate import tabulate

from mel.marian.tables import ShowDB, Show, Season, Episode
from mel.marian import GuideFetcher, EpisodeRenamer, SeriesInfo, EpisodeGuess

def season_format(season):
  return "id(%s) season_no(%s) name(%s)" % (season.id, season.season_no, season.name)

class InteractiveSeasonRename(StateMachine):
  idle = State('Idle', initial=True)
  season_select = State('SeasonSelect')
  guess_select = State('GuessSelect')
  episode_select = State('EpisodeSelect')

  go = idle.to(season_select) \
    | season_select.to(guess_select) \
    | guess_select.to(episode_select) \
    | episode_select.to(guess_select)

  back = episode_select.to(guess_select) \
    | guess_select.to(season_select)

  def q(self, message, choices):
    self.question = [{
      'type': 'list',
      'name': 'choice',
      'message': message,
      'choices': choices
    }]

  def matched_guesses(self):
    guesses = []
    for guess in self.guesses:
      if guess.confidence > 99:
        guesses.append(guess)
    return guesses

  def unmatched_guesses(self):
    guesses = []
    for guess in self.guesses:
      if guess.confidence < 100:
        guesses.append(guess)
    return guesses

  def unmatched_episodes(self):
    episodes = []
    for episode in self.episodes:
      matched = False
      filename = episode.filename()
      for guess in self.matched_guesses():
        if guess.destination_filename == filename:
          matched = True
      if not matched:
        episodes.append(episode)
    return episodes

  def set_seriesname(self, seriesname):
    self.seriesname = seriesname

  def user_choice_season(self, season):
    logger = logging.getLogger()
    logger.info("Setting selected season to %s" % (season.season_no))
    self.selected_season = season

    seriesinfo = (SeriesInfo(self.seriesname)
      .load_show()
      .load_episodes())

    self.episodes = [x for x in seriesinfo.episodes if x.season.season_no == self.selected_season.season_no]

    renamer = EpisodeRenamer()
    renamer.load_media_files()
    renamer.guess_series(seriesinfo)
    self.guesses = [x for x in renamer.guesses if x.season_no == self.selected_season.season_no]
    self.go()

  def user_choice_guess(self, guess):
    logger = logging.getLogger()
    logger.info("Choosing to edit %s" % (guess.filename))
    self.selected_guess = guess
    self.go()

  def user_choice_episode(self, episode):
    self.selected_guess.episode_no = episode.episode_no
    self.selected_guess.episode_name = episode.name
    self.selected_guess.generate_destination_filename()
    self.selected_guess.confidence = 100
    self.go()

  def user_choice_play_episode(self):
    subprocess.Popen([r"C:\Program Files (x86)\VideoLAN\VLC\vlc.exe", self.selected_guess.filename])
    flag = "--video-on-top"

  def on_enter_season_select(self):
    seasons = ShowDB.session.query(Season).order_by(Season.season_no).all()
    choices = [
      {'name': season_format(season),
      'value': partial(self.user_choice_season, season)}
      for season in seasons
    ]
    choices.append({'name': 'apply renames', 'value': self.rename_files})
    choices.append({'name': 'exit, discarding changes', 'value': sys.exit})
    self.q("Please choose a season", choices)

  def on_enter_guess_select(self):
    logger = logging.getLogger()
    logger.info("+----------------------+")
    logger.info("+ Matched Guesses      +")
    logger.info("+----------------------+")
    for guess in self.matched_guesses():
      logger.info("%s --> %s" % (guess.filename, guess.destination_filename))
    logger.info("+----------------------+")
    logger.info("+ UnMatched Guesses    +")
    logger.info("+----------------------+")
    for guess in self.unmatched_guesses():
      logger.info("%s" % (guess.filename))
    logger.info("+----------------------+")
    logger.info("+ UnMatched Episodes   +")
    logger.info("+----------------------+")
    for guess in self.unmatched_episodes():
      logger.info("%s" % (guess.name))

    episodes = self.selected_season.episodes
    choices = [
      {'name': "%s" % (guess.filename),
      'value': partial(self.user_choice_guess, guess)}
      for guess in self.unmatched_guesses()
    ]
    choices.append({'name': 'go back to season select', 'value': self.back})
    choices.append({'name': 'rename files', 'value': self.rename_files})
    self.q("Please choose a episode", choices)

  def on_enter_episode_select(self):
    choices = [
      {'name': "%s %s  --  %s" % (episode.episode_no, "{:<20}".format(episode.name), "{:<30}".format(episode.description)),
      'value': partial(self.user_choice_episode, episode)}
      for episode in self.unmatched_episodes()
    ]
    choices.append({'name': 'go back to file select', 'value': self.back})
    actual_choices = [{'name': 'play episode', 'value': self.user_choice_play_episode}]
    for choice in choices:
      actual_choices.append(choice)
    self.q("Please choose a episode", actual_choices)

  def rename_files(self):
    logger = logging.getLogger()
    logger.info("Renaming files")

    for guess in self.guesses:
      if guess.confidence > 99:
        if guess.filename != guess.destination_filename:
          if os.path.exists(guess.destination_filename):
            logging.info("Destination already exists - ignoring" % (guess.destination_filename))
            continue
          os.rename(guess.filename, guess.destination_filename)
          guess.filename = guess.destination_filename
