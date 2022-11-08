"""
Contains implementation of functions that could be used for processing data everywhere and
are not necessarily bounded to a class.

"""

# core
import pandas as pd
import xmltodict
import csv
# ours: data
from niklib.data.preprocessor import FileTransformCompose
# helpers
from typing import Callable, Optional, Union, cast
from enlighten import Manager
from fnmatch import fnmatch
import enlighten
import logging
import sys
import os


# set logger
logger = logging.getLogger(__name__)


def dict_to_csv(d: dict, path: str) -> None:
    """Takes a flattened dictionary and writes it to a CSV file.

    Args:
        d (dict): A dictionary
        path (str): Path to the output file (will be created if not exist)
    """

    with open(path, 'w') as f:
        w = csv.DictWriter(f, d.keys())
        w.writeheader()
        w.writerow(d)


def dump_directory_structure_csv(
    src: str,
    shallow: bool = True
) -> None:
    """Saves a tree structure of a directory in csv file

    Takes a ``src`` directory path, creates a tree of dir structure and writes
    it down to a csv file with name ``'label.csv'`` with
    default value of ``'0'`` for each path

    Note:
        This has been used to manually extract and record labels.

    Args:
        src (str): Source directory path
        shallow (bool, optional): If only dive one level of depth (False: recursive).
            Defaults to True.
    """

    dic = create_directory_structure_tree(src=src, shallow=shallow)
    flat_dic = flatten_dict(dic)
    flat_dic = {k: v for k, v in flat_dic.items() if v is not None}
    dict_to_csv(d=flat_dic, path=src+'/label.csv')


def create_directory_structure_tree(src: str, shallow: bool = False) -> dict:
    """Takes a path to directory and creates a dictionary of its directory structure tree

    Args:
        src (str): Path to source directory
        shallow (bool, optional): Whether or not just dive to root dir's subdir.
            Defaults to False.

    Reference:
        1. https://stackoverflow.com/a/25226267/18971263

    Returns:
        dict:
            Dictionary of all dirs (and subdirs) where keys are path
            and values are ``0``
    """
    d = {'name': os.path.basename(src) if os.path.isdir(
        src) else None}  # ignore files, only dir
    if os.path.isdir(src):
        if shallow:
            d['children'] = [{x: '0'} for x in os.listdir(src)]  # type: ignore
        else:  # recursively walk into all dirs and subdirs
            d['children'] = [create_directory_structure_tree(  # type: ignore
                os.path.join(src, x)) for x in os.listdir(src)]
    else:
        pass
        # d['type'] = "file"
    return d


def flatten_dict(d: dict) -> dict:
    """Takes a (nested) multilevel dictionary and flattens it

    Args:
        d (dict): A dictionary (could be multilevel)

    Reference:
        1. https://stackoverflow.com/a/67744709/18971263

    Returns:
        dict:
            Flattened dictionary where keys and values of returned dict are:
                - ``new_keys[i] = f'{old_leys[level]}.{old_leys[level+1]}.[...].{old_leys[level+n]}'``
                - ``new_value = old_value``

    """

    def items():
        if isinstance(d, dict):
            for key, value in d.items():
                # nested subtree
                if isinstance(value, dict):
                    for subkey, subvalue in flatten_dict(value).items():
                        yield '{}.{}'.format(key, subkey), subvalue
                # nested list
                elif isinstance(value, list):
                    for num, elem in enumerate(value):
                        for subkey, subvalue in flatten_dict(elem).items():
                            yield '{}.[{}].{}'.format(key, num, subkey), subvalue
                # everything else (only leafs should remain)
                else:
                    yield key, value
    return dict(items())


def xml_to_flattened_dict(xml: str) -> dict:
    """Takes a (nested) XML and flattens it to a dict via :func:`flatten_dict`

    Args:
        xml (str): A XML string

    Returns:
        dict: A flattened dictionary of given XML
    """
    flattened_dict = xmltodict.parse(xml)  # XML to dict
    flattened_dict = flatten_dict(flattened_dict)
    return flattened_dict


