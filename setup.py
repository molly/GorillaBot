from distutils.core import setup
setup(
  name = 'gorillabot',
  packages = ['gorillabot'],
  package_data = {'gorillabot': ['plugins/*.py']},
  scripts = ['gorillabot/docs/make_docs.py'],
  version = '2.0',
  description = 'An easily-extensible IRC bot.',
  license = 'MIT',
  author = 'Molly White',
  author_email = 'molly.white5@gmail.com',
  url = 'https://github.com/molly/GorillaBot',
  download_url = 'https://github.com/molly/gorillabot/tarball/2.0',
  keywords = ['irc', 'bot', 'freenode'],
  classifiers = [],
  install_requires = ['beautifulsoup4'],
)