import requests
import lxml.html
import re

from login import login

URL_SLACK = "https://{workspace}.slack.com"
URL_ADD = "{workspace_url}/api/emoji.add"
URL_REMOVE = "{workspace_url}/api/emoji.remove"
URL_CUSTOMIZE = "{workspace_url}/customize/emoji"
API_TOKEN_REGEX = r"api_token: \"(.*)\","


def check_login(workspace_name: str, session):
    """
    ログインしているかチェックする
    URL_CUSTOMIZEを見て、リダイレクトされたら未ログイン状態と判定する
    """
    slack_url = URL_SLACK.format(workspace=workspace_name)
    customize_url = URL_CUSTOMIZE.format(workspace_url=slack_url)
    res = session.get(customize_url, allow_redirects=False)

    return res.status_code == 200


def post_emoji(workspace_name: str, session, emoji_name: str, file_binary: bytes):
    slack_url = URL_SLACK.format(workspace=workspace_name)
    api_key = _parse_api_key(
        session, URL_CUSTOMIZE.format(workspace_url=slack_url))

    param = _create_param(api_key, emoji_name)
    file = {"image": file_binary}
    res = session.post(URL_ADD.format(workspace_url=slack_url),
                       data=param, files=file, allow_redirects=False)

    return res


def remove_emoji(workspace_name: str, session, emoji_name: str):
    slack_url = URL_SLACK.format(workspace=workspace_name)
    api_key = _parse_api_key(
        session, URL_CUSTOMIZE.format(workspace_url=slack_url))

    param = _create_param(api_key, emoji_name)

    res = session.post(URL_REMOVE.format(workspace_url=slack_url),
                       data=param, allow_redirects=False)

    return res


def _parse_api_key(session, customize_url):
    res = session.get(customize_url)
    root = lxml.html.fromstring(res.text)
    scripts = root.cssselect("script")
    for script in scripts:
        if script.text is not None:
            for line in script.text.splitlines():
                if 'api_token' in line:
                    # https://{ワークスペース}.slack.com/customize/emoji
                    # ここで F12 開いてconsoleに次のコード打ち込むとよく分かる
                    # Array.from(document.querySelectorAll("script")).map(v => v.innerText.split("\n")).reduce((b, c) => b.concat(c), []).filter(line => line.indexOf("api_token") >= 0)[0].trim()
                    return re.match(API_TOKEN_REGEX, line.strip()).group(1)

    raise Exception(
        'api_token not found. response status={}'.format(res.status_code))


def _create_param(api_key, name):
    return {
        "mode": "data",
        "name": name,
        "token": api_key
    }


def main():
    workspace_name = ""
    session = login(workspace_name=workspace_name,
                    email="",
                    password="")
    print(post_emoji(
        workspace_name=workspace_name,
        session=session,
        emoji_name="",
        file_binary=open("", "rb")).json())


if __name__ == '__main__':
    main()
