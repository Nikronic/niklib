## Setup

It is been explained why some of requirements are needed. You can install these manually if you want to be sure about the environment.

### Install Core packages

Note that you can use `conda` and `mamba` in all following commands, but we stick to the `pip` and `venv`.

#### Data

1. xmltodict: `pip install xmltodict`: Some helping with parsing data extracted
from pdf or other media to common data format.
2. pandas: `pip install pandas`: main tool for exploratory data analysis
3. numpy: `pip install numpy` (it should be installed already): array manipulation
here and there
4. PyPDF2: `pip install pypdf2`: organizing pdf files particularly extracting data
5. pikepdf: `pip install pikepdf`: for manipulation and repair of PDFs. I particularly use this for reading Adobe protected PDFs that forced you to use Adobe Reader (because of `XFA` forms - these damned propriety formats :\)
6. python-dateutil: `pip install python-dateutil`

#### Modeling

1. sklearn: `pip install scikit-learn`: For preprocessing (not EDA which is done by pandas) for modeling and also the modeling itself. (I highly appreciate tree based models)
2. flaml: `pip install flaml`: The main automl modeling. It installs cuda toolkit, xgboost and lightgbm but not other necessary libs if you want such as catboost, transformers, etc. As I am relying on tree based model as the baseline almost always, only tree based dependencies are installed.
3. catboost: `pip install catboost`: For `flaml` tree based dependency.
4. xgboost: `pip install xgboost`: For `flaml` tree based dependency.
5. lightgbm: `pip install lightgbm`: For `flaml` dependency.

#### Serving

1. fastapi: `pip install fastapi`: For creating APIs very fast.
2. gunicorn: `pip install gunicorn`: Debug level server
3. sqlalchemy: `pip install sqlalchemy`: For databases used via API
4. uvicorn (standard): `pip install uvicorn[standard]`: For serving in production. If you want to use `uvicorn` for debugging, it is better to use `pip install uvicorn` as this is a pure python and easier to read.

### Install Helpers Packages

Currently, they all are needed for the code to work, but they will be made optional maybe in future.

1. mlflow: `pip install mlflow`: For tracking experiments, codes, models, etc.
2. dvc: `pip install dvc`: Data version control which is a must have in ML. Note that even though one can use both CLI and python SKD and also can install `dvc` in system-wide, because I use it in integration with `mlflow`, I prefer to have `dvc` in this virtual environment rather than OS package level.
3. enlighten: `pip install enlighten`: For having progress bar in log that can be redirected from std to another std. (here from console to file for mlflow artifact)
4. matplotlib: `pip install matplotlib`: for visualizations.

### Docs

The only mandatory one here is `sphinx`. All other ones can be ignored and in that case, you need to remove the corresponding line in `docs/src/conf.py`.

1. sphinx: `pip install sphinx`: Building the docs.
2. sphinx-rtd-theme: `pip install sphinx-rtd-theme`: Just a theme.
3. sphinx-autodoc-typehints: `pip install sphinx-autodoc-typehints`: For automatically documenting type hints
4. sphinx-copybutton: `pip install sphinx-copybutton`: Copy button for the source code.
5. furo: `pip install furo`: Sphinx Furo theme
