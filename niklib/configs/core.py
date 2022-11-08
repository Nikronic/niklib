# core
import json
# helper
from typing import Any, Union
from pathlib import Path


class JsonConfigHandler:
    def __init__(self) -> None:
        return None

    @staticmethod
    def load(filename: str) -> Any:
        with open(filename, 'r') as f:
            configs = json.load(f)
        return configs

    def parse(self, filename: Union[Path, str], target: str) -> dict:
        """Takes a json file path and parse it for a particular class or method

        In the highest level of configs, there are keys that contain the name of method
        or property of a `Callable` object. These needs to be passed to the :meth:`parse`
        method of the :class:`niklib.configs.core.JsonConfigHandler` class.

            >>> from niklib.configs import JsonConfigHandler
            >>> from niklib.labeling.model import LabelModel
            >>> configs = JsonConfigHandler.parse(LABEL_MODEL_CONFIGS, LabelModel)
            >>> configs['method_fit']['n_epochs']
            100
            >>> configs['method_init']['cardinality']
            2

        Note:
            This method has hardcoded and customized definitions for different
            ``target`` values which can be found in the ``niklib.configs`` constant
            variables such as ``niklib.configs.LABEL_MODEL_CONFIGS``.

        Args:
            filename (Union[Path, str]): Path to JSON file
            target (str): Target class or method name to parse the configs for

        Raises:
            ValueError: If the target class or method is not supported or implemented

        Returns:
            dict: A dictionary containing the configs for each possible method or property
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
