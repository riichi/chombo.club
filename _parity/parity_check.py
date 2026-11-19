#!/usr/bin/env python3
"""Parity check: compare a Zola output directory against the Jekyll Baseline.

Usage:
    python3 _parity/parity_check.py BASELINE OUTPUT [--prefix P ...] [--no-exceptions]
                                    [--verbose] [--max-diff N]

Each file is reported as OK, MISSING (in Baseline only), EXTRA (in output only),
DIFFERENT (with a diff of the normalised forms) or KNOWN (a listed known
exception). Exit code is 1 when anything is MISSING, EXTRA or DIFFERENT.

Rebuilding the Baseline (from the repo root, at the Baseline commit, with the
pre-migration Dockerfile):
    git worktree add ../zola-baseline/src ae8d366
    docker build --target build -t chombo-baseline ../zola-baseline/src
    id=$(docker create chombo-baseline)
    docker cp "$id:/output" ../zola-baseline/site && docker rm "$id"
Keep the Baseline outside the worktree.

Comparison rules (see .scratch/zola-migration/spec.md, "Parity check"):
  *.html       parsed as trees; whitespace outside pre/textarea/script, attribute
               order, void-tag syntax, character references, quoting and comments
               ignored; kramdown code-block wrappers and the
               language-plaintext/highlighter-rouge/highlight classes removed;
               JSON <script>s compared as parsed JSON; footer "© YYYY" ignored.
  *.xml        normalised XML; the feed-level <updated> ignored; Atom
               content/summary of type="html" compared as HTML.
  *.css        compared after the same minifier on both sides.
  pagefind/    checked for existence only.
  otherwise    byte-identical.
"""
import argparse
import difflib
import json
import re
import sys
import urllib.parse
from pathlib import Path

import lxml.etree as etree
import lxml.html

# --- Known exceptions: the single list, each with its reason. ---------------
KNOWN_EXCEPTIONS = {
    "dropped-en-static": "jekyll-polyglot copied static files under /en/; Zola serves "
                         "static files from the root only (ADR 0001).",
    "en-root-assets": "EN pages reference root assets (/assets/...) instead of the "
                      "dropped /en/ copies; Baseline /en/<static> URLs are rewritten.",
    "sitemap-no-static": "jekyll-sitemap listed static files (PDFs, /pralka/ ...); the "
                         "Zola sitemap lists generated pages only.",
    "no-css-source-map": "dart-sass wrote a source map (main.css.map) pointing at _sass/; "
                         "Zola's Sass compiler (grass) emits none. Not visible to visitors.",
}

ATOM = "{http://www.w3.org/2005/Atom}"
PRESERVE = {"pre", "textarea", "script", "style"}
KRAMDOWN_CLASSES = {"language-plaintext", "highlighter-rouge", "highlight"}
YEAR_RE = re.compile(r"(©|&copy;)\s*\d{4}")


def ws(s):
    return re.sub(r"\s+", " ", s).strip()


# --- HTML -------------------------------------------------------------------
def norm_html(text):
    if not text.strip():
        return []
    doc = lxml.html.document_fromstring(text)
    for c in doc.xpath("//comment()"):
        drop(c)
    # kramdown: <div class="… highlighter-rouge"><div class="highlight"><pre>… → <pre>…
    for div in doc.xpath('//div[contains(concat(" ", @class, " "), " highlighter-rouge ")]'):
        kids = list(div)
        if len(kids) == 1 and kids[0].tag == "div" and len(kids[0]) == 1 and kids[0][0].tag == "pre":
            pre = kids[0][0]
            pre.tail = div.tail
            div.getparent().replace(div, pre)
    for el in doc.iter():
        if isinstance(el.tag, str) and "class" in el.attrib:
            cls = [c for c in el.get("class").split() if c not in KRAMDOWN_CLASSES]
            if cls:
                el.set("class", " ".join(cls))
            else:
                del el.attrib["class"]
    lines = []
    walk_html(doc, 0, lines)
    return lines


def drop(node):
    parent = node.getparent()
    if parent is None:
        return
    tail = node.tail or ""
    prev = node.getprevious()
    if prev is not None:
        prev.tail = (prev.tail or "") + tail
    else:
        parent.text = (parent.text or "") + tail
    parent.remove(node)


def attr_value(k, v):
    if k == "class":
        return ws(v)
    if k in ("href", "src"):
        # pulldown-cmark percent-encodes non-ASCII URLs, kramdown doesn't; browsers treat both the same
        return urllib.parse.unquote(v)
    return v


