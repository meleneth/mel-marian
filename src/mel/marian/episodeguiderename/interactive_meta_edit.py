import logging
from functools import partial

from PyInquirer import prompt, print_json, Separator
from statemachine import StateMachine, State
from tabulate import tabulate

from mel.marian.tables import ShowDB, Show, Season, Episode
from mel.marian import GuideFetcher, EpisodeRenamer, SeriesInfo, EpisodeGuess

def season_format(season):
  return "id(%s) season_no(%s) name(%s)" % (season.id, season.season_no, season.name)

class InteractiveMetaEdit(StateMachine):
  idle = State('Idle', initial=True)
  main_menu = State('Menu')
  season_select = State('SeasonSelect')
  season_operation_select = State('SeasonOperationSelect')
  episode_select = State('EpisodeSelect')
  episode_operation_select = State('EpisodeOperationSelect')
  edit_episode_name = State("EditEpisodeName")
  edit_episode_episode_no = State("EditEpisodeEpisodeNo")
  edit_episode_season = State("EditEpisodeSeason")

  go_display_choices = idle.to(main_menu)
  go_show_seasons = main_menu.to(season_select)
  go_select_season_operation = season_select.to(season_operation_select) \
    | episode_operation_select.to(season_operation_select)
  go_select_episode_operation = season_operation_select.to(episode_operation_select)
  go_episode_select = season_operation_select.to(episode_select)
  go_back = season_select.to(main_menu) \
    | episode_select.to(season_select) \
    | season_operation_select.to(season_select) \
    | edit_episode_name.to(episode_operation_select) \
    | edit_episode_episode_no.to(episode_operation_select) \
    | edit_episode_season.to(episode_operation_select) \
    | episode_operation_select.to(season_operation_select)
  go_edit_episode_name = episode_operation_select.to(edit_episode_name)
  go_edit_episode_episode_no = episode_operation_select.to(edit_episode_episode_no)
  go_edit_episode_season = episode_operation_select.to(edit_episode_season)

  def set_seriesname(self, seriesname):
    self.seriesname = seriesname

  def user_choice_series_info(self):
    seriesinfo = (SeriesInfo(self.seriesname)
      .load_show()
      .load_episodes())
    seriesinfo.display()

    renamer = EpisodeRenamer()
    renamer.load_media_files()
    renamer.guess_series(seriesinfo)
    renamer.display_guesses()

  def user_choice_season(self, season):
    logger = logging.getLogger()
    logger.info("Setting selected season to %s" % (season.season_no))
    self.selected_season = season
    self.go_select_season_operation()

  def user_choice_season_episode(self, episode):
    logger = logging.getLogger()
    logger.info("Setting selected episode to %s" % (episode.name))
    self.selected_episode = episode
    self.go_select_episode_operation()

  def user_choice_renumber_season_episodes(self):
    episodes = self.selected_season.episodes
    episodes.sort(key=lambda x: x.episode_no)
    for episode_no, episode in enumerate(episodes, start=1):
      episode.episode_no = episode_no
    ShowDB.commit()

  def user_choice_delete_selected_episode(self):
    logger = logging.getLogger()
    logger.info("(not) Deleting episode %s" % (self.selected_episode.name))
    ShowDB.delete(self.selected_episode)
    ShowDB.commit()
    self.selected_episode = None
    self.go_select_season_operation()

  def user_choice_episode_set_season(self, season):
    self.selected_episode.season = season
    ShowDB.commit()
    self.go_back()

  def q(self, message, choices):
    self.question = [{
      'type': 'list',
      'name': 'choice',
      'message': message,
      'choices': choices
    }]

  def on_enter_main_menu(self):
    choices = [
      {'name': 'Seasons', 'value': self.go_show_seasons},
      {'name': 'Series Info', 'value': self.user_choice_series_info}
    ]
    self.q("Please choose a mode", choices)

  def on_enter_season_select(self):
    seasons = ShowDB.session.query(Season).order_by(Season.season_no).all()
    choices = [
      {'name': season_format(season),
      'value': partial(self.user_choice_season, season)}
      for season in seasons
    ]
    choices.append({'name': 'go back to main menu', 'value': self.go_back})
    self.q("Please choose a season", choices)

  def on_enter_season_operation_select(self):
    print(self.selected_season.name)
    print(tabulate([[x.season.season_no, x.episode_no, x.name] for x in self.selected_season.episodes], tablefmt="pretty"))

    episodes = self.selected_season.episodes
    episodes.sort(key=lambda x: x.episode_no)
    choices = [
      {'name': "id(%s) episode_no(%s) name(%s)" % (episode.id, episode.episode_no, episode.name),
      'value': partial(self.user_choice_season_episode, episode)}
      for episode in episodes
    ]
    choices.append({'name': 'renumber season episodes', 'value': self.user_choice_renumber_season_episodes})
    choices.append({'name': 'go back to main menu', 'value': lambda : [self.go_back, self.go_back]})
    choices.append({'name': 'go back to season select menu', 'value': self.go_back})

    self.q("Seasons operation select enter", choices)

  def on_enter_episode_select(self):
    episodes = ShowDB.session.query(Season).order_by(Season.season_no).all()
    choices = [
      {'name': "id(%s) season_no(%s) name(%s)" % (season.id, season.season_no, season.name),
      'value': partial(self.user_choice_season, season)}
      for season in seasons
    ]
    choices.append({'name': 'go back to main menu', 'value': self.go_back})
    self.q("Please choose a season", choices)

  def on_enter_episode_operation_select(self):
    print(self.selected_season.name)
    print(self.selected_episode.name)

    choices = [
      {'name': "edit name", 'value': self.go_edit_episode_name},
      {'name': "edit episode_no", 'value': self.go_edit_episode_episode_no},
      {'name': "change season", 'value': self.go_edit_episode_season},
      {'name': "delete episode", 'value': self.user_choice_delete_selected_episode}
    ]
    choices.append({'name': 'go back to main menu', 'value': lambda : [self.go_back, self.go_back]})
    choices.append({'name': 'go back to season select menu', 'value': self.go_back})

    self.q("Seasons operation select enter", choices)

  def on_enter_edit_episode_name(self):
    question = [{
      'type': 'input',
      'name': 'episode_name',
      'default': self.selected_episode.name,
      'message': "episode name"
    }]
    answer = prompt(question)
    self.selected_episode.name = answer['episode_name']
    ShowDB.commit()
    self.go_back()

  def on_enter_edit_episode_episode_no(self):
    question = [{
      'type': 'input',
      'name': 'episode_no',
      'default': str(self.selected_episode.episode_no),
      'message': "episode number"
    }]
    answer = prompt(question)
    self.selected_episode.episode_no = int(answer['episode_no'])
    ShowDB.commit()
    self.go_back()

  def on_enter_edit_episode_season(self):
    seasons = ShowDB.session.query(Season).order_by(Season.season_no).all()
    choices = [
      {'name': season_format(season),
      'value': partial(self.user_choice_episode_set_season, season)}
      for season in seasons
    ]
    choices.append({'name': 'go back to episode operation select', 'value': self.go_back})

    question = [{
      'type': 'list',
      'name': 'choice',
      'message': "Select season to move the episode to",
      'choices': choices
    }]
    answer = prompt(question)
    answer['choice']()
