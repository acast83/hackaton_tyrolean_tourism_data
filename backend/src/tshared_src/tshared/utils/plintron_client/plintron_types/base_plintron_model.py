from pydantic import BaseModel


__all__ = [
    "BasePlintronModel",
]


class BasePlintronModel(BaseModel):
    class Config:
        allow_population_by_field_name = True
        alias_generator = str.upper
        validate_all = True
        # arbitrary_types_allowed = True
