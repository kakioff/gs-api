import hashlib
import random
import time
from typing import Any, Optional, Union
from fastapi import Response
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


#  非对称加密
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding


class RSAEncrypt:
    def __init__(self):
        """
        初始化 RSA 加密
        """
        rsa_dir = "static/rsa"
        # 从 PEM 格式的 公钥 文件中读取数据
        with open(f"{rsa_dir}/public.pem", "rb") as f:
            self.pub_key = serialization.load_pem_public_key(f.read())

        with open(f"{rsa_dir}/private.pem", "rb") as f:
            self.priv_key = serialization.load_pem_private_key(f.read(), password=None)

    def encrypt(self, data: str) -> Union[str, None]:
        """对数据进行加密

        Args:
            data (str): 要加密的数据

        Returns:
            str: 加密后的数据
        """
        ciphertext = self.pub_key.encrypt(  # type: ignore
            data.encode(),
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA1()),
                algorithm=hashes.SHA1(),
                label=None,
            ),
        )
        if not ciphertext:
            return None
        return ciphertext.hex()

    def decrypt(self, data: str) -> Union[str, None]:
        """对数据进行解密

        Args:
            data (str): 要解密的数据

        Returns:
            Union[str, None]: 解密后的数据
        """
        data_bytes = bytes.fromhex(data)
        plaintext = self.priv_key.decrypt(  # type: ignore
            data_bytes,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA1()),
                algorithm=hashes.SHA1(),
                label=None,
            ),
        )
        return plaintext.decode()


def get_file_md5(file) -> str:
    """
    获取文件的 MD5 值
    :param file: 文件对象
    :return: 文件的 MD5 值
    """
    m = hashlib.md5()
    while True:
        data = file.read(4096)
        if not data:
            break
        m.update(data)
    return m.hexdigest()


def generate_uid(salt=""):
    hash_time = hashlib.sha256((str(time.time_ns()) + salt).encode("utf-8")).hexdigest()
    uid = hash_time[:8]
    # 随机位置插入一个下划线
    x_index = random.randint(1, 7)
    uid = uid[:x_index] + "_" + uid[x_index:]
    return uid
