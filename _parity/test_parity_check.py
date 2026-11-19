"""Tests for the Parity check, exercised only through its CLI.

Run: python3 -m unittest discover -s _parity
Set PARITY_BASELINE to a Baseline directory to also run the full-site self-tests.
"""
import os
import shutil
import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path

SCRIPT = Path(__file__).with_name("parity_check.py")
BASELINE = os.environ.get(
    "PARITY_BASELINE",
    str(Path(__file__).resolve().parents[2] / "zola-baseline" / "site"),
)


def run(baseline, output, *args):
    p = subprocess.run(
        [sys.executable, str(SCRIPT), str(baseline), str(output), *args],
        capture_output=True, text=True,
    )
    return p.returncode, p.stdout + p.stderr


class Fixture(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.a = self.tmp / "a"
        self.b = self.tmp / "b"
        self.a.mkdir()
        self.b.mkdir()

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def write(self, side, rel, content):
        p = side / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(content, bytes):
            p.write_bytes(content)
        else:
            p.write_text(textwrap.dedent(content), encoding="utf-8")

    def pair(self, rel, a, b):
        self.write(self.a, rel, a)
        self.write(self.b, rel, b)
        return run(self.a, self.b)

    def assertClean(self, res):
        code, out = res
        self.assertEqual(code, 0, out)

    def assertDiffers(self, res, needle=None):
        code, out = res
        self.assertNotEqual(code, 0, out)
        if needle:
            self.assertIn(needle, out)


class HtmlTests(Fixture):
    def test_whitespace_attr_order_void_charrefs_quotes_comments_ignored(self):
        self.assertClean(self.pair(
            "x/index.html",
            '<html><body><p class="a" id=\'b\'>Caf&eacute; &amp; &#8220;x&#8221;<br/>y</p><!-- c --></body></html>',
            '<html>\n <body>\n  <p id="b" class="a">\n    Café &amp; “x”<br>y\n  </p>\n </body>\n</html>',
        ))

    def test_changed_word_reported_with_diff(self):
        self.assertDiffers(self.pair(
            "index.html", "<p>Hello world</p>", "<p>Hello there</p>"), "there")

    def test_whitespace_inside_pre_matters(self):
        self.assertDiffers(self.pair(
            "index.html", "<pre>a\n  b</pre>", "<pre>a\n b</pre>"))

    def test_kramdown_code_wrappers_normalised(self):
        self.assertClean(self.pair(
            "index.html",
            '<div class="language-plaintext highlighter-rouge"><div class="highlight">'
            '<pre class="highlight"><code>x = 1\n</code></pre></div></div>'
            '<p><code class="language-plaintext highlighter-rouge">y</code></p>',
            '<pre><code>x = 1\n</code></pre><p><code>y</code></p>',
        ))

    def test_json_ld_compared_as_json(self):
        self.assertClean(self.pair(
            "index.html",
            '<script type="application/ld+json">{"a":1,"b":[1,2]}</script>',
            '<script type="application/ld+json">\n{ "b": [1, 2],\n  "a": 1 }\n</script>',
        ))
        self.assertDiffers(self.pair(
            "index.html",
            '<script type="application/ld+json">{"a":1}</script>',
            '<script type="application/ld+json">{"a":2}</script>',
        ))

    def test_footer_year_ignored(self):
        self.assertClean(self.pair(
            "index.html",
            "<footer><span>&copy; 2026 Club</span></footer>",
            "<footer><span>© 2027 Club</span></footer>",
        ))


class OtherFormatTests(Fixture):
    def test_feed_normalised_xml_and_updated_ignored(self):
        self.assertClean(self.pair(
            "feed.xml",
            '<?xml version="1.0" encoding="utf-8"?><feed xmlns="http://www.w3.org/2005/Atom">'
            '<updated>2026-01-01T00:00:00+01:00</updated><entry><id>x</id></entry></feed>',
            '<?xml version="1.0" encoding="UTF-8"?>\n<feed xmlns="http://www.w3.org/2005/Atom">\n'
            '  <updated>2027-05-05T00:00:00+00:00</updated>\n  <entry>\n    <id>x</id>\n  </entry>\n</feed>\n',
        ))
        self.assertDiffers(self.pair(
            "feed.xml",
            '<feed xmlns="http://www.w3.org/2005/Atom"><entry><id>x</id></entry></feed>',
            '<feed xmlns="http://www.w3.org/2005/Atom"><entry><id>y</id></entry></feed>',
        ))

    def test_entry_updated_still_compared(self):
        self.assertDiffers(self.pair(
            "feed.xml",
            '<feed xmlns="http://www.w3.org/2005/Atom"><entry><updated>1</updated></entry></feed>',
            '<feed xmlns="http://www.w3.org/2005/Atom"><entry><updated>2</updated></entry></feed>',
        ))

    def test_css_minified_on_both_sides(self):
        self.assertClean(self.pair(
            "a.css", "a{color:red;margin:0}", "/* c */\na {\n  color: red;\n  margin: 0;\n}\n"))
        self.assertDiffers(self.pair("a.css", "a{color:red}", "a{color:blue}"))

    def test_other_files_byte_identical(self):
        self.assertClean(self.pair("x.bin", b"\x00\x01", b"\x00\x01"))
        self.assertDiffers(self.pair("robots.txt", "a\n", "a \n"))

    def test_pagefind_existence_only(self):
        self.write(self.a, "pagefind/pagefind.js", "old")
        self.write(self.b, "pagefind/other.js", "new")
        self.assertClean(run(self.a, self.b))
        shutil.rmtree(self.b / "pagefind")
        self.assertDiffers(run(self.a, self.b), "pagefind")

    def test_missing_and_extra_reported(self):
        self.write(self.a, "gone.txt", "x")
        self.write(self.b, "new.txt", "x")
        code, out = run(self.a, self.b)
        self.assertNotEqual(code, 0)
        self.assertIn("MISSING  gone.txt", out)
        self.assertIn("EXTRA    new.txt", out)


class KnownExceptionTests(Fixture):
    def setUp(self):
        super().setUp()
        # A static file: present at the root and copied byte-identically under /en/.
        for side in (self.a, self.b):
            self.write(side, "assets/s.css", "a{b:c}")
        self.write(self.a, "en/assets/s.css", "a{b:c}")

    def test_dropped_en_static_copy_is_known(self):
        code, out = run(self.a, self.b)
        self.assertEqual(code, 0, out)
        self.assertIn("KNOWN", out)

    def test_en_pages_may_reference_root_assets(self):
        self.assertClean(self.pair(
            "en/index.html",
            '<link href="/en/assets/s.css"><a href="/en/about/">x</a>',
            '<link href="/assets/s.css"><a href="/en/about/">x</a>',
        ))
        self.assertDiffers(self.pair(
            "en/index.html", '<a href="/en/about/">x</a>', '<a href="/about/">x</a>'))

    def test_sitemap_without_static_files(self):
        self.assertClean(self.pair(
            "sitemap.xml",
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
            '<url><loc>https://chombo.club/</loc></url>'
            '<url><loc>https://chombo.club/assets/s.css</loc></url></urlset>',
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
            '<url><loc>https://chombo.club/</loc></url></urlset>',
        ))

    def test_no_exceptions_flag_disables_them(self):
        code, out = run(self.a, self.b, "--no-exceptions")
        self.assertNotEqual(code, 0, out)


class FilterTests(Fixture):
    def test_prefix_filter(self):
        self.write(self.a, "blog/x.txt", "1")
        self.write(self.b, "blog/x.txt", "1")
        self.write(self.a, "about/x.txt", "1")
        self.assertClean(run(self.a, self.b, "--prefix", "blog/"))
        self.assertDiffers(run(self.a, self.b, "--prefix", "about/"))
        self.assertDiffers(run(self.a, self.b))


@unittest.skipUnless(Path(BASELINE).is_dir(), "Baseline not available")
class BaselineSelfTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = Path(tempfile.mkdtemp())
        cls.copy = cls.tmp / "site"
        shutil.copytree(BASELINE, cls.copy)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp)

    def test_baseline_vs_itself_is_clean(self):
        code, out = run(BASELINE, BASELINE, "--no-exceptions")
        self.assertEqual(code, 0, out)

    def test_baseline_vs_empty_reports_every_file_missing(self):
        empty = self.tmp / "empty"
        empty.mkdir(exist_ok=True)
        code, out = run(BASELINE, empty, "--no-exceptions")
        self.assertNotEqual(code, 0)
        n = sum(1 for p in Path(BASELINE).rglob("*")
                if p.is_file() and "pagefind" not in p.relative_to(BASELINE).parts[:1])
        self.assertEqual(out.count("MISSING  "), n + 1)  # + the pagefind/ directory

    def test_changed_word_reported_reindent_not(self):
        p = self.copy / "about" / "index.html"
        orig = p.read_text(encoding="utf-8")
        try:
            p.write_text(orig.replace("<p>", "\n    <p>\n      ").replace("</p>", "\n    </p>\n"),
                         encoding="utf-8")
            code, out = run(BASELINE, self.copy, "--no-exceptions")
            self.assertEqual(code, 0, out)
            p.write_text(orig.replace("Krakowski Klub", "Krakowski Klubik", 1), encoding="utf-8")
            code, out = run(BASELINE, self.copy, "--no-exceptions")
            self.assertNotEqual(code, 0, out)
            self.assertIn("DIFFERENT about/index.html", out)
        finally:
            p.write_text(orig, encoding="utf-8")


if __name__ == "__main__":
    unittest.main()
