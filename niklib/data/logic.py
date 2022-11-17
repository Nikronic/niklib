__all__ = [
    'Logics', 'ExampleLogics'
]

# core
from functools import reduce
import pandas as pd
import numpy as np
# helpers
from typing import Callable, cast


class Logics:
    """Applies logics on different type of data resulting in summarized, expanded, or transformed data

    Methods here are implemented in the way that can be used as ``Pandas.agg_`` function
    over :class:`pandas.Series` using ``functools.reduce_``.

    Note: 
        This is constructed based on domain knowledge hence is designed 
        for a specific purpose based on application.

        For demonstration purposes, see following methods of this class:

            - :meth:`count_previous_residency_country`
            - :meth:`count_rel`
            - :meth:`count_foreign_family_resident`

        These methods has be implemented by their superclass. See:
        
            - :meth:`ExampleLogics.count_previous_residency_country`
            - :meth:`ExampleLogics.count_rel`
            - :meth:`ExampleLogics.count_foreign_family_resident`


    .. _Pandas.agg: https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.Series.agg.html
    .. _functools.reduce: https://docs.python.org/3/library/functools.html#functools.reduce
    """

    def __init__(self, dataframe: pd.DataFrame = None) -> None:
        """Init class by setting dataframe globally

        Args:
            dataframe (:class:`pandas.DataFrame`, optional): The dataframe that functions of this class 
                will be user over its series, i.e. ``Logics.*(series)``. Defaults to None.
        """
        self.df = dataframe

    def __check_df(self, func: str) -> None:
        """Checks that :attr:`df` is initialized when function with the name ``func`` is being called

        Args:
            func (str): The name of the function that operates over :attr:`df`

        Raises:
            TypeError: If :attr:`df` is not initialized
        """
        if self.df is None:
            raise TypeError(
                f'`df` attribute cannot be `None` when using "{func}".')

    def reset_dataframe(self, dataframe: pd.DataFrame) -> None:
        """Takes a new dataframe and replaces the old one

        Note:
            This should be used when the dataframe is modified outside of functions 
            provided in this class. E.g.::

                my_df: pd.DataFrame = ...
                logics = Logics(dataframe=my_df)
                my_df = third_party_tools(my_df)
                # now update df in logics
                logics.reset_dataframe(dataframe=my_df)

        Args:
            dataframe (:class:`pandas.DataFrame`): The new dataframe
        """
        self.df = dataframe

    def add_agg_column(
        self,
        aggregator: Callable,
        agg_column_name: str,
        columns: list
    ) -> pd.DataFrame:
        """Aggregate columns and adds it to the original dataframe using an aggregator function

        Args:
            aggregator (Callable): A function that takes multiple columns of a
                series and reduces it
            agg_column_name (str): The name of new aggregated column
            columns (list): Name of columns to be aggregated (i.e. input to ``aggregator``)

        Note:
            Although this function updated the dataframe the class initialized with *inplace*,
            but user must update the main dataframe outside of this class to make sure he/she
            can use it via different tools. Simply put::

                my_df: pd.DataFrame = ...
                logics = Logics(dataframe=my_df)
                my_df = logics.add_agg_column(...)
                my_df = third_party_tools(my_df)
                # now update df in logics
                logics.reset_dataframe(dataframe=my_df)
                # aggregate again...
                my_df = logics.add_agg_column(...)

        Returns:
            :class:`pandas.DataFrame`: Updated dataframe that contains aggregated data
        """
        # check self.df is initialized
        self.__check_df(func=self.add_agg_column.__name__)
        self.df = cast(pd.DataFrame, self.df)
        # aggregate
        self.df[agg_column_name] = self.df[columns].agg(aggregator, axis=1)
        self.df = self.df.rename(
            columns={aggregator.__name__: agg_column_name})
        # return updated dataframe to be used outside of this class
        return self.df

    def count_previous_residency_country(self, series: pd.Series) -> int:
        """Counts the number of previous country of resident

        Args:
            series (:class:`pandas.Series`): Pandas Series to be processed

        Returns:
            int: Result of counting
        """
        raise NotImplementedError

    def count_rel(self, series: pd.Series) -> int:
        """Counts the number of items for the given relationship

        Args:
            series (:class:`pandas.Series`): Pandas Series to be processed

        Returns:
            int: Result of counting
        """
        raise NotImplementedError

    def count_foreign_family_resident(self, series: pd.Series) -> int:
        """Counts the number of family members that are living in a foreign country

        Args:
            series (:class:`pandas.Series`): Pandas Series to be processed

        Returns:
            int: Result of counting
        """

        raise NotImplementedError


class ExampleLogics(Logics):
    """
    Customize and extend logics defined in :class:`Logics` for an Example (Canada) dataset

    """

    def __init__(self, dataframe: pd.DataFrame = None) -> None:
        super().__init__(dataframe)

    def count_previous_residency_country(self, series: pd.Series) -> int:
        """Counts the number of previous residency by counting non-zero periods of residency

        When ``*.Period == 0``, then we can say that the person has no residency.
        This way one just needs to count non-zero periods.

        Args:
            series (:class:`pandas.Series`): Pandas Series to be processed containing
                residency periods

        Returns:
            int: Result of counting
        """

        def counter(x, y): return np.sum(np.isin([x, y], [0]))
        return reduce(lambda x, y: 2 - counter(x, y), series)

    def count_rel(self, series: pd.Series) -> int:
        """Counts the number of people for the given relationship, e.g. siblings.

        Args:
            series (:class:`pandas.Series`): Pandas Series to be processed 

        Returns:
            int: Result of counting
        """

        def counter(y): return np.sum(y != 0.)
        return reduce(lambda x, y: x + counter(y), series, 0)

    def count_foreign_family_resident(self, series: pd.Series) -> int:
        """Counts the number of family members that are long distance resident

        This is being done by only checking the literal value ``'foreign'`` in the
        ``'*Addr'`` columns (address columns).

        Args:
            series (:class:`pandas.Series`): Pandas Series to be processed containing 
                the residency state/province in string. In practice, 
                any string different from applicant's province will be counted
                as difference.

        Examples:
            >>> import pandas as pd
            >>> from niklib.data.logic import CanadaLogics
            >>> f = CanadaLogics().count_foreign_family_resident
            >>> s = pd.Series(['alborz', 'alborz', 'alborz', None, 'foreign', None, 'gilan', 'isfahan', None])
            >>> f(s)
            1
            >>> s1 = pd.Series(['foreign', 'foreign', 'alborz', 'fars'])
            >>> f(s1)
            2
            >>> s2 = pd.Series([None, None, 'alborz', 'fars'])
            >>> f(s2)
            0

        Returns:
            int: Result of counting
        """

        self.df = cast(pd.DataFrame, self.df)  # for mypy only

        def counter(y): return np.sum(
            np.isin([y], ['foreign']))  # type: ignore
        return reduce(lambda x, y: x + counter(y), series, 0)  # type: ignore
