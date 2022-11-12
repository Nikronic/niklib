"""Contains configs of evaluation, metrics and scripts for it

Configs are the same as in :mod:`niklib.models.trainers <niklib.models.trainers>`
but for purpose of evaluation.
Also, there are some scripts to evaluate the models similar to what is used in 
:mod:`niklib.models.trainers <niklib.models.trainers>` for training.

Submodules:

    * :mod:`niklib.models.evaluators.metrics <niklib.models.evaluators.metrics>`: contains all the metrics for evaluation

"""


# helpers
import logging


# set logger
logger = logging.getLogger(__name__)
