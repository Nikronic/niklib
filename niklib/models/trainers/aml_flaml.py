# core
from xgboost import XGBClassifier
from lightgbm import LGBMClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import (
    DecisionTreeClassifier,
    ExtraTreeClassifier
)
from catboost import CatBoostClassifier
import numpy as np
import flaml
from flaml import AutoML
from flaml.ml import sklearn_metric_loss_score
# devops
import mlflow
# helpers
from typing import Any, Dict, List, Optional, Union, Callable
from pathlib import Path
import logging


# configure logging
logger = logging.getLogger(__name__)


def get_loss_score(
    y_predict: np.ndarray,
    y_true: np.ndarray,
    metrics: Union[List[str], str, Callable]
) -> Dict[str, Any]:
    """Gives loss score given predicted and true labels and metrics

    Args:
        y_predict (np.ndarray): Predicted labels, same shape as ``y_true``
        y_true (np.ndarray): Ground truth labels, same shape as ``y_predict``
        metrics (Union[List[str], str, callable]): ``metrics`` can be either
            a metric name (``str``) or a list of metric names that is supported
            by ``flaml.ml.sklearn_metric_loss_score``.

            ``metrics`` can also be a custom metric which in that case must be class
            that implements ``__call__`` method with following signature:::

                def __call__(
                    X_test, y_test, estimator, labels,
                    X_train, y_train, weight_test=None, weight_train=None,
                    config=None, groups_test=None, groups_train=None,
                ):
                    return metric_to_minimize, metrics_to_log

    Returns:
        Dict[str, Any]:
        Dictionary of ``{'metric_name': metric_value}`` for all given
        ``metrics``.

    See Also:
        * :func:`report_loss_score`
    """
    # name of metrics for logging purposes
    metrics_names: List[str] = []
    # actual metrics param for APIs that need name of metrics e.g. sklearn
    metrics_values = []

    # if `metrics` is one of flaml's metrics
    if isinstance(metrics, str):
        metrics_names = [metrics]
        metrics_values = sklearn_metric_loss_score(
            metric_name=metrics,
            y_predict=y_predict,
            y_true=y_true
        )
    # if `metrics` is a list of metrics of flaml's metrics
    elif isinstance(metrics, list):
        metrics_names = metrics
        metrics_values = [
            sklearn_metric_loss_score(
                metric_name=metric,
                y_predict=y_predict,
                y_true=y_true) for metric in metrics
        ]
    # if `metrics` is a class
    # TODO: fix complaining that mypy does not understand Callable (herald :D)
    elif isinstance(metrics, Callable):  # type: ignore
        metrics = metrics()
        metrics_names = [f'custom_{metrics.__class__.__name__}']
        metrics_values = [
            metrics(y_predict=y_predict, y_true=y_true)  # type: ignore
        ]

    # return dictionary of metrics values and their names
    metrics_name_value: dict = {}
    for metric_name, metric_value in zip(metrics_names, metrics_values):
        metrics_name_value[metric_name] = metric_value
    return metrics_name_value


def report_loss_score(metrics: Dict[str, Any]) -> str:
    """Prints a dictionary of ``{'metric_name': metric_value}``

    Such a dictionary can be produced via :func:`get_loss_score`.

    Args:
        metrics (Dict[str, Any]): Dictionary of ``{'metric_name': metric_value}``

    Returns: 
        str: 
        A string containing the loss score and their corresponding names
        in a new line. e.g.::

            'accuracy: 0.97'
            'f1: 0.94'

    """
    msg: str = ''
    for metric_name, metric_value in metrics.items():
        if is_score_or_loss(metric_name):
            msg += f'{metric_name} score: {1 - metric_value:.2f}\n'
        else:
            msg += f'{metric_name} loss: {metric_value:.2f}\n'
    return msg


def is_score_or_loss(metric: str) -> bool:
    """Check if metric is a score or loss

    If metric is a loss (the lower the better), then the value itself
    will be reported. If metric is a score (the higher the better), then
    the ``1 - value`` will be reported.

    The reason is that ``flaml`` uses ``1 - value`` to minimize the error
    when users' chosen ``metric`` is a **score** rather than a **loss**.

    Args:
        metric (str): metric name that is supported by ``flaml``. For 
            more info see :func:`flaml.ml.sklearn_metric_loss_score`.

    See Also:
        * :func:`report_loss_score`

    Returns:
        bool: If is a score then return ``True``, otherwise return ``False``
    """
    # determine if it is 'score' (maximization) or 'loss' (minimization)
    result = False
    if metric in [
        'r2',
        'accuracy',
        'roc_auc',
        'roc_auc_ovr',
        'roc_auc_ovo',
        'f1',
        'ap',
        'micro_f1',
        'macro_f1',
    ]:
        result = True
    return result