def attrs(el):
    return " ".join(f'{k}="{attr_value(k, v)}"' for k, v in sorted(el.attrib.items()))


def text_line(s, depth, lines, keep):
    if keep:
        if s:
            lines.append("  " * depth + "|" + repr(s))
    else:
        s = YEAR_RE.sub(r"\1 YEAR", ws(s)).replace("&copy;", "©")
        if s:
            lines.append("  " * depth + "|" + s)


def walk_html(el, depth, lines, keep=False):
    tag = el.tag
    a = attrs(el)
    lines.append("  " * depth + f"<{tag}{' ' + a if a else ''}>")
    keep = keep or tag in PRESERVE
    if tag == "script" and "json" in (el.get("type") or ""):
        try:
            data = json.dumps(json.loads(el.text or ""), sort_keys=True, indent=1, ensure_ascii=False)
            lines.extend("  " * (depth + 1) + "|" + l for l in data.splitlines())
        except ValueError:
            text_line(el.text or "", depth + 1, lines, True)
    else:
        text_line(el.text or "", depth + 1, lines, keep)
        for child in el:
            walk_html(child, depth + 1, lines, keep)
    lines.append("  " * depth + f"</{tag}>")
    text_line(el.tail or "", depth, lines, keep and el.getparent() is not None
              and el.getparent().tag in PRESERVE)


# --- XML --------------------------------------------------------------------
def norm_xml(data, sitemap_drop=None):
    root = etree.fromstring(data, etree.XMLParser(remove_comments=True, remove_pis=True))
    if root.tag == ATOM + "feed":
        for u in root.findall(ATOM + "updated"):
            root.remove(u)
    if sitemap_drop is not None:
        for url in list(root):
            loc = url.find("{*}loc")
            if loc is not None and sitemap_drop(loc.text or ""):
                root.remove(url)
    lines = []
    walk_xml(root, 0, lines)
    return lines


def walk_xml(el, depth, lines):
    a = " ".join(f'{k}="{v}"' for k, v in sorted(el.attrib.items()))
    lines.append("  " * depth + f"<{el.tag}{' ' + a if a else ''}>")
    if el.tag in (ATOM + "content", ATOM + "summary") and el.get("type") == "html":
        body = norm_html(el.text or "")
        lines.extend("  " * (depth + 1) + l for l in body[2:-2])  # strip <html><body>
    else:
        t = ws(el.text or "")
        if t:
            lines.append("  " * (depth + 1) + "|" + t)
        for child in el:
            walk_xml(child, depth + 1, lines)
    lines.append("  " * depth + f"</{el.tag}>")


# --- CSS --------------------------------------------------------------------
def minify_css(s):
    s = re.sub(r"/\*.*?\*/", "", s, flags=re.S)
    s = re.sub(r"\s+", " ", s)
    s = re.sub(r"\s*([{}:;,>+~])\s*", r"\1", s)
    s = s.replace(";}", "}")
    # dart-sass vs grass serialiser differences
    s = re.sub(r"@media \(", "@media(", s)
    s = re.sub(r"(?<![\w.])0\.(\d)", r".\1", s)
    s = re.sub(r"\btransparent\b", "rgba(0,0,0,0)", s)
    return s.strip()


# --- Driver -----------------------------------------------------------------
def files(root):
    root = Path(root)
    return {p.relative_to(root).as_posix() for p in root.rglob("*") if p.is_file()}


