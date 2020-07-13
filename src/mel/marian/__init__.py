import re
import logging
import time
import json
import os.path

from tabulate import tabulate
from PyInquirer import prompt, print_json, Separator

import requests
from bs4 import BeautifulSoup

class GuideFetcher(object):
  def __init__(self):
    self.episodes = []
    self.base_url = "http://www.tv.com"

  def fetch_and_parse_url(self, url):
    time.sleep(10)
    url = "%s%s" % (self.base_url, url)
    logger = logging.getLogger()
    logger.info(url)
    page = requests.get(url)
    soup = BeautifulSoup(page.text, 'html.parser')
    return soup

  def find_guide(self, name):
    soup = self.fetch_and_parse_url("/search?q=%s" % (name.replace(" ", "%20")))
    url = self.parse_search_result(soup)
    soup = self.fetch_and_parse_url(url)
    season_urls = self.parse_series(soup, url)
    for url in season_urls:
      soup = self.fetch_and_parse_url(url)
      self.parse_season(soup)

  def save_guide(self, name):
    with open("%s.json" % (name), "w") as f:
      f.write(json.dumps(self.episodes))

  def parse_search_result(self, soup):
    logger = logging.getLogger()
    links = soup.find_all("a")
    links = list(filter(lambda x: re.search("Episode Guide", x.text), soup.find_all('a')))
    episode_guide_url = links[0]["href"]
    return episode_guide_url

  def parse_series(self, soup, url):
    div = soup.find_all("div", class_="_col_a1")[0]
    return list(filter(lambda x: x != url, [x["href"] for x in div.find_all("a")]))

  def parse_season(self, soup):
    (title, season)= soup.find_all("title")[0].text.strip().split(" - ")[0:2]
    season = int(season.replace("Season ", ""))
    episodes = [x.parent for x in soup.find_all("div", class_="description")]
    for episode in episodes:
      info = {}
      info["show_name"] = title
      info['season_no'] = season
      info['name'] = episode.find("a", class_="title").text.strip()
      info['air_date'] = episode.find("div", class_="date").text.strip()
      info['description'] = episode.find("div", class_="description").text.strip()
      info['episode_no'] = int(episode.find("div", class_="ep_info").text.strip().replace("Episode ", ""))
      if info['episode_no']:
        self.episodes.append(info)

class SeriesInfo(object):
  def __init__(self, name):
    self.episodes = []
    self.name = name
  def load_episode_info(self, filename):
    with open(filename) as f:
     self.episodes = json.load(f)
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
          for episode in episodes:
            logger.info(answer)
            if episode['name'] != answer['episode_name']:
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

class EpisodeGuess(object):
  def __init__(self, filename):
    self.filename = filename
    self.season_no = None
    self.episode_no = None
    self.episode_name = None
    self.destination_filename = filename

  def is_video_file(self):
    extension = os.path.splitext(self.filename)[1]
    print("Extension is %s" % (extension))
    if extension.lower() in [".mkv", ".avi"]:
      return True
    return False

class EpisodeRenamer(object):
  def __init__(self):
    self.episodes = []
    self.extra_files = []
    self.series_info = False

  def load_media_files(self):
    """Load all files from the current directory."""
    pass

  def guess_file(self, filename):
    pass

  def guess_episodes(self):
    pass

  def guess_single_season(self):
    pass

  def guess_multiple_seasons(self):
    pass
