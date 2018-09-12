import requests


def login(workspace_name, email, password):
    """
    slackにログインしてCookieのセッションIDを取得する
    """
    slack_url = "https://%s.slack.com" % workspace_name
    crumb_token = _parse_crumb(slack_url)
    param = _create_param(email, password, crumb_token)
    res = requests.post(slack_url, data=param)

    return res.headers["set-cookie"]


def _create_param(email, password, crumb):
    return {
        "signin": 1,
        "redir": "",
        "has_remember": 1,
        "crumb": crumb,
        "email": email,
        "password": password,
        "remember": "on"
    }


def _parse_crumb(slack_url):
    """
    crumb tokenをパースする
    """
    import lxml.html
    html = requests.get(slack_url).text
    root = lxml.html.fromstring(html)
    crumb_input = root.cssselect('#signin_form > input[name="crumb"]')
    return crumb_input[0].value


if __name__ == '__main__':
    print(login("zuttomosystem", "", ""))
