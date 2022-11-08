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

    def _setup_mlflow_artifacts_dirs(self, base_path: Union[str, Path]) -> None:
        """Builds the directories for saving images, logs, and configs as mlflow artifacts

        Following type of artifacts are predefined and each will be considered as a
        subdirectory of ``base_path``:

            - images: ``images``
            - logging prints: ``logs``
            - configs of classes, setting, etc as json files: ``configs``
            - model weights or objects: ``models``
            - ``MLflow`` flavor-specific tracked model: ``MLmodel`` 

        Note:
            If you are using this class for just flagging the data,
            you can simply send numerical values (``1/*``, ``2/*``)
        
        Todo:
            Make generation of the directories and their constant attributes (self.*)
            automatic given a list of names rather than this hardcoded pepega mode.

        Args:
            base_path (Union[str, :class:`pathlib.Path`]): Base path for artifacts. 
        """
        base_path = self.__str_to_path(string=base_path)
        base_path = self.mlflow_artifacts_base_path / base_path
        MLFLOW_ARTIFACTS_LOGS_PATH = base_path / 'logs'
        MLFLOW_ARTIFACTS_CONFIGS_PATH = base_path / 'configs'
        MLFLOW_ARTIFACTS_IMAGES_PATH = base_path / 'images'
        MLFLOW_ARTIFACTS_MODELS_PATH = base_path / 'models'
        MLFLOW_ARTIFACTS_MLMODELS_PATH = base_path / 'MLmodel'
        if not base_path.exists():
            base_path.mkdir(parents=True)
            MLFLOW_ARTIFACTS_LOGS_PATH.mkdir(parents=True)
            MLFLOW_ARTIFACTS_CONFIGS_PATH.mkdir(parents=True)
            MLFLOW_ARTIFACTS_IMAGES_PATH.mkdir(parents=True)
            MLFLOW_ARTIFACTS_MODELS_PATH.mkdir(parents=True)
            MLFLOW_ARTIFACTS_MLMODELS_PATH.mkdir(parents=True)

        self.MLFLOW_ARTIFACTS_LOGS_PATH = MLFLOW_ARTIFACTS_LOGS_PATH
        self.MLFLOW_ARTIFACTS_CONFIGS_PATH = MLFLOW_ARTIFACTS_CONFIGS_PATH
        self.MLFLOW_ARTIFACTS_IMAGES_PATH = MLFLOW_ARTIFACTS_IMAGES_PATH
        self.MLFLOW_ARTIFACTS_MODELS_PATH = MLFLOW_ARTIFACTS_MODELS_PATH
        self.MLFLOW_ARTIFACTS_MLMODELS_PATH = MLFLOW_ARTIFACTS_MLMODELS_PATH

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
