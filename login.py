import requests
import lxml.html


def login(workspace_name, email, password):
    """
    slackにログインしてCookieを適用したセッションを取得する
    """
    slack_url = "https://%s.slack.com" % workspace_name
    crumb_token = _parse_crumb(slack_url)
    param = _create_param(email, password, crumb_token)
    session = requests.Session()
    res = session.post(slack_url, data=param, allow_redirects=False)
    session.headers = {"Cookie": res.cookies.get("d")}
    return session, slack_url


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
    html = requests.get(slack_url).text
    root = lxml.html.fromstring(html)
    crumb_input = root.cssselect('#signin_form > input[name="crumb"]')
    return crumb_input[0].value


if __name__ == '__main__':
    print(login("", "", ""))
