import requests

url = "https://api.clickup.com/api/v2"


def get_user(token: str):
    """Get user information from ClickUp API

    example:
    {
        "user": {
            "id": 114111466,
            "username": "Byron",
            "email": "towardmirror@icloud.com",
            "color": "",
            "profilePicture": null,
            "initials": "B",
            "week_start_day": null,
            "global_font_support": true,
            "timezone": "Asia/Shanghai"
        }
    }
    """
    headers = {
        "Authorization": f"Bearer {token}",
    }

    response = requests.get(url + "/user", headers=headers)
    if response.status_code != 200:
        raise Exception("Failed to get user information")
    return response.json()["user"]
