# core
from dateutil.relativedelta import *
import pikepdf
# helpers
from typing import Any
import shutil
import logging


# logging
logger = logging.getLogger(__name__)


class FileTransform:
    """A base class for applying transforms as a composable object over files.

    Any behavior over the files itself (not the content of files)
    must extend this class.

    """

    def __init__(self) -> None:
        pass

    def __call__(self, src: str, dst: str, *args: Any, **kwds: Any) -> Any:
        """

        Args:
            src: source file to be processed
            dst: the pass that the processed file to be saved 
        """
        pass


class CopyFile(FileTransform):
    """Only copies a file, a wrapper around ``shutil`` 's copying methods

    Default is set to ``'cf'``, i.e. :func:`shutil.copyfile`. For more info see
    shutil_ documentation.


    Reference:
        1. https://stackoverflow.com/a/30359308/18971263
    """

    def __init__(self, mode: str) -> None:
        super().__init__()

        self.COPY_MODES = ['c', 'cf', 'c2']
        self.mode = mode if mode is not None else 'cf'
        self.__check_mode(mode=mode)

    def __call__(self, src: str, dst: str,  *args: Any, **kwds: Any) -> Any:
        if self.mode == 'c':
            shutil.copy(src=src, dst=dst)
        elif self.mode == 'cf':
            shutil.copyfile(src=src, dst=dst)
        elif self.mode == 'c2':
            shutil.copy2(src=src, dst=dst)

    def __check_mode(self, mode: str):
        """Checks copying mode to be available in shutil_

        Args:
            mode: copying mode in ``shutil``, one of ``'c'``, ``'cf'``, ``'c2'``

        .. _shutil: https://docs.python.org/3/library/shutil.html
        """
        if not mode in self.COPY_MODES:
            raise ValueError(
                f'Mode {mode} does not exist,',
                 ' choose one of "{self.COPY_MODES}".'
            )


class MakeContentCopyProtectedMachineReadable(FileTransform):
    """Reads a ``'content-copy'`` protected PDF and removes this restriction

    Removing the protection is done by saving a "printed" version of via pikepdf_

    References:
        1. https://www.reddit.com/r/Python/comments/t32z2o/simple_code_to_unlock_all_readonly_pdfs_in/
        2. https://pikepdf.readthedocs.io/en/latest/

    .. _pikepdf: https://pikepdf.readthedocs.io/en/latest/
    """

    def __init__(self) -> None:
        super().__init__()

    def __call__(self, src: str, dst: str, *args: Any, **kwds: Any) -> Any:
        """

        Args:
            src (str): source file to be processed
            dst (str): destination to save the processed file

        Returns:
            Any: None
        """
        pdf = pikepdf.open(src, allow_overwriting_input=True)
        pdf.save(dst)


class FileTransformCompose:
    """Composes several transforms operating on files together

    The transforms should be tied to files with keyword and this will be only applying
    functions on files that match the keyword using a dictionary

    Transformation dictionary over files in the following structure::

        {
            FileTransform: 'filter_str', 
            ...,
        }

    Note:
        Transforms will be applied in order of the keys in the dictionary
    """

    def __init__(self, transforms: dict) -> None:
        """

        Args:
            transforms: a dictionary of transforms, where the key is the instance of 
                FileTransform and the value is the keyword that the transform will be
                applied to

        Raises:
            ValueError: if the keyword is not a string
        """
        if transforms is not None:
            for k in transforms.keys():
                if not issubclass(k.__class__, FileTransform):
                    raise TypeError(f'Keys must be {FileTransform} instance.')

        self.transforms = transforms

    def __call__(self, src: str, dst: str, *args: Any, **kwds: Any) -> Any:
        """Applies transforms in order

        Args:
            src (str): source file path to be processed
            dst (str): destination to save the processed file
        """
        for transform, file_filter in self.transforms.items():
            if file_filter in src:
                transform(src, dst)
