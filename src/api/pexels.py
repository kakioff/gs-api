import requests
import time

from database import redis
from config import get_settings

setitngs = get_settings()
# https://www.pexels.com/zh-cn/api/documentation/

def _request(url, params=None):
    headers = {
        "Authorization": "9dRdBqWwkzqWzNT0q0MPxO6Qh928ZkcgCgTZHB4kYgJxcZkXThD6tEHK",
    }
    url = f"https://api.pexels.com/v1/{url}"
    res = requests.get(url, headers=headers, params=params)
    limit = res.headers.get("X-Ratelimit-Limit")
    remaining = res.headers.get("X-Ratelimit-Remaining")
    redis.hset("pexels", "limit", limit)
    redis.hset("pexels", "remaining", remaining)
    redis.hset("pexels", "time", str(int(time.time())))
    
    return res.json()


if __name__ == "__main__":
    res = _request("search", {"query": "avatar"})
    print(res)
