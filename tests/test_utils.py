import datetime

from pydantic import BaseModel

from nasa_apis_wrapper import Utils


class TestObject(BaseModel):
    parameter_str: str


class TestUtils:
    def test_obj_dict(self) -> None:
        result = Utils.obj_dict(TestObject(parameter_str="test"))
        assert result

    def test_obj_dict_with_date(self) -> None:
        result = Utils.obj_dict(datetime.date(2022, 3, 27))
        assert result
