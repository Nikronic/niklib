__all__ = [
    'Logger'
]

# core
import logging
# helpers
from typing import List, Optional, Union
from enum import IntEnum
from pathlib import Path
import sys


class LoggingLevels(IntEnum):
    """Logging levels from ``logging``

    Just a clone of ``logging`` **levels** for our internal use, do not expose to user. 
    """

    CRITICAL = 50
    FATAL = CRITICAL
    ERROR = 40
    WARNING = 30
    WARN = WARNING
    INFO = 20
    DEBUG = 10
    NOTSET = 0


class Logger(logging.Logger):
    def __init__(
        self,
        name: str,
        level: Union[LoggingLevels, int],
        mlflow_artifacts_base_path: Union[Path, str],
        libs: Optional[List[str]] = None
    ) -> None:
        super().__init__(name, level)

        self.__mlflow_artifacts_base_path = mlflow_artifacts_base_path
        self.__create_artifacts_dir(self.mlflow_artifacts_base_path)
        self.logger_formatter = logging.Formatter(
            "[%(name)s: %(asctime)s] {%(lineno)d} %(levelname)s - %(message)s", "%m-%d %H:%M:%S"
        )

        # config system standard in/out to redirect to logger
        stdout_stream_handler = logging.StreamHandler(stream=sys.stdout)
        stderr_stream_handler = logging.StreamHandler(stream=sys.stderr)
        stdout_stream_handler.setFormatter(self.logger_formatter)
        stderr_stream_handler.setFormatter(self.logger_formatter)
        self.addHandler(stdout_stream_handler)
        self.addHandler(stderr_stream_handler)

        # a counter as a naming method for new artifacts
        self._artifact_name: int = 0

        # set libs to log to our logging config
        self.libs_logger: List[logging.Logger] = []
        if libs is not None:
            for __l in libs:
                __libs_logger = logging.getLogger(__l)
                __libs_logger.setLevel(level)
                __libs_logger.addHandler(stdout_stream_handler)
                __libs_logger.addHandler(stderr_stream_handler)
                self.libs_logger.append(__libs_logger)

        # hold `*.log` handlers so we can delete it on each new artifact creation
        self.__prev_handler: Optional[logging.Handler] = None

    @property
    def mlflow_artifacts_base_path(self) -> Path:
        self.__mlflow_artifacts_base_path = self.__str_to_path(
            self.__mlflow_artifacts_base_path
        )
        return self.__mlflow_artifacts_base_path

    def __create_artifacts_dir(self, path: Path) -> None:
        """Creates an empty dir at ``path``

        Args:
            path (:class:`pathlib.Path`): Path to create dir as base artifacts for mlflow
        """
        path.mkdir()

    def __str_to_path(self, string: Union[str, Path]) -> Path:
        """Converts a string of path to :class:`pathlib.Path`

        Args:
            string (Union[str, `pathlib.Path`]): path string or object to convert

        Returns:
            :class:`pathlib.Path`: ``Path`` instance of given path string 
        """
        if isinstance(string, str):
            return Path(string)
        return string

    def _setup_mlflow_artifacts_dirs(
        self,
        base_path: Union[str, Path],
        subdirs: Optional[List[str]] = None
        ) -> None:
        """Builds the directories for saving images, logs, and configs as mlflow artifacts
        
        Note:
            If you are using this class for just flagging the data,
            you can simply send numerical values (``1/*``, ``2/*``)
        
        Args:
            base_path (Union[str, :class:`pathlib.Path`]): Base path for artifacts.
            subdirs (List[str], optional): A list of names of directories that will be 
                subdirectories of ``base_path`` for separating different artifacts. 
                These subdirs are available as properties that start with
                ``MLFLOW_ARTIFACTS_SUBDIRS[x]_PATH``.
                Following type of artifacts are predefined and each will be considered as a
                subdirectory of ``base_path`` if ``None`` is provided:

                    - images: ``images``
                    - logging prints: ``logs``
                    - configs of classes, setting, etc as json files: ``configs``
                    - model weights or objects: ``models``
                    - ``mlflow`` flavor-specific tracked model: ``MLmodel`` 
                
                Please use names that only contain characters, numbers and dash/underline.
        """

        # construct subdir names
        if subdirs is None:
            subdirs = ['logs', 'configs', 'images', 'models', 'MLmodel']
        
        # construct base dir path
        base_path = self.__str_to_path(string=base_path)
        base_path = self.mlflow_artifacts_base_path / base_path
        if not base_path.exists():
            base_path.mkdir(parents=True)

        # construct subdirs' path
        for subdir in subdirs:
            subdir_path: Path = base_path / subdir
            if not subdir_path.exists():
                subdir_path.mkdir(parents=True)

                # dynamically create properties
                #   with names `MLFLOW_ARTIFACTS_[_subdir]_PATH` (all upper)
                setattr(
                    self,
                    f'MLFLOW_ARTIFACTS_{str.upper(subdir)}_PATH',
                    subdir_path
                )

    def _remove_previous_handlers(self) -> None:
        """This is used to remove file related handlers on each new run of :meth:`create_artifact_instance`

        Note:
            Do not forget to remove file handler from all libs, here, :attr:`libs_logger`.
        """
        if self.__prev_handler is not None:
            self.removeHandler(self.__prev_handler)
            for lib_log in self.libs_logger:
                lib_log.removeHandler(self.__prev_handler)

    def create_artifact_instance(
        self,
        artifact_name: str = None
    ):
        """Creates an entire artifact (mlflow) directory each time it is called

        This is used to create artifacts sub directories that each include
        sub directories such as ``images``, ``configs``, and so on (see
        :meth:`_setup_mlflow_artifacts_dirs` for more info) that each will
        include the artifacts of that type.

        Args:
            artifact_name (str): a directory name. Please refrain 
                from providing full path and only give a directory name. It is expected 
                that you pass the path as :attr:`mlflow_artifacts_base_path` which makes  
                ``artifact_name`` as its sub directory. If None, we use an internal
                counter and use natural numbers increasing each time this method is called.
        """
        # if prev handler exits, remove it
        self._remove_previous_handlers()

        # check if artifact_name is provided, if not, count calls to this method
        if artifact_name is None:
            artifact_name = f'{self._artifact_name}'
            self._artifact_name += 1

        # create new artifacts directory
        self._setup_mlflow_artifacts_dirs(base_path=artifact_name)

        # setup main logger
        logger_handler = logging.FileHandler(
            filename=self.MLFLOW_ARTIFACTS_LOGS_PATH / f'{artifact_name}.log',
            mode='w'
        )
        logger_handler.setFormatter(self.logger_formatter)
        self.addHandler(logger_handler)
        # redirect libs main logger to our main
        for lib_log in self.libs_logger:
            lib_log.addHandler(logger_handler)

        # keep last handler so we can remove it on next call
        self.__prev_handler = logger_handler

kek = Logger('kek', 10, 'kek')
kek.create_artifact_instance('lel')
