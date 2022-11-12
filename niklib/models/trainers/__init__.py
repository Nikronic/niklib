"""Contains configs of training and scripts for it

Configs contain different setups for training that need to used by different
training scripts defined in this module. 
Also, for each different type of estimator or different purpose, a separate
training script needs to be defined.

Note that training scripts must be complete. I.e. they should be able to
checkpoint, load model, load data, etc.
"""

# flaml
from .aml_flaml import report_feature_importances
from .aml_flaml import sklearn_metric_loss_score
from .aml_flaml import report_loss_score
from .aml_flaml import get_loss_score
from .aml_flaml import log_mlflow_model
from .aml_flaml import AutoML
# helpers
import logging
import pathlib


# set logger
logger = logging.getLogger(__name__)


# path to all config/db files
parent_dir = pathlib.Path(__file__).parent
DATA_DIR = parent_dir / 'data'

# we have to import path to `/data` here to avoid circular import
EXAMPLE_FLAML_AUTOML_CONFIGS = DATA_DIR / 'example_flaml_automl_configs.json'
"""Configs for FLAML_ AutoML args and params as JSON

For more information:

    * about how to use it please see :class:`niklib.configs.core.JsonConfigHandler`.
    * about what fields are expected, see :class:`flaml.AutoML` respectively.


.. _FLAML: https://microsoft.github.io/FLAML/

"""