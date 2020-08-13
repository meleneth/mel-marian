import os
import os.path

import flexmock
from bs4 import BeautifulSoup

from mel.marian.episodeguiderename.commandline import get_parser
from mel.marian.episodeguiderename.commandline import entry_default
from mel.marian.episodeguiderename.commandline import entry_edit

def test_argparser_handles_basic_case():
  parser = get_parser()
  args = parser.parse_args([])
  assert args.func == entry_default

def test_argparser_handles_edit():
  parser = get_parser()
  args = parser.parse_args(['edit'])
  assert args.func == entry_edit
