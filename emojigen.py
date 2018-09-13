import requests


def fetch_emoji(url: str):
    res = requests.get(url)
    return res.content


def create_emoji_url(text: str, back_color: str, color: str, font: str, public_flg: bool, size_fixed: bool, stretch: bool):
    return "https://emoji-gen.ninja/emoji?%s" % _create_param(
        text, back_color, color, font, public_flg, size_fixed, stretch)


def _create_param(text: str, back_color: str, color: str, font: str, public_flg: bool, size_fixed: bool, stretch: bool):
    return "text=%s" % text + ("&back_color=%s&color=%s&font=%s&public_flg=%s&size_fixed=%s&stretch=%s"
                               % (back_color, color, font, public_flg, size_fixed, stretch)).lower()  # bool値の頭文字が大文字なので全部小文字にする


if __name__ == '__main__':
    with open("emoji.png", "wb") as f:
        data = fetch_emoji(create_emoji_url("てすとえもじうひひひひひひひ",
                                            back_color="FFFFFF00",
                                            color="EC71A1FF",
                                            font="notosans-mono-bold",
                                            public_flg=False,
                                            size_fixed=False,
                                            stretch=True
                                            ))
        f.write(data)
