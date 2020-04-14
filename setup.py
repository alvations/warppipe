from distutils.core import setup
import setuptools

console_scripts = """
[console_scripts]
warppipe_one=warppipe.cli:cli_one
warppipe_two=warppipe.cli:cli_two
warppipe_threewarppipe.cli:cli_three
"""

setup(
  name = 'warppipe',
  packages = ['warppipe'],
  version = '0.0.3',
  description = '',
  long_description = '',
  author = '',
  license = '',
  url = 'https://github.com/alvations/warppipe',
  keywords = [],
  classifiers = [],
  install_requires = ['click', 'joblib', 'tqdm', 'sacremoses'],
  entry_points=console_scripts,
)
