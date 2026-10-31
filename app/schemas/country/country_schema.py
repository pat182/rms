from ...core.base_schema import BaseSchema

from pydantic import ConfigDict

class CountryData(BaseSchema):
    model_config = ConfigDict(from_attributes=True)
    id : int
    country_name : str
    country_code : str
    phone_code : str