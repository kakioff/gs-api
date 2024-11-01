import requests

url = "https://api.github.com"


def get_user(token):
    """
    example:
        {
        "login": "kakioff",
        "id": 64448740,
        "node_id": "MDQ6VXNlcjY0NDQ4NzQw",
        "avatar_url": "https://avatars.githubusercontent.com/u/64448740?v=4",
        "gravatar_id": "",
        "url": "https://api.github.com/users/kakioff",
        "html_url": "https://github.com/kakioff",
        "followers_url": "https://api.github.com/users/kakioff/followers",
        "following_url": "https://api.github.com/users/kakioff/following{/other_user}",
        "gists_url": "https://api.github.com/users/kakioff/gists{/gist_id}",
        "starred_url": "https://api.github.com/users/kakioff/starred{/owner}{/repo}",
        "subscriptions_url": "https://api.github.com/users/kakioff/subscriptions",
        "organizations_url": "https://api.github.com/users/kakioff/orgs",
        "repos_url": "https://api.github.com/users/kakioff/repos",
        "events_url": "https://api.github.com/users/kakioff/events{/privacy}",
        "received_events_url": "https://api.github.com/users/kakioff/received_events",
        "type": "User",
        "user_view_type": "private",
        "site_admin": false,
        "name": "byron",
        "company": null,
        "blog": "",
        "location": null,
        "email": "1636700244@qq.com",
        "hireable": null,
        "bio": null,
        "twitter_username": null,
        "notification_email": "1636700244@qq.com",
        "public_repos": 10,
        "public_gists": 1,
        "followers": 1,
        "following": 2,
        "created_at": "2020-04-28T01:15:51Z",
        "updated_at": "2024-10-18T12:03:02Z",
        "private_gists": 2,
        "total_private_repos": 3,
        "owned_private_repos": 3,
        "disk_usage": 15678,
        "collaborators": 0,
        "two_factor_authentication": true,
        "plan": {
            "name": "free",
            "space": 976562499,
            "collaborators": 0,
            "private_repos": 10000
        }
    }
    """
    headers = {
        "User-Agent": "Apifox/1.0.0 (https://apifox.com)",
        "Authorization": f"Bearer {token}",
    }

    response = requests.request("GET", url + "/user", headers=headers)
    if response.status_code != 200:
        raise Exception("Github API Error")
    return response.json()
