import json
import logging

from sqlalchemy import func
from tabulate import tabulate

from mel.marian.util import filename_safety
from mel.marian.tables import ShowDB, Show, Season, Episode

class SeriesInfo(object):
  def __init__(self, name):
    self.episodes = []
    self.name = name
  def load_episode_info(self, filename):
    with open(filename) as f:
      self.episodes = json.load(f)
      sorted_eps = sorted(self.episodes, key=lambda x: x["season_no"])
      self.episodes = sorted(sorted_eps, key=lambda x: x["episode_no"])
    return self
  def load_show(self):
    self.show = Show.find(name=self.name)
    return self
  def save_episode_info(self):
    with open(self.saved_info_filename(), "w") as f:
     f.write(json.dumps(self.episodes))
    return self
  def saved_info_filename(self):
    return "%s.json" % (self.episodes[0]['show_name'])
  def season_numbers(self):
    return list(set([x["season_no"] for x in self.episodes]))
  def season_episode_numbers(self, season_no):
    return list(set([x["episode_no"] for x in self.season_episodes(season_no)]))
  def season_episodes(self, season_no):
    return list(filter(lambda x: x['season_no'] == season_no, self.episodes))
  def matching_episodes(self, season_no, episode_no):
    return list(filter(lambda x: x['season_no'] == season_no and x['episode_no'] == episode_no, self.episodes))
  def interactive_db_audit_seriesdata(self):
    logger = logging.getLogger()
    for season in self.show.seasons:
      logger.info("---------And now, a penguin wearing a hat")
      results = (ShowDB.session.query(
        Episode.episode_no,
        func.count(Episode.episode_no))
        .group_by(Episode.episode_no)
        .having(func.count(Episode.episode_no) > 1)
        .filter(Episode.season_id == season.id)
        .all()
      )
      for result in results:
        logger.info(result)
        dupes = ShowDB.session.query(Episode).filter(Episode.season_id == season.id, Episode.episode_no == result[0]).all()
        print(dupes)

    logger.info("Alas sweet yorick, I kissed him")
  def interactive_audit_seriesdata(self):
    logger = logging.getLogger()
    season_numbers = self.season_numbers()
    made_changes = False
    for season_number in season_numbers:
      season_episode_numbers = self.season_episode_numbers(season_number)
      season_episodes = self.season_episodes(season_number)
      if len(season_episodes) != len(season_episode_numbers):
        logger.info("Strange data detected! num_episodes != num_unique episodes")
      for episode_no in season_episode_numbers:
        episodes = self.matching_episodes(season_number, episode_no)
        if len(episodes) != 1:
          logger.info("Not a single episode for episode %s" % (episode_no))
          answer = self.interactive_ask_dupe_episodes(episodes)
          episode_to_keep = list(filter(lambda x: x['name'] == answer['episode_name'], episodes))[0]
          for episode in episodes:
            if not episode is episode_to_keep:
              self.episodes.remove(episode)
              made_changes = True
      if made_changes:
        self.interactive_confirm_save_episode_info()
      self.display_episodes(season_episodes)
  def interactive_confirm_save_episode_info(self):
    questions = [{
      'type': 'list',
      'name': 'save_episodes',
      'message': 'Save newly trimmed episode metadata?',
      'choices': ['No', 'Yes']
    }]
    answers = prompt(questions)
    if answers['save_episodes'] == 'Yes':
      self.save_episode_info()
  def display(self):
    print(self.season_numbers())
    for season_no in self.season_numbers():
      print("Season %d" % (season_no))
      self.display_season(season_no)
  def is_single_season(self):
    return self.season_numbers() == [1]
  def display_season(self, season_no):
    self.display_episodes(self.season_episodes(season_no))
  def display_episodes(self, episodes):
    print(tabulate([[x['season_no'], x['episode_no'], x['name']] for x in episodes], tablefmt="pretty"))
  def interactive_ask_dupe_episodes(self, episodes):
    self.display_season(episodes[0]['season_no'])
    questions = [{
      'type': 'list',
      'name': 'episode_name',
      'message': 'Please select the episode to keep',
      'choices': [episode['name'] for episode in episodes]
    }]
    return prompt(questions)
  def episode_filename(self, episode, extension):
    return filename_safety("{0} - S{1}E{2} - {3}{4}".format(self.name, str(episode['season_no']).zfill(2), str(episode['episode_no']).zfill(2), episode['name'], extension))
