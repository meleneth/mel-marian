import logging
from functools import partial

from PyInquirer import prompt, print_json, Separator
from statemachine import StateMachine, State
from tabulate import tabulate

from mel.marian.tables import ShowDB, Show, Season, Episode
from mel.marian import GuideFetcher, EpisodeRenamer, SeriesInfo, EpisodeGuess

class InteractiveMetaEdit(StateMachine):
  idle = State('Idle', initial=True)
  main_menu = State('Menu')
  season_select = State('SeasonSelect')
  season_operation_select = State('SeasonOperationSelect')

  go_display_choices = idle.to(main_menu)
  go_show_seasons = main_menu.to(season_select)
  go_select_season_operation = season_select.to(season_operation_select)

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
    seasons = ShowDB.session.query(Season).all()
    choices = [
      {'name': "id(%s) season_no(%s) name(%s)" % (season.id, season.season_no, season.name),
      'value': partial(self.user_choice_season, season)}
      for season in seasons
    ]
    self.q("Please choose a season", choices)

  def on_enter_season_operation_select(self):
    print(tabulate([[x.season.season_no, x.episode_no, x.name] for x in self.selected_season.episodes], tablefmt="pretty"))

    choices = [{'name': "huff and puff", 'value': self.selected_season}]
    self.q("Seasons operation select enter", choices)
