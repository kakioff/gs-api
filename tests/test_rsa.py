import logging
from src import utils


def test_rsa():
    rsa = utils.RSAEncrypt()
    data = "123123123"
    en = rsa.encrypt(data)
    assert en is not None, "RSA加密失败"
    logging.debug(en)
    de = rsa.decrypt(en)
    assert de is not None, "RSA解密失败"
    logging.debug(de)
    assert data == de, "RSA加密解密失败"
