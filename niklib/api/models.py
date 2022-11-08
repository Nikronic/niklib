__all__ = [
    'PayloadExample'
]

# core
import pydantic
from pydantic import validator
import json
# ours
from niklib.data.constant import (
    ExampleSex,
)
# helpers
from typing import Any


class BaseModel(pydantic.BaseModel):
    """Extension of :class:`pydantic.BaseModel` to parse ``File`` and ``Form`` data along side each other

    Note:
        All models has to be subclass this class. Note that validation can be done using
        pydantic's ``validate`` decorator. See examples for more info.
    
    Example:
        >>> class PredictionResponse(BaseModel):
        >>>     '''Response model for the prediction of machine learning model
        >>>        Note:
                    This is the final goal of the project from technical aspect
        >>>     '''
        >>> result: float
    
    Example:
        >>> class XaiResponse(BaseModel):
        >>>    '''XAI values for trained model
        >>>    Note:
        >>>     For more info about XAI and available methods, see :mod:`niklib.xai.shap`. 
        >>>    '''
        >>>    xai_overall_score: float
        >>>    xai_top_k: Dict[str, float]


    Reference:
        - https://stackoverflow.com/a/70640522/18971263
    """
    def __init__(__pydantic_self__, **data: Any) -> None:
        super().__init__(**data)

    @classmethod
    def __get_validators__(cls):
        yield cls._validate_from_json_string

    @classmethod
    def _validate_from_json_string(cls, value):
        if isinstance(value, str):
            return cls.validate(json.loads(value.encode()))
        return cls.validate(value)


class PayloadExample(BaseModel):
    """API payload provided by user

    Validation of API payload where it has a domain specific value or 
    has fixed data. In that case, it is expected that developer first 
    created an interface to have access to these fixed data or domain-specific
    knowledge as a validator function.

    ``sex`` is an example were it could be fixed, hence an :class:`enum.Enum`
    with fixed members has been defined in :class:`niklib.data.constant.Sex` that contains it.

    ``funds`` is a domain-specific knowledge that in this example, cannot be negative.
    or in some cases it could not surpass a specific value. For this, developer
    can add this manually here (not recommended) or creates an validator in where
    data actually has been first processed (e.g. :mod:`niklib.data.preprocessor`).

    TODO:
        Currently, for the second case where domain-specific knowledge is important,
        there has been no design pattern, and the manual way of handling validation
        has been used.


    Raises:
        ValueError: _description_
        ValueError: _description_
    """

    sex: str
    @validator('sex')
    def _sex(cls, value):
        if value not in ExampleSex.get_member_names():
            raise ValueError(f'"{value}" is not valid')
        return value

    funds: float = 8000.
    @validator('funds')
    def _funds(cls, value):
        if value <= 0.:
            raise ValueError('funds cannot be negative number.')
        return value

    class Config:
        orm_mode = True
