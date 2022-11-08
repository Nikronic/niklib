from .core import JsonConfigHandler

# ref: https://stackoverflow.com/a/50797410/18971263
import pathlib


# path to all config/db files
parent_dir = pathlib.Path(__file__).parent
DATA_DIR = parent_dir / 'data'


SAMPLE = DATA_DIR / 'sample.csv'
"""Some sample data for demo

Note:
    The data has been obtained from http://example.com
"""
