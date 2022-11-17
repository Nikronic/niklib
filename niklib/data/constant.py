__all__ = [
    'EXAMPLE_FINANCIAL_RATIOS', 'ExampleFillna', 'ExampleDocTypes', 'DATEUTIL_DEFAULT_DATETIME'

    # Data Enums shared all over the place
    'CustomNamingEnum', 'ExampleMarriageStatus', 'ExampleSex'
]

import datetime
from enum import Enum, auto
from types import DynamicClassAttribute
from typing import List


EXAMPLE_FINANCIAL_RATIOS = {
    # house related
    'rent2deposit': 100./3.,  # rule of thumb provided online
    'deposit2rent': 3./100.,
    'deposit2worth': 5.,      # rule of thumb provided online
    'worth2deposit': 1./5.,
    # company related
    'tax2income': 100./15.,  # 10% for small, 20% for larger, we use average 15% tax rate
    'income2tax': 15./100.,
    # a company worth 15x of its income for minimum: C[T/E]O suggestion
    'income2worth': 15.,
    'worth2income': 1./15.,
}
"""Ratios used to convert rent, deposit, and total worth to each other

Note:
    This is part of dictionaries containing factors in used in heuristic
    calculations using domain knowledge.

Note:
    Although this is created as an code example, values chosen here are
    from basic rule of thump and actually can be used if no other
    reliable information is available.

"""

DATEUTIL_DEFAULT_DATETIME = {
    'day': 18,  # no reason for this value (CluelessClown)
    'month': 6,  # no reason for this value (CluelessClown)
    'year': datetime.MINYEAR
}
"""A default date for the ``dateutil.parser.parse`` function when some part of date is not provided

Warning:
    Since I am using python's `dateutil` and `datetime` libraries for parsing these
    string (using `dateutil.parser`), if `month` and `day` are not provided, it uses
    *system date* which results in creating datasets that are run dependent and all
    tests would fail since new day, new date and the tracked datasets (e.g. using DVC)
    are returning the old dates.

    ``dateutil`` and ``datetime`` for obtaining *today* (i.e. ``datetime.datetime.now()``)
    call built in library ``time.time()`` which returns the system time
    which in our case WSL UNIX time - bash ``date`` command.
    This can be seen here: https://github.com/python/cpython/blob/3.10/Lib/datetime.py#L833-L836
    ```python
    def today(cls):
        "Construct a date from time.time()."
        t = _time.time()
        return cls.fromtimestamp(t)
    ```

"""

class CustomNamingEnum(Enum):
    """Extends base :class:`enum.Enum` to support custom naming for members

    Note:
        Class attribute :attr:`name` has been overridden to return the name
        of a marital status that matches with the dataset and not the ``Enum``
        naming convention of Python. For instance, ``COMMON_LAW`` -> ``common-law`` in
        case of Canada forms.

    Note:
        Developers should subclass this class and add their desired members in newly
        created classes. E.g. see :class:`MarriageStatus`

    Note:
        Classes that subclass this, for values of their members should use :class:`enum.auto`
        to demonstrate that chosen value is not domain-specific. Otherwise, any explicit
        value given to members should implicate a domain-specific (e.g. extracted from dataset)
        value. Values that are explicitly provided are the values used in original data. Hence,
        it should not be modified by any means as it is tied to dataset, transformation,
        and other domain-specific values. E.g. compare values in :class:`MarriageStatus`
        and :class:`SiblingRelation`.

    Note:
        If you need to customize naming specifically, you need to override
        :attr:`name` similar to what is done in this class. i.e.::

            @DynamicClassAttribute
            def name(self):
                _name = super(CustomNamingEnum, self).name
                _name: str = ...  # DO YOU THING
                self._name_ = _name
                return self._name_
    """

    @DynamicClassAttribute
    def name(self):
        _name = super(CustomNamingEnum, self).name
        _name: str = _name.lower()
        # convert FOO_BAR to foo-bar (dataset convention)
        _name = _name.replace('_', '-')
        self._name_ = _name
        return self._name_

    @classmethod
    def get_member_names(cls):
        _member_names_: List[str] = []
        for mem_name in cls._member_names_:
            _member_names_.append(cls._member_map_[mem_name].name)
        return _member_names_


class ExampleMarriageStatus(CustomNamingEnum):
    """States of marriage in (some specific) form

    Note:
        Values for the members are the values used in original forms. Hence,
        it should not be modified by any means as it is tied to dataset, transformation,
        and other domain-specific values.

    Note:
        These values have been chosen for demonstration purposes in this class and
        and do not carry any meaning or information (El No Sabe). But for real world,
        you must use meaningful ones.
    """

    COMMON_LAW = 69
    DIVORCED = 3
    SEPARATED = 4
    MARRIED = 0
    SINGLE = 7
    WIDOWED = 85
    UNKNOWN = 9


class ExampleDocTypes(CustomNamingEnum):
    """Contains all document types which can be used to customize ETL steps for each document type

    Members follow the ``<country_name>_<document_type>`` naming convention. The value 
    and its order are meaningless.
    """
    CANADA = auto()        # referring to all Canada docs in general
    CANADA_5257E = auto()  # application for visitor visa (temporary resident visa)
    CANADA_5645E = auto()  # Family information
    CANADA_LABEL = auto()  # containing labels


class ExampleFillna(CustomNamingEnum):
    """Values used to fill ``None`` s depending on the form structure

    Members follow the ``<field_name>_<form_name>`` naming convention. The value
    has been extracted by manually inspecting the documents. Hence, for each
    form, user must find and set this value manually.

    Note:
        We do not use any heuristics here, we just follow what form used and
        only add another option which should be used as ``None`` state; i.e. ``None``
        as a separate feature in categorical mode.
    """

    CHD_M_STATUS_5645E = 9


class ExampleSex(CustomNamingEnum):
    """Sex types in general

    Note:
        The values of enum members are not important, hence no explicit valuing is used

    Note:
        The name of the members has to be customized because of bad preprocessing
        (or in some cases, domain-specific knowledge), hence, :attr:`name` has
        been overridden.
    """

    FEMALE = auto()
    MALE = auto()

    @DynamicClassAttribute
    def name(self):
        _name = super(CustomNamingEnum, self).name
        # convert foobar to Foobar (i.e. Female, Male)
        _name: str = _name.lower().capitalize()
        self._name_ = _name
        return self._name_
