import datetime
from typing import Optional

from pydantic import BaseModel

from nasa_apis_wrapper import Utils


class SampleModel(BaseModel):
    required_field: str
    optional_field: Optional[str] = None


class TestUtils:
    def test_obj_dict_returns_dict(self) -> None:
        result = Utils.obj_dict(SampleModel(required_field="test"))
        assert result == {"required_field": "test"}

    def test_obj_dict_excludes_none_fields(self) -> None:
        result = Utils.obj_dict(SampleModel(required_field="test", optional_field=None))
        assert "optional_field" not in result

    def test_obj_dict_with_date_field(self) -> None:
        class DateModel(BaseModel):
            date: datetime.date
            optional_date: Optional[datetime.date] = None

        result = Utils.obj_dict(DateModel(date=datetime.date(2022, 3, 27)))
        assert result == {"date": datetime.date(2022, 3, 27)}
        assert "optional_date" not in result
