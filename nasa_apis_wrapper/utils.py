from pydantic import BaseModel


def obj_dict(obj: BaseModel) -> dict:
    """Converts a Pydantic model into a query-params dict, excluding None fields."""
    return obj.model_dump(exclude_none=True)
