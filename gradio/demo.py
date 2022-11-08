# core
import pandas as pd
import numpy as np
import pickle
# ours
from vizard.models import preprocessors
from vizard.models import trainers
# devops
import dvc.api
import mlflow
# demo
import gradio as gr
# helpers
from typing import List


# data versioning config
PATH = 'raw-dataset/all.pkl'  # the main data file (usually the large one you track)
REPO = '/home/nik/my_repo'    # git repo associated with DVC
VERSION = 'v1.0.0'            # which version of data should be loaded
MLFLOW_RUN_ID = 'uuid'        # which run of the model should be used to download artifacts (weights, models) from

# set this to track the URI you defined in `mlflow-server.sh`
mlflow.set_tracking_uri('http://localhost:5000')

# read data from DVC storage
#   only need this data for columns to build Gradio interface properly
data_url = dvc.api.get_url(path=PATH, repo=REPO, rev=VERSION)
data: pd.DataFrame = pd.read_pickle(data_url)

# load fitted preprocessing models
X_CT_NAME = 'some_sklearn_fitted_transformer.pkl'
x_ct_path = mlflow.artifacts.download_artifacts(
    run_id=MLFLOW_RUN_ID,
    artifact_path=f'models/{X_CT_NAME}',
    dst_path=f'gradio/'
)
with open(x_ct_path, 'rb') as f:
    x_ct = pickle.load(f)

# load fitted model for prediction (main model) e.g. flaml automl
FLAML_AUTOML_NAME = 'some_model.pkl'
flaml_automl_path = mlflow.artifacts.download_artifacts(
    run_id=MLFLOW_RUN_ID,
    artifact_path=f'models/{FLAML_AUTOML_NAME}',
    dst_path=f'gradio/'
)
with open(flaml_automl_path, 'rb') as f:
    flaml_automl = pickle.load(f)

# a predict method to use loaded model
def predict(*args):
    # convert to dataframe
    x_test = pd.DataFrame(data=[list(args)], columns=data.columns)
    x_test = x_test.astype(data.dtypes)
    x_test = x_test.to_numpy()
    # preprocess test data
    xt_test = x_ct.transform(x_test)
    # predict
    y_pred = flaml_automl.predict_proba(xt_test)
    label = np.argmax(y_pred)
    y_pred = y_pred[0, label]
    y_pred = y_pred if label == 1 else 1. - y_pred
    msg = f'Percentage: {y_pred * 100:.2f}'
    print(msg)
    return msg, y_pred

# build gradio interface given dataframe dtype
inputs: List[gr.components.Component] = []
for col in data.columns:
    if data[col].dtype == 'category':
        inputs.append(gr.Dropdown(choices=list(data[col].unique()),
                                  label=col))
    elif data[col].dtype == 'float32':
        inputs.append(gr.Number(label=col,
                                value=int(data[col].min())))
    elif data[col].dtype == 'int32':
        inputs.append(gr.Slider(minimum=int(data[col].min()),
                                maximum=int(data[col].max()),
                                step=1,
                                label=col,
                                value=int(data[col].min())))
    else:
        raise ValueError(f'Unknown dtype {data[col].dtype} for column {col}')

# prediction probability output
outputs = [
    gr.Textbox(label='Percentage of success'),
    gr.Number(label='Probability'),
]

examples = [
    # as a list [feature1, feature2, ...]
]

title = 'title of gradio demo'
description = 'description of gradio demo'

# close all Gradio instances
gr.close_all()

# launch gradio
gr.Interface(
    fn=predict,
    inputs=inputs,
    outputs=outputs,
    examples=examples,
    title=title,
    description=description,
    flagging_dir='gradio/flags',
    analytics_enabled=True,
).launch(debug=True, enable_queue=True, server_port=7860)
