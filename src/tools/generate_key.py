from Crypto.PublicKey import RSA


# 生成一对长度为 2048 位的 RSA 秘钥对, 使用默认的随机数生成函数,
# 也可以手动指定一个随机数生成函数: randfunc=Crypto.Random.new().read
rsa_key = RSA.generate(2048)

# 导出公钥, "PEM" 表示使用文本编码输出, 返回的是 bytes 类型, 格式如下:
# b'-----BEGIN PUBLIC KEY-----\n{Base64Text}\n-----END PUBLIC KEY-----'
# 输出格式可选: "PEM", "DER", "OpenSSH"
pub_key = rsa_key.publickey().export_key("PEM")

# 导出私钥, "PEM" 表示使用文本编码输出, 返回的是 bytes 类型, 格式如下:
# b'-----BEGIN RSA PRIVATE KEY-----\n{Base64Text}\n-----END RSA PRIVATE KEY-----'
pri_key = rsa_key.export_key("PEM")

rsa_dir = "static/rsa"

# 创建目录
import os
os.makedirs(rsa_dir, exist_ok=True)

# 把公钥和私钥保存到文件
with open(f"{rsa_dir}/public.pem", "wb") as pub_fp:
    pub_fp.write(pub_key)

with open(f"{rsa_dir}/private.pem", "wb") as pri_fp:
    pri_fp.write(pri_key)
