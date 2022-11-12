"""Contains core functionalities that is shared by all preprocessors.

"""

# core
from sklearn import model_selection
from sklearn.compose import ColumnTransformer
from sklearn.compose import make_column_selector
import pandas as pd
import numpy as np
# ours
from niklib.models.preprocessors import EXAMPLE_COLUMN_TRANSFORMER_CONFIG_X
from niklib.models.preprocessors import EXAMPLE_PANDAS_TRAIN_TEST_SPLIT
from niklib.models.preprocessors import EXAMPLE_TRAIN_TEST_EVAL_SPLIT
from niklib.models.preprocessors import TRANSFORMS
# helpers
from typing import Callable, Tuple, Optional, Any, List, Union
import inspect
import logging
import pathlib
import json


# configure logging
logger = logging.getLogger(__name__)


class TrainTestEvalSplit:
    """Convert a pandas dataframe to a numpy array for with train, test, and eval splits

    For conversion from :class:`pandas.DataFrame` to :class:`numpy.ndarray`, we use the same
    functionality as :meth:`pandas.DataFrame.to_numpy`, but it separates dependent and
    independent variables given the target column ``target_column``.

    Note:

        * To obtain the eval set, we use the train set as the original data to be splitted 
          i.e. the eval set is a subset of train set. This is of course to make 
          sure model by no means sees the test set.
        * ``args`` cannot be set directly and need to be provided using a json file. 
          See :meth:`set_configs` for more information.
        * You can explicitly override following ``args`` by passing it as an argument
          to :meth:`__init__`:

            * :attr:`random_state`
            * :attr:`stratify`

    Returns:
        Tuple[:class:`numpy.ndarray`, ...]:
        Order is ``(x_train, x_test, x_eval, y_train, y_test, y_eval)``
    """

    def __init__(
        self,
        stratify: Any = None,
        random_state: Union[np.random.Generator, int] = None
    ) -> None:
        self.logger = logging.getLogger(logger.name + self.__class__.__name__)
        self.CONF = self.set_configs()

        # override configs if explicitly set
        self.random_state = random_state
        self.stratify = stratify

    def set_configs(self, path: Union[str, pathlib.Path] = None) -> dict:
        """Defines and sets the config to be parsed

        The keys of the configs are the attributes of this class which are:

            * test_ratio (float): Ratio of test data
            * eval_ratio (float): Ratio of eval data
            * shuffle (bool): Whether to shuffle the data
            * stratify (Optional[:class:`numpy.ndarray`]): If not None, this is used to stratify the data
            * random_state (Optional[int]): Random state to use for shuffling

        Note:
            You can explicitly override following attributes by passing it as an argument
            to :meth:`__init__`:

                * :attr:`random_state`
                * :attr:`stratify`

        The values of the configs are parameters and can be set manually
        or extracted from JSON config files by providing the path to the JSON file.

        Args:
            path: path to the JSON file containing the configs

        Returns:
            dict: A dictionary of `str`: `Any` pairs of configs as class attributes
        """

        # convert str path to Path
        if isinstance(path, str):
            path = pathlib.Path(path)

        # if no json is provided, use the default configs
        if path is None:
            path = EXAMPLE_TRAIN_TEST_EVAL_SPLIT
        self.conf_path = path

        # log the path used
        self.logger.info(f'Config file "{self.conf_path}" is being used')

        # read the json file
        with open(path, 'r') as f:
            configs = json.load(f)

        # set the configs if explicit calls made to this method
        self.CONF = configs
        # return the parsed configs
        return configs

    def as_mlflow_artifact(self, target_path: Union[str, pathlib.Path]) -> None:
        """Saves the configs to the MLFlow artifact directory

        Args:
            target_path: Path to the MLFlow artifact directory. The name of the file
                will be same as original config file, hence, only provide path to dir.
        """

        # convert str path to Path
        if isinstance(target_path, str):
            target_path = pathlib.Path(target_path)

        if self.conf_path is None:
            raise ValueError(
                'Configs have not been set yet. Use set_configs to set them.')

        # read the json file
        with open(self.conf_path, 'r') as f:
            configs = json.load(f)

        # save the configs to the artifact directory
        target_path = target_path / self.conf_path.name
        with open(target_path, 'w') as f:
            json.dump(configs, f)

    def __call__(
        self,
        df: pd.DataFrame,
        target_column: str,
        *args: Any, **kwds: Any
    ) -> Tuple[np.ndarray, ...]:
        """Convert a pandas dataframe to a numpy array for with train, test, and eval splits

        Args:
            df (:class:`pandas.DataFrame`): Dataframe to convert
            target_column (str): Name of the target column

        Returns:
            Tuple[:class:`numpy.ndarray`, ...]: Order is
            ``(x_train, x_test, x_eval, y_train, y_test, y_eval)``
        """
        # get values from config
        test_ratio = self.CONF['test_ratio']
        eval_ratio = self.CONF['eval_ratio']
        shuffle = self.CONF['shuffle']
        stratify = self.CONF['stratify']
        random_state = self.CONF['random_state'] if self.random_state is None else self.random_state

        # separate dependent and independent variables
        y = df[target_column].to_numpy()
        x = df.drop(columns=[target_column], inplace=False).to_numpy()

        # create train and test data
        x_train, x_test, y_train, y_test = model_selection.train_test_split(
            x, y,
            train_size=None,
            test_size=test_ratio,
            shuffle=shuffle,
            stratify=stratify,
            random_state=random_state
        )
        if eval_ratio == 0.:
            return (x_train, x_test, y_train, y_test)

        # create eval data from train data
        x_train, x_eval, y_train, y_eval = model_selection.train_test_split(
            x_train, y_train,
            train_size=None,
            test_size=eval_ratio,
            shuffle=shuffle,
            stratify=stratify,
            random_state=random_state
        )
        return (x_train, x_test, x_eval, y_train, y_test, y_eval)


