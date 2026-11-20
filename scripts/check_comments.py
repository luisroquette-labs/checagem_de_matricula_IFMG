from html.parser import HTMLParser
from pathlib import Path
import json
import subprocess
import sys
import tokenize
from io import BytesIO
from xml.parsers import expat


def code_comments(source: str) -> list[int]:
    lines = []
    line = 1
    quote = ""
    index = 0
    while index < len(source):
        char = source[index]
        if char == "\n":
            line += 1
        if quote:
            if char == "\\":
                index += 2
                continue
            if char == quote:
                quote = ""
        elif char in {'"', "'"}:
            quote = char
        elif source.startswith("/*", index):
            lines.append(line)
            end = source.find("*/", index + 2)
            next_index = len(source) if end < 0 else end + 2
            line += source[index:next_index].count("\n")
            index = next_index
            continue
        index += 1
    return lines


def js_comments(source: str) -> list[int]:
    checker = Path(__file__).with_name("check_js_comments.cjs")
    result = subprocess.check_output(["node", str(checker)], input=source.encode())
    return json.loads(result)


def yaml_comments(source: str) -> list[int]:
    checker = Path(__file__).with_name("check_yaml_comments.cjs")
    result = subprocess.check_output(["node", str(checker)], input=source.encode())
    return json.loads(result)


def shell_comments(source: str) -> list[int]:
    lines = []
    for number, line in enumerate(source.splitlines(), 1):
        if number == 1 and line.startswith("#!"):
            continue
        quote = ""
        index = 0
        while index < len(line):
            char = line[index]
            if char == "\\" and quote != "'":
                index += 2
                continue
            if char in {'"', "'"}:
                quote = "" if quote == char else char if not quote else quote
            elif char == "#" and not quote and (index == 0 or line[index - 1].isspace() or line[index - 1] in ";|&()"):
                lines.append(number)
                break
            index += 1
    return lines


class PageComments(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=False)
        self.language = ""
        self.lines = []

    def handle_starttag(self, tag, attrs):
        if tag in {"style", "script"}:
            self.language = tag

    def handle_endtag(self, tag):
        if tag == self.language:
            self.language = ""

    def handle_comment(self, data):
        self.lines.append(self.getpos()[0])

    def handle_data(self, data):
        if self.language:
            scanner = js_comments if self.language == "script" else code_comments
            self.lines.extend(self.getpos()[0] + line - 1 for line in scanner(data))


def file_comments(path: Path) -> list[int]:
    source = path.read_text()
    if path.suffix.lower() == ".svg":
        lines = []
        parser = expat.ParserCreate()
        parser.CommentHandler = lambda _: lines.append(parser.CurrentLineNumber)
        parser.Parse(source)
        return lines
    if path.suffix.lower() in {".js", ".cjs", ".mjs"}:
        return js_comments(source)
    if path.suffix.lower() == ".css":
        return code_comments(source)
    if path.suffix.lower() == ".py":
        return [token.start[0] for token in tokenize.tokenize(BytesIO(source.encode()).readline) if token.type == tokenize.COMMENT]
    if path.suffix.lower() in {".yml", ".yaml"}:
        return yaml_comments(source)
    if path.suffix.lower() == ".sh":
        return shell_comments(source)
    parser = PageComments()
    parser.feed(source)
    return parser.lines


def main() -> int:
    paths = subprocess.check_output(["git", "ls-files", "-z"]).decode().split("\0")
    suffixes = {".html", ".svg", ".js", ".cjs", ".mjs", ".css", ".py", ".yml", ".yaml", ".sh"}
    failures = [f"{path}:{line}" for path in paths if Path(path).suffix.lower() in suffixes for line in file_comments(Path(path))]
    if failures:
        print("Comments forbidden:\n" + "\n".join(failures), file=sys.stderr)
        return 1
    print("Comment ratchet: zero comments in tracked source and workflow files.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
