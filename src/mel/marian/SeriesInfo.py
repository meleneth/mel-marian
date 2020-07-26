import json
import logging

from sqlalchemy import func
from tabulate import tabulate
from PyInquirer import prompt, print_json, Separator

from mel.marian.util import filename_safety
from mel.marian.tables import ShowDB, Show, Season, Episode

class SeriesInfo(object):
  def __init__(self, name):
    self.episodes = []
    self.name = name
  def load_show(self):
    self.show = Show.find(name=self.name)
    return self
  def interactive_db_audit_seriesdata(self):
    logger = logging.getLogger()
    for season in self.show.seasons:
      results = (ShowDB.session.query(
        Episode.episode_no,
        func.count(Episode.episode_no))
        .group_by(Episode.episode_no)
        .having(func.count(Episode.episode_no) > 1)
        .filter(Episode.season_id == season.id)
        .all()
      )
      needs_commit = False
      for result in results:
        logger.info(result)
        dupes = ShowDB.session.query(Episode).filter(Episode.season_id == season.id, Episode.episode_no == result[0]).all()
        question = [{
          'type': 'list',
          'name': 'episode_id',
          'message': 'Please select the episode to keep',
          'choices': [{'name': episode.name, 'value': episode.id} for episode in dupes]
        }]
        answer = prompt(question)
        for episode in dupes:
          if not episode.id == answer['episode_id']:
            ShowDB.session.delete(episode)
            needs_commit = True
    if needs_commit:
      ShowDB.session.commit()
  def is_single_season(self):
    return self.season_numbers() == [1]
  def display_season(self, season_no):
    self.display_episodes(self.season_episodes(season_no))
  def display_episodes(self, episodes):
    print(tabulate([[x['season_no'], x['episode_no'], x['name']] for x in episodes], tablefmt="pretty"))
  def episode_filename(self, episode, extension):
    return filename_safety("{0} - S{1}E{2} - {3}{4}".format(self.name, str(episode['season_no']).zfill(2), str(episode['episode_no']).zfill(2), episode['name'], extension))
