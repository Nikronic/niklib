## Setup
It is been explained why some of requirements are needed. You can install these manually if you want to be sure about the environment but it is way easier to just install using conda environment as a `env.yml` file containing all necessary dependencies is already provided.

### `mamba` and `conda-forge`
It is fast and for some reason, do way better job at resolving while
conda can't. `conda install -c conda-forge mamba`

### Install Core packages
Note that you can use `conda` instead of `mamba` in all following commands,
but why would you want to do it? `mamba` is better!

#### Data
1. xmltodict: `mamba install -c conda-forge xmltodict`: Some helping with parsing data extracted
from pdf or other media to common data format.
2. pandas: `mamba install pandas`: main tool for exploratory data analysis
3. numpy: `mamba install -c conda-forge numpy` (it should be installed already): array manipulation
here and there
4. PyPDF2: `mamba install -c conda-forge pypdf2`: organizing pdf files particularly extracting data
5. pikepdf: `pip install pikepdf`: for manipulation and repair of PDFs. I particularly use this for reading Adobe protected PDFs that forced you to use Adobe Reader (because of `XFA` forms - these damned propriety formats :\)
6. python-dateutil: `mamba install -c conda-forge python-dateutil`: Note that official doc only says
about the `pip` but still install the `conda-forge` one.

#### Modeling
7. sklearn: `mamba install -c conda-forge scikit-learn`: For preprocessing (not EDA which is done by pandas) for modeling and also the modeling itself. (I highly appreciate tree based models)
8. flaml: `mamba install flaml -c conda-forge`: The main automl modeling. It installs cuda toolkit, xgboost and lightgbm but not other necessary libs if you want such as catboost, transformers, etc. As I am relying on tree based model as the baseline almost always, only tree based dependencies are installed.
9. catboost: `mamba install catboost -c conda-forge`: For `flaml` tree based dependency.

#### Serving
10. fastapi: `pip install fastapi`: For creating APIs very fast.
11. gunicorn: `pip install gunicorn`: Debug level server
12. sqlalchemy: `pip install sqlalchemy`: For databases used via API
13. uvicorn (standard): `pip install uvicorn[standard]`: For serving in production. If you want to use `uvicorn` for debugging, it is better to use `pip install uvicorn` as this is a pure python and easier to read.


### Install Helpers Packages
Currently, they all are needed for the code to work, but they will be made optional maybe in future.

1. mlflow: `pip install mlflow`: For tracking experiments, codes, models, etc.
2. enlighten: `mamba install -c conda-forge enlighten`: For having progress bar in log that can be redirected from std to another std. (here from console to file for mlflow artifact)
3. dvc: `mamba install -c conda-forge dvc==2.10.2`: Data version control which is a must have in ML. Note that even though one can use both CLI and python SKD and also can install `dvc` in system-wide, because I use it in integration with `mlflow`, I prefer to have `dvc` in this virtual environment rather than OS package level. Also, make sure to install `2.10.2` until [this bug](https://github.com/iterative/dvc/issues/7927) is fixed. You can of course install the latest version as this bug could be easily resolved by hardcoding.
4. matplotlib: `mamba install -c conda-forge matplotlib`: for vis.

### Docs
The only mandatory one here is `sphinx`. All other ones can be ignored and in that case, you need to remove the corresponding line in `docs/src/conf.py`.
1. sphinx: `pip install sphinx`: Building the docs.
2. sphinx-rtd-theme: `pip install sphinx-rtd-theme`: Just a theme.
3. sphinx-autodoc-typehints: `pip install sphinx-autodoc-typehints`: For automatically documenting type hints
4. : `pip install sphinx-copybutton`: Copy button for the source code.

