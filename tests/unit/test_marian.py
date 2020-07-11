import flexmock
import os
import os.path

import mel.marian
from mel.marian import IMDBLookupFailureException
from mel.marian import GuideFetcher
from mel.marian import EpisodeRenamer
from mel.marian import MediaSeries
from mel.marian import Season
from mel.marian import Episode
from mel.marian import MediaFile

def test_throws_IMDBLookupFailureException():
  pass

def test_GuideFetcher_parse_season():
  test_dir = os.path.dirname(os.path.abspath(__file__))
  with open(os.path.join(test_dir, "example_season.html")) as f:
    test_html = f.read()
  guide = GuideFetcher("Boston Legal")
  guide.parse_season(test_html)
  episode = guide.episodes[0]
  print("Final Verdict:")
  print(episode)
  assert "Last Call" == episode["name"]
  assert 13 == episode["episode_no"]
  assert """To make sure that Alan receives all his money when he dies, Denny marries Alan in a double wedding with Carl and Shirley.""" == episode["description"]
  assert "12/8/08" == episode["air_date"]
  assert "Boston Legal" == episode["show_name"]
  assert 5 == episode["season_no"]

def test_EpisodeRenamer():
  pass

def test_MediaSeries():
  pass

def test_Season():
  pass

def test_Episode():
  pass

def test_MediaFile():
  pass
