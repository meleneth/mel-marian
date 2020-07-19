import re
import logging
import time
import json

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
