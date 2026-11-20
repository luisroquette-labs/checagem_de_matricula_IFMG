import unittest
import subprocess
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

from scripts.check_comments import code_comments, file_comments, js_comments


class CommentLintTest(unittest.TestCase):
    def test_script_url_and_comment(self):
        self.assertEqual(js_comments('const url = "https://example.test";\n// remove'), [2])

    def test_script_regex_and_template(self):
        self.assertEqual(js_comments("const r = /[//]/; const x = /'/; const y = `${1 /* remove */}`;"), [1])

    def test_css_string_and_comment(self):
        self.assertEqual(code_comments('a::after{content:"/* literal */"} /* remove */'), [1])

    def test_standalone_files(self):
        with TemporaryDirectory() as directory:
            js = Path(directory) / "file.js"
            js.write_text("const x = 1; // remove")
            css = Path(directory) / "style.css"
            css.write_text("a { color: red /* remove */ }")
            self.assertEqual(file_comments(js), [1])
            self.assertEqual(file_comments(css), [1])

    def test_tracked_standalone_file(self):
        with TemporaryDirectory() as directory:
            (Path(directory) / "file.js").write_text("const x = 1; // remove")
            subprocess.run(["git", "init", "-q"], cwd=directory, check=True)
            subprocess.run(["git", "add", "file.js"], cwd=directory, check=True)
            checker = Path(__file__).resolve().parents[1] / "scripts/check_comments.py"
            result = subprocess.run([sys.executable, str(checker)], cwd=directory, capture_output=True)
            self.assertEqual(result.returncode, 1)
            self.assertIn(b"file.js:1", result.stderr)

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
