import logging

from PyInquirer import prompt, print_json, Separator
from statemachine import StateMachine, State
from tabulate import tabulate

from mel.marian import GuideFetcher, EpisodeRenamer, SeriesInfo, EpisodeGuess

class InteractiveMetaEdit(StateMachine):
  idle = State('Idle', initial=True)
  main_menu = State('Menu')
  show_seasons = State('ShowSeasons')
  seasons_menu = State('SeasonsMenu')

  choose = idle.to(main_menu) | show_seasons.to(seasons_menu)
  show_seasons = main_menu.to(seasons_menu)

  def set_seriesname(self, seriesname):
    self.seriesname = seriesname

  def on_enter_main_menu(self):
    logger = logging.getLogger()
    logger.info("Made it. but you still have to tell me what to do")
    seriesinfo = (SeriesInfo(self.seriesname)
      .load_show()
      .load_episodes())
    seriesinfo.display()

    renamer = EpisodeRenamer()
    renamer.load_media_files()
    renamer.guess_series(seriesinfo)
    renamer.display_guesses()

    self.question = [{
      'type': 'list',
      'name': 'choice',
      'message': 'Please choose a mode',
      'choices': [{'name': 'Seasons', 'value': self.show_seasons}]
    }]

  def on_enter_show_seasons(self):
    seasons = ShowDB.session.query(Season).all()

    logger = logging.getLogger()
    logger.info("seasons enter")
    question = [{
      'type': 'list',
      'name': 'choice',
      'message': 'Please choose a season',
      'choices': [{'name': season.name, 'value': season} for season in seasons]
    }]
    answer = prompt(question)
