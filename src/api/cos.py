# -*- coding=utf-8
import os
from typing import Generator
from qcloud_cos import CosConfig
from qcloud_cos import CosS3Client
import sys
import logging

if __name__ == "__main__":
    sys.path.append(os.getcwd() + "/src")
from api.models import CosFileItem
from config import get_settings

settings = get_settings()

# 正常情况日志级别使用 INFO，需要定位时可以修改为 DEBUG，此时 SDK 会打印和服务端的通信信息
logging.basicConfig(level=logging.WARN, stream=sys.stdout)

config = CosConfig(
    Region=settings.cos_region,
    SecretId=settings.cos_secret_id,
    SecretKey=settings.cos_secret_key,
)
client = CosS3Client(config)


def upload_file(file_path: str, cos_path: str):
    """上传文件

    Args:
        file_path (str): 本地文件地址
        cos_path (str): 对象存储文件地址

    Returns:
        dict: cos返回的原始结果
    """
    res = client.upload_file(
        Bucket=settings.cos_bucket,
        LocalFilePath=file_path,
        Key=cos_path,
        PartSize=1,
        MAXThread=10,
        EnableMD5=False,
    )
    return res


def get_file(cos_path: str, file_path: str | None = None):
    """下载文件

    Args:
        cos_path (str): 对象存储地址
        file_path (str | None, optional): 文件保存地址，不设置返回文件流，否则返回True. Defaults to None.

    Returns:
        bool | bytes: 返回状态或文件流
    """
    response = client.get_object(Bucket=settings.cos_bucket, Key=cos_path)
    if file_path:
        response["Body"].get_stream_to_file(file_path)
        return True
    else:
        fp = response['Body'].get_raw_stream()
        fpb: bytes = fp.read()
        return fpb


def get_file_list(cos_path: str) -> list[CosFileItem]:
    """获取文件列表

    单次调用只能查询1000个对象

    Args:
        cos_path (str): 文件夹地址

    Returns:
        list[CosFileItem]: 文件列表
    """
    res = client.list_objects(Bucket=settings.cos_bucket, Prefix=cos_path)
    lst = []
    for item in res.get("Contents", []):
        lst.append(CosFileItem(**item, isFile=not item.get("Key").endswith("/")))
    return lst


def get_file_list_v2(cos_path: str) -> Generator[CosFileItem, None, None]:
    """获取文件列表(迭代器版本，可以获取完整列表)

    Args:
        cos_path (str): 对象存储地址

    Yields:
        CosFileItem: 文件信息
    """
    marker = ""
    while True:
        res = client.list_objects(
            Bucket=settings.cos_bucket, Prefix=cos_path, Marker=marker
        )
        for item in res.get("Contents", []):
            yield CosFileItem(**item, isFile=not item.get("Key").endswith("/"))
        if res["IsTruncated"] == "false":
            break
        marker = res["NextMarker"]

