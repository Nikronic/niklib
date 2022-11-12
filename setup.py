from setuptools import find_packages
from setuptools import setup
from pathlib import Path
from typing import Dict


this_directory = Path(__file__).parent
long_description = (this_directory / 'README.md').read_text()

LIB_NAME = 'niklib'

# version.py defines the VERSION and VERSION_SHORT variables.
# We use exec here so we don't import snorkel.
VERSION: Dict[str, str] = {}
with open(f'{LIB_NAME}/version.py', 'r') as version_file:
    exec(version_file.read(), VERSION)

setup(
  name=LIB_NAME,
  version=VERSION['VERSION'],
  packages=find_packages(),
  description='niklib: Copypasta of Nikronic!',
  author='Nikan Doosti',
  author_email='nikan.doosti@outlook.com',
  long_description=long_description,
  long_description_content_type='text/markdown',
  include_package_data = True,
  # ref https://stackoverflow.com/a/73649552/18971263
  package_data={
        'niklib.configs': ['**/*.csv', '**/*.json'],
        'niklib.models.preprocessors': ['**/*.json'],
        'niklib.models.trainers': ['**/*.json'],
      }
)