def process_directory(
    src_dir: str,
    dst_dir: str,
    compose: FileTransformCompose,
    file_pattern: str = '*',
    manager: Optional[Manager] = None
) -> None:
    """Transforms all files that match pattern in given dir and saves new files preserving dir structure

    Note:
        A methods used for handling files from manually processed dataset to raw-dataset
        see :class:`FileTransform <niklib.data.preprocessor.FileTransform>` for more information.

    References:
        1. https://stackoverflow.com/a/24041933/18971263

    Args:
        src_dir (str): Source directory to be processed
        dst_dir (str): Destination directory to write processed files
        compose (FileTransformCompose): An instance of transform composer.
            see :class:`niklib.data.preprocessor.FileTransformCompose`.
        file_pattern (str, optional): pattern to match files, default to ``'*'`` for
            all files. Defaults to ``'*'``.
        manager (Optional[Manager], optional): ``enlighten.Manager`` for progressbar.
            Defaults to None.
    """

    assert src_dir != dst_dir, 'Source and destination dir must differ.'
    if src_dir[-1] != '/':
        src_dir += '/'

    # logging
    manager = enlighten.get_manager(sys.stderr) if manager is None else manager
    progress_bar = manager.counter(
        total=len(next(os.walk(src_dir), (None, [], None))[1]),
        desc='Extracted',
        unit='data point files'
    )
    i = 0

    # process directories
    for dirpath, _, all_filenames in os.walk(src_dir):
        # filter out files that match pattern only
        filenames = filter(lambda fname: fnmatch(
            fname, file_pattern), all_filenames)
        dirname = dirpath[len(dirpath) - dirpath[::-1].find('/'):]
        logger.info(f'Processing directory="{dirname}"...')
        if filenames:
            dir_ = os.path.join(dst_dir, dirpath.replace(src_dir, ''))
            os.makedirs(dir_, exist_ok=True)
            for fname in filenames:
                in_fname = os.path.join(dirpath, fname)  # original path
                out_fname = os.path.join(dir_, fname)  # processed path
                compose(in_fname, out_fname)  # composition of transforms
                logger.info(f'Processed file="{fname}"')
        logger.info(f'Processed "{i}th" data entry.')
        i += 1
        progress_bar.update()


def extended_dict_get(
    string: str,
    dic: dict,
    if_nan: str,
    condition: Union[Callable, bool, None] = None
):
    """Takes a string and looks for it inside a dictionary with default value if condition is satisfied

    Args:
        string (str): the ``string`` to look for inside dictionary ``dic``
        dic (dict): the dictionary that ``string`` is expected to be
        if_nan (str): the value returned if ``string`` could not be found in ``dic``
        condition (Optional[bool], optional): look for ``string`` in ``dic`` only
            if ``condition`` is True 

    Examples:
        >>> d = {'1': 'a', '2': 'b', '3': 'c'}
        >>> extended_dict_get('1', d, 'z', str.isnumeric)
        'a'
        >>> extended_dict_get('x', d, 'z', str.isnumeric)
        'x'

    Returns:
        Any: Substituted value instead of `string`
    """

    condition = (lambda x: True) if condition is None else condition
    condition = cast(Callable, condition)

    # check given `condition` is true or not
    if condition(string):
        return dic.get(string, if_nan)  # look for `string` if not use `if_nan`
    else:
        logger.debug(
            f'"{string}" is not True for the given `condition`'
             ' ==> `false_condition_value` will be applied.')
        return string


def config_csv_to_dict(path: str) -> dict:
    """Takes a config CSV and return a dictionary of key and values

    Note:
        Configs of our use case can be found in :mod:`niklib.configs`

    Args:
        path (str): string path to config file

    Returns:
        dict: A dictionary of converted csv
    """

    config_df = pd.read_csv(path)
    return dict(zip(config_df[config_df.columns[0]], config_df[config_df.columns[1]]))

