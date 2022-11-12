# core
import numpy as np
import pandas as pd
# ours: models
from niklib.models.preprocessors import ColumnTransformer
from niklib.models.preprocessors import OneHotEncoder
# helpers
from typing import List, Union
import logging


# configure logging
logger = logging.getLogger(__name__)


def preview_column_transformer(
    column_transformer: ColumnTransformer,
    original: np.ndarray,
    transformed: np.ndarray,
    df: pd.DataFrame,
    random_state: Union[int, np.random.Generator] = np.random.default_rng(),
    **kwargs
) -> pd.DataFrame:
    """Preview transformed data next to original one obtained via ``ColumnTransformer``

    When the transformation is not :class:`sklearn.preprocessing.OneHotEncoder`,
    the transformed data is previewed next to the original data in a pandas dataframe.

    But when the transformation is :class:`sklearn.preprocessing.OneHotEncoder`,
    this is no longer clean or informative in seeing only 0s and 1s. So, I just 
    skip previewing the transformed data entirely but report following information:

        - The number of columns affected by transformation
        - The number of unique values in all of affected columns
        - The number of newly produced columns

    Args:
        column_transformer (ColumnTransformer): An instance
            of :class:`sklearn.compose.ColumnTransformer`
        original (np.ndarray): Original data as a :class:`numpy.ndarray`.
            Same shape as ``transformed``
        transformed (np.ndarray): Transformed data as a :class:`numpy.ndarray`.
            Same shape as ``original``
        df (:class:`pandas.DataFrame`): A dataframe that hosts the ``original`` and ``transformed``
            data. Used to extract column names and unique values for logging
            information about the transformations done
        random_state (Union[int, np.random.Generator], optional): A seed value or
            instance of  :class:`numpy.random.Generator` for sampling. Defaults to
            :func:`numpy.random.default_rng()`.
        **kwargs: Additional arguments as follows:

            * ``n_samples`` (int): Number of samples to draw. Defaults to 1.

    Raises:
        ValueError: If ``original`` and ``transformed`` are not of the same shape

    Yields:
        :class:`pandas.DataFrame`:
        Preview dataframe for each transformer in ``column_transformer.transformers_``.
            Dataframe has twice as columns as ``original`` and ``transformed``, i.e.
            ``df.shape == (original.shape[0], 2 * original.shape[1])``
    """
    # extract kwargs
    n_samples = kwargs.get('n_samples', 1)

    # just aliases for shorter lines
    ct = column_transformer

    # set rng
    if isinstance(random_state, int):
        random_state = np.random.default_rng(random_state)

    # generate sample indices
    sample_indices = random_state.choice(
        original.shape[0],
        size=n_samples,
        replace=False
    )
    sample_indices = sample_indices.reshape(-1, 1)  # to broadcast properly

    # loop through each transform (over subset of columns) and preview it
    for idx, k in enumerate(ct.output_indices_):
        # 'remainder' is not transformed, so end of the loop
        if k == 'remainder':
            return None

        # get indices of the transformed columns
        transformed_columns_slice: Union[list, slice] = ct.output_indices_[k]
        if isinstance(transformed_columns_slice, slice):
            transformed_columns_range = range(transformed_columns_slice.stop)
            transformed_columns_range = transformed_columns_range[transformed_columns_slice]
            transformed_columns_indices = list(transformed_columns_range)
        else:
            transformed_columns_indices = transformed_columns_slice
        # get indices of the original columns
        columns_indices = ct._columns[idx]
        # get names of the original columns
        columns_indices_names = df.columns.values[columns_indices]

        # preview transformed and original data side by side
        if not isinstance(ct.transformers[idx][1], OneHotEncoder):

            # compare the values of the transformed and the original columns
            original_sample = original[
                sample_indices,
                columns_indices
            ]
            transformed_sample = transformed[
                sample_indices,
                transformed_columns_indices
            ]
            # fix shapes to be 2d
            original_sample = original_sample.reshape(
                sample_indices.shape[0],
                columns_indices.__len__()
            )
            transformed_sample = transformed_sample.reshape(
                sample_indices.shape[0],
                columns_indices.__len__()
            )
            # create a dataframe with the original and transformed columns side by side
            sample = np.empty(
                shape=(original_sample.shape[0], original_sample.shape[1] * 2)
            )
            sample[:, ::2] = original_sample
            sample[:, 1::2] = transformed_sample
            preview_cols: List[str] = []
            [preview_cols.extend([f'{c}_og', f'{c}_tf'])  # type: ignore
             for c in columns_indices_names]
            preview_df = pd.DataFrame(sample, columns=preview_cols)
            # yield the previews
            if n_samples == 1:
                # just better visuals for single sample
                yield preview_df.T
            else:
                yield preview_df

        # show info about onehot encoder changes
        elif isinstance(ct.transformers[idx][1], OneHotEncoder):
            count_uniques = df.iloc[:, columns_indices].nunique().sum()
            logger.info(f'For "{ct.transformers[idx][0]}" transformer: ')
            logger.info(f'{len(columns_indices)} columns are affected. ')
            logger.info(
                f'On selected columns, {count_uniques} unique values exist. '
                f'It is expected to have {count_uniques - len(columns_indices)}'
                f' new columns and '
                f'{len(transformed_columns_indices) - len(columns_indices)}'
                f' columns are newly produced.\n'
            )
