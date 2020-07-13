from setuptools import setup, find_packages

setup(name='mel-marian',
  version='0.0.1dev',
  description='Utilities to help rename media files according to their tv.com entries',
  author='Meleneth',
  author_email='meleneth@gmail.com',
  license='GPL',
  packages=find_packages('src'),
  package_dir={'': 'src'},
  install_requires=['requests', 'beautifulsoup4', 'PyInquirer', 'tabulate'],
  tests_require=['pytest', 'pytest-cov'],
  entry_points = {
    'console_scripts': [
      'fetch-episode-guide=mel.marian.fetchepisodeguide.commandline:main',
      'episode-guide-rename=mel.marian.episodeguiderename.commandline:main'
    ]
  },
  zip_safe=False
)
