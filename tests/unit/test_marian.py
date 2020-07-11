import os
import os.path

import flexmock
from bs4 import BeautifulSoup

import mel.marian
from mel.marian import GuideFetcher

def test_GuideFetcher_parse_search_result():
  test_dir = os.path.dirname(os.path.abspath(__file__))
  with open(os.path.join(test_dir, "example_search_result.html")) as f:
    test_html = f.read()
  guide = GuideFetcher()
  url = guide.parse_search_result(BeautifulSoup(test_html, 'html.parser'))
  assert "/shows/serial-experiments-lain/episodes/" == url

def test_GuideFetcher_parse_series():
  test_dir = os.path.dirname(os.path.abspath(__file__))
  with open(os.path.join(test_dir, "example_series.html")) as f:
    test_html = f.read()
  guide = GuideFetcher()
  results = guide.parse_series(BeautifulSoup(test_html, 'html.parser'), "/shows/farscape/episodes/")
  assert ['/shows/farscape/season-5/',
    '/shows/farscape/season-4/',
    '/shows/farscape/season-3/',
    '/shows/farscape/season-2/',
    '/shows/farscape/season-1/'
  ] == results

def test_GuideFetcher_parse_season():
  test_dir = os.path.dirname(os.path.abspath(__file__))
  with open(os.path.join(test_dir, "example_season.html")) as f:
    test_html = f.read()
  guide = GuideFetcher()
  guide.parse_season(BeautifulSoup(test_html, 'html.parser'))
  episode = guide.episodes[0]

  assert "Last Call" == episode["name"]
  assert 13 == episode["episode_no"]
  assert """To make sure that Alan receives all his money when he dies, Denny marries Alan in a double wedding with Carl and Shirley.""" == episode["description"]
  assert "12/8/08" == episode["air_date"]
  assert "Boston Legal" == episode["show_name"]
  assert 5 == episode["season_no"]
