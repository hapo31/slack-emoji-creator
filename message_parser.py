import re


class CommandParser():
    def __init__(self, message: str):
        target, method, option_query = self._lexer(message)
        self.target = target
        self.type = method[0] if len(method) == 1 else ""

        self.options = self._option_parser(option_query)

    def _lexer(self, message) -> (str, list, list):
        tokens = message.split()
        print(tokens)
        if len(tokens) <= 0:
            return "error", [], []
        else:
            return tokens[0], tokens[1:2], tokens[2:]

    def _option_parser(self, option_query: list):
        """
        option_queryはGETパラメータのように＆区切りか、スペース区切りの文字列を想定
        """
        options = {}
        print(option_query)
        # option_query は range 構文で切り取っているので、リストとして渡されている想定
        if len(option_query) > 0:
            # 一旦結合したあと、&かスペースか,でsplitする
            option_tokens = re.split(r"[&\s,]", " ".join(option_query))
            print(option_tokens)
            for token in option_tokens:
                # 各オプションの値は=で繋がっていることとする
                option_list = token.split("=")
                print(option_list)
                if len(option_list) == 2:
                    prop, value = option_list
                    options[prop.strip()] = value.strip()

        return options