class PandasTrainTestSplit:
    """Split a pandas dataframe with train and test

    Note:
        This is a class very similar to :class:`TrainTestEvalSplit` with this difference
        that this class is specialized for Pandas Dataframe and since we are going to use
        augmentation on Pandas Dataframe rather than Numpy, then this class enable us
        to do augmentation only on train split and let the test part stay as it is.

    Note:

        * ``args`` cannot be set directly and need to be provided using a json file. 
          See :meth:`set_configs` for more information.
        * You can explicitly override following ``args`` by passing it as an argument
          to :meth:`__init__`:

            * :attr:`random_state`
            * :attr:`stratify`

    Returns:
        Tuple[:class:`numpy.ndarray`, ...]: A tuple of 
        ``(data_train, data_test)`` which contains both dependent and 
        independent variables
    """

    def __init__(
        self,
        stratify: Any = None,
        random_state: Union[np.random.Generator, int] = None
    ) -> None:
        self.logger = logging.getLogger(logger.name + self.__class__.__name__)
        self.CONF = self.set_configs()

        # override configs if explicitly set
        self.random_state = random_state
        self.stratify = stratify

    def set_configs(self, path: Union[str, pathlib.Path] = None) -> dict:
        """Defines and sets the config to be parsed

        The keys of the configs are the attributes of this class which are:

            * train_ratio (float): Ratio of train data
            * shuffle (bool): Whether to shuffle the data
            * stratify (Optional[np.ndarray]): If not None, this is used to stratify the data
            * random_state (Optional[int]): Random state to use for shuffling

        Note:
            You can explicitly override following attributes by passing it as an argument
            to :meth:`__init__`:

                * :attr:`random_state`
                * :attr:`stratify`

        The values of the configs are parameters and can be set manually
        or extracted from JSON config files by providing the path to the JSON file.

        Args:
            path: path to the JSON file containing the configs

        Returns:
            dict: A dictionary of ``str``: ``Any`` pairs of configs as class attributes
        """

        # convert str path to Path
        if isinstance(path, str):
            path = pathlib.Path(path)

        # if no json is provided, use the default configs
        if path is None:
            path = EXAMPLE_PANDAS_TRAIN_TEST_SPLIT
        self.conf_path = path

        # log the path used
        self.logger.info(f'Config file "{self.conf_path}" is being used')

        # read the json file
        with open(path, 'r') as f:
            configs = json.load(f)

        # set the configs if explicit calls made to this method
        self.CONF = configs
        # return the parsed configs
        return configs

    def as_mlflow_artifact(self, target_path: Union[str, pathlib.Path]) -> None:
        """Saves the configs to the MLFlow artifact directory

        Args:
            target_path: Path to the MLFlow artifact directory. The name of the file
                will be same as original config file, hence, only provide path to dir.
        """

        # convert str path to Path
        if isinstance(target_path, str):
            target_path = pathlib.Path(target_path)

        if self.conf_path is None:
            raise ValueError(
                'Configs have not been set yet. Use set_configs to set them.')

        # read the json file
        with open(self.conf_path, 'r') as f:
            configs = json.load(f)

        # save the configs to the artifact directory
        target_path = target_path / self.conf_path.name
        with open(target_path, 'w') as f:
            json.dump(configs, f)

    def __call__(
        self,
        df: pd.DataFrame,
        target_column: str,
        *args: Any, **kwds: Any
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Split a pandas dataframe with train and test splits

        Args:
            df (:class:`pandas.DataFrame`): Dataframe to convert
            target_column (str): Name of the target column

        Returns:
            Tuple[:class:`numpy.ndarray`, ...]: Order is
            ``(data_train, data_test)``
        """
        # get values from config
        train_ratio = self.CONF['train_ratio']
        shuffle = self.CONF['shuffle']
        stratify = self.CONF['stratify']
        random_state = self.CONF['random_state'] if self.random_state is None else self.random_state

        # shuffle dataframe
        if shuffle:
            df = df.sample(frac=1, random_state=random_state)

        # stratify dataframe
        if stratify is not None:
            raise NotImplementedError(
                'Stratify is not implemented yet. Sadge :(')

        # split dataframe into train and test by rows
        idx: int = int(len(df) * train_ratio)
        data_train: pd.DataFrame = df.iloc[:idx, :]
        data_test: pd.DataFrame = df.iloc[idx:, :]
        return (data_train, data_test)


class ColumnSelector:
    """Selects columns based on regex pattern and dtype

    User can specify the dtype of columns to select, and the dtype of columns to ignore.
    Also, user can specify the regex pattern for including and excluding columns, separately.

    This is particularly useful when combined with :class:`sklearn.compose.ColumnTransformer`
    to apply different sort of ``transformers`` to different subsets of columns. E.g::

        # select columns that contain 'Country' in their name and are of type `np.float32`
        columns = preprocessors.ColumnSelector(columns_type='numeric',
                                               dtype_include=np.float32,
                                               pattern_include='.*Country.*',
                                               pattern_exclude=None,
                                               dtype_exclude=None)(df=data)
        # use a transformer for selected columns
        ct = preprocessors.ColumnTransformer(
            [('some_name',                   # just a name
            preprocessors.StandardScaler(),  # the transformer
            columns),                        # the columns to apply the transformer to
            ],
        )

        ct.fit_transform(...)

    Note:
        If the data that is passed to the :class:`ColumnSelector` is a :class:`pandas.DataFrame`,
        then you can ignore calling the instance of this class and directly use it in the
        pipeline. E.g::

            # select columns that contain 'Country' in their name and are of type `np.float32`
            columns = preprocessors.ColumnSelector(columns_type='numeric',
                                                   dtype_include=np.float32,
                                                   pattern_include='.*Country.*',
                                                   pattern_exclude=None,
                                                   dtype_exclude=None)  # THIS LINE
            # use a transformer for selected columns
            ct = preprocessors.ColumnTransformer(
                [('some_name',                   # just a name
                preprocessors.StandardScaler(),  # the transformer
                columns),                        # the columns to apply the transformer to
                ],
            )

            ct.fit_transform(...)


    See Also:
        :class:`sklearn.compose.make_column_selector` as ``ColumnSelector`` follows the
        same semantics.

    """

    def __init__(
        self,
        columns_type: str,
        dtype_include: Any,
        pattern_include: Optional[str] = None,
        dtype_exclude: Any = None,
        pattern_exclude: Optional[str] = None
    ) -> None:
        """Selects columns based on regex pattern and dtype

        Args:
            columns_type (str): Type of columns:

                1. ``'string'``: returns the name of the columns. Useful for 
                   :class:`pandas.DataFrame`
                2. ``'numeric'``: returns the index of the columns. Useful for
                   :class:`numpy.ndarray`

            dtype_include (type): Type of the columns to select. For more info
                see :meth:`pandas.DataFrame.select_dtypes`.
            pattern_include (str): Regex pattern to match columns to **include**
            dtype_exclude (type): Type of the columns to ignore. For more info
                see :meth:`pandas.DataFrame.select_dtypes`. Defaults to None.
            pattern_exclude (str): Regex pattern to match columns to **exclude**
        """
        self.columns_type = columns_type
        self.pattern_include = pattern_include
        self.pattern_exclude = pattern_exclude
        self.dtype_include = dtype_include
        self.dtype_exclude = dtype_exclude

    def __call__(
        self,
        df: pd.DataFrame,
        *args: Any, **kwds: Any
    ) -> Union[List[str], List[int]]:
        """

        Args:
            df (:class:`pandas.DataFrame`): Dataframe to extract columns from

        Returns:
            Union[List[str], List[int]]: List of names or indices of
            filtered columns

        Raises:
            ValueError: If the ``df`` is not instance of :class:`pandas.DataFrame`

        """
        if not isinstance(df, pd.DataFrame):
            raise TypeError(f'`df` must be a `DataFrame` not {type(df)}')

        # since `make_column_selector` will ignore pattern if None provide,
        # we need to set pattern (pattern_exclude) to sth pepega to ignore all columns
        pattern_exclude = '\~' if self.pattern_exclude is None else self.pattern_exclude

        # first select desired then select undesired
        columns_to_include = make_column_selector(
            dtype_include=self.dtype_include,
            dtype_exclude=self.dtype_exclude,
            pattern=self.pattern_include
        )(df)
        columns_to_exclude = make_column_selector(
            dtype_include=self.dtype_include,
            dtype_exclude=self.dtype_exclude,
            pattern=pattern_exclude
        )(df)

        # remove columns_to_exclude from columns_to_include
        columns = [
            column for column in columns_to_include if column not in columns_to_exclude]

        # return columns based on columns_type (`columns` is already `string`)
        if self.columns_type == 'numeric':
            return [df.columns.get_loc(column) for column in columns]
        return columns


class ColumnTransformerConfig:
    """A helper class that parses configs for using the :class:`sklearn.compose.ColumnTransformer`

    The purpose of this class is to create the list of ``transformers`` to be used
    by the :class:`sklearn.compose.ColumnTransformer`. Hence, one needs to define the configs
    by using the :meth:`set_configs` method. Then use the :meth:`generate_pipeline` method
    to create the list of transformers.

    This class at the end, will return a list of tuples, where each tuple is a in
    the form of ``(name, transformer, columns)``.
    """

    def __init__(self) -> None:

        self.logger = logging.getLogger(logger.name+self.__class__.__name__)
        self.CONF = self.set_configs()

    def set_configs(self, path: Union[str, pathlib.Path] = None) -> dict:
        """Defines and sets the config to be parsed

        The keys of the configs are the names of the transformers. They must include
        the API name of one of the available transforms at the end:

            * sklearn transformers: Any class that could be used for transformation
              that is importable as ``sklearn.preprocessing.API_NAME``
            * custom transformers: Any class that is not a ``sklearn`` transformer
              and is importable as ``niklib.models.preprocessors.API_NAME``

        This naming convention is used to create proper transformers for each type of data.
        e.g in json format::

            "age_StandardScaler": {
                "columns_type": "'numeric'",
                "dtype_include": "np.float32",
                "pattern_include": "'age'",
                "pattern_exclude": "None",
                "dtype_exclude": "None",
                "group": "False",
                "use_global": "False"
            }

            "sex_OneHotEncoder": {
                "columns_type": "'numeric'",
                "dtype_include": "'category'",
                "pattern_include": "'VisaResult'",
                "pattern_exclude": "None",
                "dtype_exclude": "None",
                "group": "True",
                "use_global": "True"
            }

        The values of the configs are the columns to be transformed. The columns can be
        obtained by using :class:`niklib.models.preprocessors.core.ColumnSelector`
        which requires user to pass certain parameters. This parameters can be set manually
        or extracted from JSON config files by providing the path to the JSON file.

        The ``group`` key is used to determine if the transformer should be applied considering
        a group of columns or not. If ``group`` is ``True``, then required values for transformation
        are obtained from all columns rather than handling each group separately. For instance,
        one can use ``OneHotEncoding`` on a set of columns where if ``group`` is ``True``,
        then all unique categories of all of those columns are extracted, then transformed.
        if ``group`` is ``False``, then each column will have be transformed based on their unique
        categories independently. (``group`` cannot be passed to :class:`ColumnSelector`)

        The ``use_global`` key is used to determine if the transformer should be applied
        considering the all data or train data (since fitting transformation for normalization
        need to be only done on *train* data). If ``use_global`` is ``True``, then the transformer
        will be applied on all data. This is particularly useful for one hot encoding categorical
        features where some categories might are rare and might only exist in test and eval data.

        Args:
            path: path to the JSON file containing the configs

        Returns:
            dict: A dictionary where keys are string names, values are tuple of 
            :class:`niklib.models.preprocessors.core.ColumnSelector` instance and a boolean control
            variable which will be passed to :meth:`generate_pipeline`.
        """

        # convert str path to Path
        if isinstance(path, str):
            path = pathlib.Path(path)

        # if no json is provided, use the default configs
        if path is None:
            path = EXAMPLE_COLUMN_TRANSFORMER_CONFIG_X
        self.conf_path = path

        # log the path used
        self.logger.info(f'Config file "{self.conf_path}" is being used')

        # read the json file
        with open(path, 'r') as f:
            configs = json.load(f)

        # parse the configs (json files)
        parsed_configs = {}
        for key, value in configs.items():
            parsed_values = {k: eval(v) for k, v in value.items()}

            # extract 'group'; if didn't exist in configs, then set it to False
            group = parsed_values.get('group', False)
            # remove 'group' from parsed_values after parsing it
            if 'group' in parsed_values:
                del parsed_values['group']

            # extract 'use_global'; if didn't exist in configs, then set it to False
            use_global = parsed_values.get('use_global', False)
            # remove 'use_global' from parsed_values after parsing it
            if 'use_global' in parsed_values:
                del parsed_values['use_global']
            parsed_configs[key] = (
                ColumnSelector(**parsed_values),
                group,
                use_global
            )

        # set the configs when explicit call to this method is made
        self.CONF = parsed_configs

        # return the parsed configs
        return parsed_configs

    def as_mlflow_artifact(self, target_path: Union[str, pathlib.Path]) -> None:
        """Saves the configs to the MLFlow artifact directory

        Args:
            target_path: Path to the MLFlow artifact directory. The name of the file
                will be same as original config file, hence, only provide path to dir.
        """

        # convert str path to Path
        if isinstance(target_path, str):
            target_path = pathlib.Path(target_path)

        if self.conf_path is None:
            raise ValueError(
                'Configs have not been set yet. Use set_configs to set them.')

        # read the json file
        with open(self.conf_path, 'r') as f:
            configs = json.load(f)

        # save the configs to the artifact directory
        target_path = target_path / self.conf_path.name
        with open(target_path, 'w') as f:
            json.dump(configs, f)

    @staticmethod
    def extract_selected_columns(
        selector: ColumnSelector,
        df: pd.DataFrame
    ) -> Union[List[str], List[int]]:
        """Extracts the columns from the dataframe based on the selector

        Note:
            This method is simply a wrapper around :class:`niklib.models.preprocessors.core.ColumnSelector`
            that makes the call given a dataframe. I.e.::

                # assuming same configs
                selector = preprocessors.ColumnSelector(...)
                A = ColumnTransformerConfig.extract_selected_columns(selector=selector, df=df)
                B = selector(df)
                A == B  # True

            Also, this is a static method.

        Args:
            selector (:class:`niklib.models.preprocessors.core.ColumnSelector`): Initialized
                selector object
            df (:class:`pandas.DataFrame`): Dataframe to extract columns from

        Returns:
            Union[List[str], List[int]]: List of columns to be transformed
        """
        return selector(df=df)

    @staticmethod
    def __check_arg_exists(callable: Callable, arg: str) -> None:
        """Checks if the argument exists in the callable signature

        Args:
            callable (Callable): Callable to check the argument in
            arg (str): Argument to check if exists in the callable signature

        Raises:
            ValueError: If the argument does not exist in the callable signature
        """

        # get the signature of the callable
        sig = inspect.signature(callable)

        # check if the argument exists in the signature
        if arg not in sig.parameters:
            raise ValueError(
                f'Argument "{arg}" does not exist in the "{callable}" signature')

    @staticmethod
    def __get_df_column_unique(df: pd.DataFrame, loc: Union[int, str]) -> list:
        """Gets uniques of a column in a dataframe

        Args:
            df (:class:`pandas.DataFrame`): Dataframe to get uniques from
            loc (Union[int, str]): Column to locate on the dataframe

        Returns:
            list: List of unique values in the column. Values of the returned
            list can be anything that is supported by :class:`pandas.DataFrame`
        """

        # if loc is an int use iloc
        if isinstance(loc, int):
            return list(df.iloc[:, loc].unique())

        # if loc is a str, use loc
        if isinstance(loc, str):
            return list(df.loc[:, loc].unique())

    def calculate_params(
        self,
        df: pd.DataFrame,
        columns: List,
        group: bool,
        transformer_name: str
    ) -> dict:
        """Calculates the parameters for the group transformation w.r.t. the transformer name

        Args:
            df (:class:`pandas.DataFrame`): Dataframe to extract columns from
            columns (List): List of columns to be transformed
            group (bool): If True, then the columns will be grouped together and
                the parameters will be calculated over all columns passed in
            transformer_name (str): Name of the transformer. It is used to determine
                the type of params to be passed to the transformer. E.g. if ``transformer_name``
                corresponds to ``OneHotEncoding``, then params would be unique categories.

        Raises:
            ValueError: If the transformer name is not implemented but supported

        Returns:
            dict: Parameters for the group transformation
        """

        # the params to be returned
        params: dict = {}

        # if transformer is OneHotEncoder, extract the unique categories from all columns
        if transformer_name == 'OneHotEncoder':
            unique_values: list = []
            # get all uniques from all columns if 'group' is True
            if group:
                for col in columns:
                    unique_values.extend(
                        self.__get_df_column_unique(df=df, loc=col)
                    )
                unique_values = list(set(unique_values))
            else:
                # if columns is a list, then we assume that user wants default behavior
                #   of OneHotEncoder and left finding categories to 3rd party library
                if len(columns) > 1:
                    return {}  # return empty params
                unique_values = self.__get_df_column_unique(
                    df=df,
                    loc=columns[0]
                )
            # check correct arg to set given the transformer object signature
            transformer_arg = 'categories'
            self.__check_arg_exists(
                TRANSFORMS[transformer_name], transformer_arg)
            # set args appropriately
            # for OneHotEncoder, the arg is 'categories'
            params[transformer_arg] = [
                unique_values for _ in range(len(columns))
            ]
        else:
            if group:
                raise NotImplementedError(
                    f'Group transformation param calculation'
                    f'is not implemented for {transformer_name}')
        return params

    def _check_overlap_in_transformation_columns(
        self,
        transformers: List[Tuple]
    ) -> None:
        """Checks if there are multiple transformers on the same columns and reports them

        Throw info if columns of different transformers overlap. I.e. at least another
        transform is happening on a column that is already has been transformed.

        Note:
            This is not a bug or misbehavior since we should be able to pipe
            multiple transformers sequentially on the same column (e.g. ``add`` -> ``divide``).
            The warning is thrown when user didn't meant to do so since the output might be
            acceptable but wrong values and there is no way to find out except manual inspection.
            Hence, this method will make the user aware that something might be wrong.

        Args:
            transformers (List[Tuple]):
                A list of tuples, where each tuple is a in the form of
                ``(name, transformer, columns)`` where ``name`` is the name of the
                transformer, ``transformer`` is the transformer object and ``columns``
                is the list of columns names to be transformed.
        Todo:
            Should I also check if each list of column is a set? (no duplicate in same list)
            see https://stackoverflow.com/a/3697450/18971263
        """

        count = len(transformers)

        for i in range(count):
            for j in range(i+1, count):
                # (_ , _, columns)
                columns_a: List[Union[int, str]] = transformers[i][-1]
                # (_ , _, columns)
                columns_b: List[Union[int, str]] = transformers[j][-1]
                overlap: List[Union[int, str]] = list(
                    set(columns_a).intersection(columns_b))
                if len(overlap) > 0:  # found overlap
                    name_a: str = transformers[i][0]  # (name, _, _)
                    name_b: str = transformers[j][0]  # (name, _, _)
                    self.logger.info(
                        f'transformer "{name_a}" is overlapping with\n'
                        f' transformer "{name_b}" on columns {overlap}')

    def generate_pipeline(
        self,
        df: pd.DataFrame,
        df_all: Optional[pd.DataFrame] = None
    ) -> list:
        """Generates the list of transformers to be used by the :class:`sklearn.compose.ColumnTransformer`

        Note:
            For more info about how the transformers are created, see methods
            :meth:`set_configs`, :meth:`extract_selected_columns` and
            :meth:`calculate_params`.

        Args:
            df (:class:`pandas.DataFrame`): Dataframe to extract columns from
                if ``df_all`` is None, then this is interpreted as train data
            df_all (Optional[:class:`pandas.DataFrame`]): Dataframe to extract columns from
                if ``df_all`` is not None, then this is interpreted as entire data. For
                more info see :meth:`set_configs`.

        Raises:
            ValueError: If the naming convention used for the keys in the
                configs (see :meth:`set_configs`) is not followed.

        Returns:
            list: A list of tuples, where each tuple is a in the form of
            ``(name, transformer, columns)`` where ``name`` is the name of the
            transformer, ``transformer`` is the transformer object and ``columns``
            is the list of columns names to be transformed.
        """

        # just place holders for what we want
        name: str = ''              # name of the transformer
        transformer: object = None  # initialized sklearn transformer
        columns: List = []          # columns to transform

        # list of (name, transformer, columns) tuples to return
        transformers: List[Tuple] = []

        # iterate through the configs to build transformer instances appropriately
        for key, value in self.CONF.items():
            # value is tuple of (selector, group)
            selector: ColumnSelector = value[0]
            group: bool = value[1]
            use_global: bool = value[2]
            # extract transformer name
            transformer_name = key.split('_')[-1]
            if transformer_name in TRANSFORMS:
                name = key
                # extract list of columns names
                columns = self.extract_selected_columns(
                    selector=selector,
                    df=df
                )
                # if group not false, extract group level transformation params
                group_params: dict = {}
                group_params = self.calculate_params(
                    df=df_all if use_global else df,
                    columns=columns,
                    group=group,
                    transformer_name=transformer_name
                )
            # build transformer object
                transformer = TRANSFORMS[transformer_name](**group_params)
            else:
                raise ValueError(f'Unknown transformer {key} in config.')

            # add to the list of transformers
            transformers.append((name, transformer, columns))

        # throw logs if columns of different self.CONF overlap
        self._check_overlap_in_transformation_columns(transformers)
        return transformers


def get_transformed_feature_names(
    column_transformer: ColumnTransformer,
    original_columns_names: List[str],
) -> List[str]:
    """Gives feature names for transformed data via original feature names

    This is super useful as the default
    :meth:`sklearn.compose.ColumnTransformer.get_feature_names_out` uses meaningless names
    for features after transformation which makes tracking the transformed features almost 
    impossible as it uses ``f0[_category], f1[_category], ... fn[_category]` as feature names.
    This method for example, extracts the name of original column ``A`` (with categories ``[a, b]``)
    before transformation and finds new columns after transforming that column and names them
    ``A_a`` and ``A_b`` meanwhile ``sklearn`` method gives ``x[num0]_a`` and ``x_[num0]_b``.

    Args:
        column_transformer (:class:`sklearn.compose.ColumnTransformer`): A **fitted**
            column transformer that has ``.transformers_`` where each is a tuple
            as ``(name, transformer, in_columns)``. ``in_columns`` used to detect the
            original index of transformed columns. 
        original_columns_names (List[str]): List of original columns names before transformation

    Returns:
        List[str]: A list of transformed columns names prefixed with original columns names

    """

    # build a dictionary of index:feature_name from untransformed dataset
    original_columns_dict: dict = {}
    # build index of transformed columns from transformers
    new_index: List[int] = []
    for t in column_transformer.transformers_:
        new_index.extend(t[2])  # (name, transformer, **in_columns**)
    # build a mapping between original index of columns and their names
    for ni in new_index:
        original_columns_dict[ni] = original_columns_names[ni]
    # original_columns_dict = dict(sorted(original_columns_dict.items()))
    original_columns_dict = dict(
        sorted(
            original_columns_dict.items(),
            key=lambda x: x[0],
            reverse=True
        )
    )
    # replace idx with `original feature name` in `transformed feature names``
    feature_names: List[str] = column_transformer.get_feature_names_out()
    new_feature_names: List[str] = []
    for fn in feature_names:
        # reverse it so if we have '10', it does not get replaced with '1' and '0' first
        for k, v in original_columns_dict.items():
            # if index of orig feature is in transformed name
            if str(k) in fn:
                # replace `x[num]` with original column names
                fn = fn.replace(f'x{k}', v)
                new_feature_names.append(fn)
                # we can have only one index, so go for next feature if u found one already
                break

    return new_feature_names


def move_dependent_variable_to_end(
    df: pd.DataFrame,
    target_column: str
) -> pd.DataFrame:
    """Move the dependent variable to the end of the dataframe

    This is useful for some frameworks that require the dependent variable to be the last
    or in general form, it is way easier to play with :class:`numpy.ndarray` s when the
    dependent variable is the last one.

    Note:
        This is particularly is useful for us since we have multiple columns of the same
        type in our dataframe, and when we want to apply same preprocessing to a all members
        of a group of features, we can directly use index of those features from our pandas
        dataframe in converted numpy array. E.g::

            df = pd.DataFrame(...)
            x = df.to_numpy()
            index = df.columns.get_loc(a_group_of_columns_with_the_same_logic)
            x[:, index] = transform(x[:, index])

    Args:
        df (:class:`pandas.DataFrame`): Dataframe to convert
        target_column (str): Name of the target column

    Returns:
        :class:`pandas.DataFrame`: Dataframe with the dependent variable at the end

    """

    columns = df.columns.tolist()
    columns.pop(columns.index(target_column))
    df = df[columns + [target_column]]
    return df
