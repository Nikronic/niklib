# core
import json
# helper
from typing import Any, Union
from pathlib import Path


class JsonConfigHandler:
    """Initializes a class or method based on a predefined json config file

    In the highest level of configs, there are keys that contain the name of method
    or property of a ``Callable`` object. These needs to be passed to the :meth:`parse`
    method of the :class:`niklib.configs.core.JsonConfigHandler` class.

    Here is the convention of constructing json config file:
        - name the json file itself as whatever you wish. But better to be
        something that represents the class object you are trying to config.
        e.g. assume we have ``flaml_automl`` object hence we name the json file
        as ``example_flaml_automl_configs.json``.
        - in highest level, if args of a method need to be defined,
        use ``method_[name_of_the_method_of_your_class]``. e.g. let's say
        ``flaml_automl`` has ``fit`` method, then key in json would be
        named ``method_fit``.
        - values of each key are the arguments of that key. E.g. let's say
        ``method_fit`` has args ``task`` and ``max_iter``. Then the value
        for ``method_fit`` would be ``[YOUR_CLASS_NAME]_[ARG]: value``. E.g.
        ``FLAML_AUTOML_TASK: "classification"``` or ``FLAML_AUTOML_MAX_ITER: 100``.

    Here is a full example::

    ```json
    {
        "method_fit": {
            "FLAML_AUTOML_METRIC": "log_loss",
            "FLAML_AUTOML_TASK": "classification",
            "FLAML_AUTOML_MAX_ITER": 100,
            "FLAML_SPLIT_RATIO": 0.1,
            "FLAML_AUTOML_MEM_THRES": 19327352832,
            "FLAML_AUTOML_N_CONCURRENT_TRIALS": 1,
            "FLAML_AUTOML_AUTO_AUGMENT": false,
            "FLAML_AUTOML_EARLY_STOP": false,
            "FLAML_AUTOML_VERBOSE": 5
        }
    }

    ```

    After defining this file, you can added it as a constant to the root of 
    the package hosting the class for this config. E.g. this example was for
    ``flaml`` model which is in :mod:`niklib.models.trainers.aml_flaml`.
    So, you can fill :mod:`niklib.models.trainers.__init__` with a 
    constant to the path of this json. In the end, you can using this way:

        >>> from niklib.configs import JsonConfigHandler
        >>> from niklib.models.trainers.aml_flaml import AutoML
        >>> configs = JsonConfigHandler.parse(EXAMPLE_FLAML_AUTOML_CONFIGS, AutoML)
        >>> configs['method_fit']['task']
        classification
        >>> configs['method_fit']['max_iter']
        100

    Note:
        This class has hardcoded and customized definitions for different
        ``target`` values which can be found in the each packages ``data`` dir
        such as ``niklib.models.trainers.EXAMPLE_FLAML_AUTOML_CONFIGS``.
    """
    def __init__(self) -> None:
        return None

    @staticmethod
    def load(filename: str) -> Any:
        with open(filename, 'r') as f:
            configs = json.load(f)
        return configs

    def parse(self, filename: Union[Path, str], target: str) -> dict:
        """Takes a json file path and parse it for a particular class or method

        Note:
            See class description about valid json configs and the way
            they are constructed.

        Args:
            filename (Union[Path, str]): Path to JSON file
            target (str): Target class or method name to parse the configs for

        Raises:
            ValueError: If the target class or method is not supported or implemented

        Returns:
            dict:
                A dictionary containing the configs for each possible method or property
                of the target class or method.
        """
        # convert str path to Path
        if isinstance(filename, str):
            filename = Path(filename)
        self.conf_path = filename
        configs = self.load(filename)  # type: ignore
        self.configs = configs

        # parse configs for each target
        if target == 'LabelModel':
            # args of `fit` method of Snorkel LabelModel
            method_fit_configs = configs['method_fit']
            fit_args = {
                'n_epochs': method_fit_configs['LM_N_EPOCHS'],
                'lr': method_fit_configs['LM_LR'],
                'log_freq': method_fit_configs['LM_LOG_FREQ'],
                'optimizer': method_fit_configs['LM_OPTIM'],
            }

            # args of `__init__` method of LabelModel
            init_configs = configs['method_init']
            init_args: dict = {
                'cardinality': init_configs['LM_CARDINALITY'],
            }

            return {
                'method_fit': fit_args,
                'method_init': init_args,
            }
        elif target == 'FLAML_AutoML':
            # args of `fit` method of FLAML.AutoML
            method_fit_configs = configs['method_fit']
            fit_args = {
                'task': method_fit_configs['FLAML_AUTOML_TASK'],
                'metric': method_fit_configs['FLAML_AUTOML_METRIC'],
                'max_iter': method_fit_configs['FLAML_AUTOML_MAX_ITER'],
                'split_ratio': method_fit_configs['FLAML_SPLIT_RATIO'],
                'mem_thres': method_fit_configs['FLAML_AUTOML_MEM_THRES'],
                'n_concurrent_trials': method_fit_configs['FLAML_AUTOML_N_CONCURRENT_TRIALS'],
                'auto_augment': method_fit_configs['FLAML_AUTOML_AUTO_AUGMENT'],
                'early_stop': method_fit_configs['FLAML_AUTOML_EARLY_STOP'],
                'verbose': method_fit_configs['FLAML_AUTOML_VERBOSE'],
            }

            return {
                'method_fit': fit_args,
            }
        else:
            raise ValueError(f'{target} is not implemented or not supported.')

    def as_mlflow_artifact(self, target_path: Union[Path, str]) -> None:
        """Saves the configs to the MLFlow artifact directory

        Args:
            target_path: Path to the MLFlow artifact directory. The name of the file
                will be same as original config file, hence, only provide path to dir.
        """

        # convert str path to Path
        if isinstance(target_path, str):
            target_path = Path(target_path)

        if self.conf_path is None:
            raise ValueError(
                'Configs have not been set yet. Use `.parse` to set them.'
            )

        # save the configs to the artifact directory
        target_path = target_path / self.conf_path.name
        with open(target_path, 'w') as f:
            json.dump(self.configs, f)