def report_feature_importances(
    estimator: Any,
    feature_names: List[str]
) -> str:
    """Prints feature importances of an fitted ``flaml.AutoML`` instance

    Args:
        estimator (Any): :class:`flaml.AutoML` underlying estimator that has ``feature_importances_``
            attribute, i.e. pass ``estimator`` in ``flaml_obj.model.estimator.feature_importances_``. 
        feature_names (List[str]): List of feature names. One can pass
            columns of original dataframe as ``feature_names``

    Returns:
        str: A string containing the feature importances in a new line. e.g.::

            'feature_1: 0.1'
            'feature_2: 0.0'
            'feature_2: 0.4'
            ...

    """
    msg: str = ''
    feature_importance = estimator.feature_importances_
    for feature_name, feature_importance in zip(feature_names,
                                                feature_importance):
        msg += f'{feature_name}: {feature_importance:.2f}\n'
    return msg


def find_estimator(flaml_automl: flaml.AutoML):
    """Finds underlying fitted estimator from given ``flaml`` model

    Args:
        flaml_automl (flaml.AutoML): An already fitted :class:`flaml.AutoML` instance

    Raises:
        NotImplementedError:
            If ``flaml_automl`` 's underlying ``model.estimator``
            is not implemented yet

    Returns:
        Any:
            The underlying estimator itself or a component of it that 
            quacks like sklearn estimators
    """
    # get best fitted estimator
    estimator: Any = flaml_automl.model.estimator
    # find algorithm/type of estimator
    if isinstance(estimator, XGBClassifier):
        pass  # xgboost
    elif isinstance(estimator, LGBMClassifier):
        estimator = estimator.booster_  # lgbm
    elif isinstance(estimator, RandomForestClassifier):
        pass  # sklearn
    elif isinstance(estimator, CatBoostClassifier):
        pass  # catboost
    elif isinstance(estimator, DecisionTreeClassifier):
        pass  # sklearn
    elif isinstance(estimator, ExtraTreeClassifier):
        pass  # sklearn
    else:
        raise NotImplementedError(
            f'estimator "{estimator.__class__.__name__}" not found'
        )
    return estimator


def log_mlflow_model(
    estimator: Any,
    artifact_path: Union[Path, str],
    conda_env: str,
    registered_model_name: Optional[str] = None
):
    """Logs the underlying estimator of :class:`flaml.AutoML` as an flavor-specific ``MLflow`` artifact

    Note:
        FLAML does not exposes the underlying estimator with the same API
        for ``mlflow.[flavor].log_model``. Hence, it is needed to the find the estimator first,
        then use the correct flavor for it.

    Args:
        estimator (Any): A trained :class:`flaml.AutoML` model that has ``flaml.model`` populated.
            Note that the list of estimators can be found by ``flaml.AutoML.estimator_list``.
        artifact_path (Union[Path, str]): A path to save the tracked model as an mlflow artifact
        conda_env (str): Path to conda environment. If None, inferred by mlflow.
        registered_model_name (Optional[str]): The name of the model if registration of the
            model is desired. Giving the same name for multiple models, uses the default
            versioning by mlflow. Defaults to None.
    """
    # find the estimator algorithm/type
    estimator = find_estimator(flaml_automl=estimator)
    # convert Path to posix since mlflow only accept posix
    if isinstance(artifact_path, Path):
        artifact_path = artifact_path.as_posix()

    # find the mlflow model flavor and track the underlying estimator with it
    if isinstance(estimator, XGBClassifier):
        mlflow.xgboost.log_model(
            xgb_model=estimator,
            artifact_path=artifact_path,
            conda_env=conda_env,
            registered_model_name=registered_model_name
        )
    if isinstance(estimator, LGBMClassifier):
        mlflow.lightgbm.log_model(
            lgb_model=estimator,
            artifact_path=artifact_path,
            conda_env=conda_env,
            registered_model_name=registered_model_name
        )
    if isinstance(estimator, CatBoostClassifier):
        mlflow.catboost.log_model(
            cb_model=estimator,
            artifact_path=artifact_path,
            conda_env=conda_env,
            registered_model_name=registered_model_name
        )
    else:
        # sklearn api: RandomForestClassifier, DecisionTreeClassifier, ...
        mlflow.sklearn.log_model(
            sk_model=estimator,
            artifact_path=artifact_path,
            conda_env=conda_env,
            registered_model_name=registered_model_name
        )

    logger.info(
        f'model of type "{estimator.__class__.__name__}"'
        f' is tracked via MLflow.'
    )