class Checker:
    def __init__(self, base, out, exceptions=True):
        self.base, self.out = Path(base), Path(out)
        self.exceptions = exceptions
        self.static = set()
        if exceptions:
            bf = files(base)
            for rel in bf:
                if not rel.startswith("en/") and "en/" + rel in bf and \
                        (self.base / rel).read_bytes() == (self.base / ("en/" + rel)).read_bytes():
                    self.static.add(rel)
        self.static_urls = {r[: -len("index.html")] if r.endswith("index.html") else r
                            for r in self.static}

    def rewrite_en(self, text):
        """en-root-assets: /en/<static> → /<static> in Baseline EN files."""
        def sub(m):
            return "/" + m.group(1) if m.group(1) in self.static_urls else m.group(0)
        return re.sub(r"/en/([^\s\"'<>()?#,]+)", sub, text)

    def is_static_url(self, loc):
        """sitemap-no-static."""
        path = re.sub(r"^[a-z]+://[^/]+/", "", loc.strip())
        return path in self.static_urls

    def normalise(self, rel, path, baseline):
        data = path.read_bytes()
        ext = rel.rsplit(".", 1)[-1].lower() if "." in rel else ""
        en = baseline and self.exceptions and rel.startswith("en/")
        if ext in ("html", "htm"):
            text = data.decode("utf-8", "replace")
            return norm_html(self.rewrite_en(text) if en else text)
        if ext == "xml":
            if en:
                data = self.rewrite_en(data.decode("utf-8")).encode("utf-8")
            drop = self.is_static_url if (baseline and self.exceptions
                                          and rel.endswith("sitemap.xml")) else None
            return norm_xml(data, drop)
        if ext == "css":
            text = data.decode("utf-8", "replace")
            return minify_css(self.rewrite_en(text) if en else text).replace("}", "}\n").splitlines()
        return data

    def compare(self, rel):
        try:
            a = self.normalise(rel, self.base / rel, True)
            b = self.normalise(rel, self.out / rel, False)
        except Exception as e:  # unparsable on either side
            return [f"    (parse error: {e}; compared bytes)"] if \
                (self.base / rel).read_bytes() != (self.out / rel).read_bytes() else None
        if a == b:
            return None
        if isinstance(a, bytes):
            return [f"    binary/byte difference ({len(a)} vs {len(b)} bytes)"]
        return ["    " + l.rstrip("\n") for l in
                difflib.unified_diff(a, b, "baseline/" + rel, "output/" + rel, n=2, lineterm="")]


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("baseline")
    ap.add_argument("output")
    ap.add_argument("--prefix", action="append", default=[],
                    help="only check paths starting with this (repeatable), e.g. en/ or tournaments/")
    ap.add_argument("--no-exceptions", action="store_true", help="disable the known exceptions")
    ap.add_argument("--verbose", "-v", action="store_true", help="also list OK files")
    ap.add_argument("--max-diff", type=int, default=60, help="diff lines shown per file (0 = all)")
    args = ap.parse_args(argv)

    for d in (args.baseline, args.output):
        if not Path(d).is_dir():
            ap.error(f"not a directory: {d}")
    chk = Checker(args.baseline, args.output, not args.no_exceptions)
    in_scope = (lambda r: any(r.startswith(p.lstrip("/")) for p in args.prefix)) if args.prefix else (lambda r: True)
    bf = {r for r in files(args.baseline) if in_scope(r)}
    of = {r for r in files(args.output) if in_scope(r)}
    counts = dict.fromkeys(["OK", "KNOWN", "MISSING", "EXTRA", "DIFFERENT"], 0)

    def report(status, rel, extra=None):
        counts[status] += 1
        if status != "OK" or args.verbose:
            print(f"{status:<8} {rel}" if status != "DIFFERENT" else f"DIFFERENT {rel}")
            if extra:
                lines = extra if not args.max_diff or len(extra) <= args.max_diff else \
                    extra[: args.max_diff] + [f"    … {len(extra) - args.max_diff} more diff lines"]
                print("\n".join(lines))

    # pagefind/: existence only
    pf = lambda s: {r for r in s if r.startswith("pagefind/")}
    if pf(bf) or pf(of) or (in_scope("pagefind/") and (Path(args.baseline) / "pagefind").is_dir()):
        if not (Path(args.output) / "pagefind").is_dir():
            report("MISSING", "pagefind/")
        else:
            report("OK", "pagefind/")
    bf -= pf(bf)
    of -= pf(of)

    for rel in sorted(bf | of):
        if rel not in of:
            if chk.exceptions and rel.startswith("en/") and rel[3:] in chk.static:
                report("KNOWN", f"{rel}  [dropped-en-static]")
            elif chk.exceptions and rel.endswith(".css.map"):
                report("KNOWN", f"{rel}  [no-css-source-map]")
            else:
                report("MISSING", rel)
        elif rel not in bf:
            report("EXTRA", rel)
        else:
            d = chk.compare(rel)
            report("DIFFERENT", rel, d) if d else report("OK", rel)

    print("\nSummary: " + ", ".join(f"{k.lower()} {v}" for k, v in counts.items()))
    if chk.exceptions and counts["KNOWN"]:
        print("Known exceptions applied:")
        for k, v in KNOWN_EXCEPTIONS.items():
            print(f"  {k}: {v}")
    bad = counts["MISSING"] + counts["EXTRA"] + counts["DIFFERENT"]
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
