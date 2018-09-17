import requests
import lxml.html
import re

from login import login

URL_SLACK = "https://{workspace}.slack.com"
URL_ADD = "{workspace}/api/emoji.add"
URL_REMOVE = "{workspace}/api/emoji.remove"
URL_CUSTOMIZE = "{workspace}/customize/emoji"
API_TOKEN_REGEX = r"api_token: \"(.*)\","


def post_emoji(workspace_name, session, emoji_name, file_binary):
    slack_url = URL_SLACK.format(workspace=workspace_name)
    api_key = _parse_api_key(
        session, URL_CUSTOMIZE.format(workspace=slack_url))

    param = _create_param(api_key, emoji_name)
    file = {"image": file_binary}
    res = session.post(URL_ADD.format(workspace=slack_url),
                       data=param, files=file, allow_redirects=False)

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
