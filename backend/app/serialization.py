from typing import Any

from fastapi.encoders import jsonable_encoder


def json_safe(value: Any) -> Any:
    return jsonable_encoder(value)
