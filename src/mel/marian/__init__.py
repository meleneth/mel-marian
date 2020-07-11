import requests
from bs4 import BeautifulSoup

import logging

class IMDBLookupFailureException(Exception):
  pass

class GuideFetcher(object):
  def __init__(self, name):
    self.name = name
    self.episodes = []

  def find_guide(self):
    logger = logging.getLogger()

    url = "http://www.tv.com/search?q=" % (self.name.replace(" ", "%20"))
    logger.info(url)
    page = requests.get(url)
    soup = BeautifulSoup(page.text, 'html.parser')
    links = list(filter(lambda x: x.content.search("Episode Guide"), soup.find_all('a')))

    base_url = "http://www.tv.com"

    episode_guide_url = links[0]["href"]

    logger.info("Found guide: #{episode_guide_url}")

  def parse_season(self, season_html):
    soup = BeautifulSoup(season_html, 'html.parser')
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

      self.episodes.append(info)

class EpisodeRenamer(object):
  pass

class MediaSeries(object):
  pass

class Season(object):
  pass

class Episode(object):
  pass

class MediaFile(object):
  pass
