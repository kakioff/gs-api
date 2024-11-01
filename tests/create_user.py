import hashlib
import time
import random

while True:
    hash_time = hashlib.sha256(str(time.time_ns()).encode("utf-8")).hexdigest()
    uid = hash_time[:8]
    # 随机位置插入一个下划线
    x_index = random.randint(1, 7)
    uid = uid[:x_index] + "_" + uid[x_index:]
    print(uid)
    time.sleep(1)
