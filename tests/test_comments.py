import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from scripts.check_comments import code_comments, file_comments


class CommentLintTest(unittest.TestCase):
    def test_script_url_and_comment(self):
        self.assertEqual(code_comments('const url = "https://example.test";\n// remove', "script"), [2])

    def test_css_string_and_comment(self):
        self.assertEqual(code_comments('a::after{content:"/* literal */"} /* remove */', "style"), [1])

    def test_html_and_svg(self):
        with TemporaryDirectory() as directory:
            html = Path(directory) / "page.html"
            html.write_text('<p title="<!-- literal -->">Text</p>\n<!-- remove -->')
            svg = Path(directory) / "image.svg"
            svg.write_text('<svg><![CDATA[<!-- literal -->]]><!-- remove --></svg>')
            self.assertEqual(file_comments(html), [2])
            self.assertEqual(file_comments(svg), [1])


if __name__ == "__main__":
    unittest.main()
