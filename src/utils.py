import hashlib
from typing import Any, Optional
from fastapi import Response
from fastapi.responses import JSONResponse
import orjson
from pydantic import BaseModel


class Res(BaseModel):
    detail: Optional[str] = None
    data: Optional[Any] = None
    total: Optional[int] = None
    code: int = 200


def return_resp(data, total, detail, code):
    c = Res(detail=detail, data=data, total=total, code=code).model_dump()
    if total is None:
        del c["total"]
    if c["data"] is None:
        del c["data"]

    res = Response(
        content=orjson.dumps(c),
        status_code=code,
        headers={"Content-Type": "application/json"},
    )
    return res


def resp_succ(
    data: Any = None, total: int | None = None, detail: str = "SUCCESS", code=200
):
    return return_resp(data=data, total=total, detail=detail, code=code)


def resp_err(
    data: Any = None, total: int | None = None, detail: str = "BAD REQUEST", code=500
):
    return return_resp(data=data, total=total, detail=detail, code=code)


def encrypt_md5(data_string, salt="0123456789ABCDEF...uygt6987"):
    """
    对字符串进行 MD5 加密
    :param data_string: 需要加密的字符串
    :param salt: 盐
    :return: 加密后的字符串
    """
    obj = hashlib.md5(salt.encode("utf-8"))
    obj.update(data_string.encode("utf-8"))
    return obj.hexdigest()
