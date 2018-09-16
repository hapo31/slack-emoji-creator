import requests
import json


def post_json(url, data, headers={}):
    """
    JSONをPOSTする
    """
    headers["Content-Type"] = "application/json; charset=UTF-8"
    json_str = json.dumps(data)

    return requests.post(url, data=json_str, headers=headers)
