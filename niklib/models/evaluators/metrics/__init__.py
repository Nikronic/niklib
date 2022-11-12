"""Different metrics from what sklearn.metrics_ offers or our own custom metrics

Note that for deep learning based metrics that need computational graph or neural network
API such as using another model or a network as a metric (similar to feature extraction),
then user should first implement all required models/networks in
:mod:`niklib.models.estimators.networks <niklib.models.estimators.networks>`
or other appropriate submodules then import them here and just make a call to them.
For instance assume we have VGG models in `niklib.models.estimators.networks.vgg.py`::

    from niklib.models.estimators.networks.vgg import vgg16
    def vgg16_metric_via_layer_x_and_y(y_true, y_pred):
        ...
        value_1 = vgg16(y_true, y_pred, layer=1)
        value_2 = vgg16(y_true, y_pred, layer=2)
        value = value_1 + value_2
        ...
        return value

.. _sklearn.metrics: https://scikit-learn.org/stable/modules/classes.html#module-sklearn.metrics

"""

# helpers
import logging


# set logger
logger = logging.getLogger(__name__)
