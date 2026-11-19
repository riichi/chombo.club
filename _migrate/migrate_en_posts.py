#!/usr/bin/env python3
"""One-time conversion of English posts (content/posts/<y>/x.en.md, Jekyll front matter) to Zola.

Front matter (date, updated, category, header) is copied from the Original x.md; path = "en/" + Original path.
Body conversion and heading IDs reuse migrate_posts.py. Then fix_lists.py runs on the file.

Usage: python3 _migrate/migrate_en_posts.py <baseline-site-dir>
Delete in ticket 10.
"""
import re, sys, glob, os, subprocess, importlib.util

B = sys.argv[1]
here = os.path.dirname(os.path.abspath(__file__))
# migrate_posts.py runs its loop at import time over _posts/*.pl.md; none are left, so importing is side-effect free.
spec = importlib.util.spec_from_file_location("mp", os.path.join(here, "migrate_posts.py"))
mp = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mp)

for src in sorted(glob.glob("content/posts/*/*.en.md")):
    text = open(src, encoding="utf-8").read()
    if text.startswith("+++"):
        continue
    _, fm, body = text.split("---\n", 2)
    title = re.search(r"^title:\s*(.*)$", fm, re.M)[1].strip().strip('"')
    orig = open(src[:-len(".en.md")] + ".md", encoding="utf-8").read()
    ofm = orig.split("+++\n")[1]
    assert "lang-exclusive" not in ofm, src
    lines = ["+++", f"title = {mp.toml_str(title)}"]
    for line in ofm.splitlines()[1:]:
        if line.startswith("path = "):
            line = 'path = "en/' + line[len('path = "'):]
        lines.append(line)
    lines.append("+++")
    path = re.search(r'^path = "([^"]+)"', "\n".join(lines), re.M)[1]
    body = mp.add_ids(mp.convert_body(body), mp.heading_ids(path))
    open(src, "w", encoding="utf-8").write("\n".join(lines) + "\n" + body)
    print(src, path)
    subprocess.run([sys.executable, os.path.join(here, "fix_lists.py"), B, src], check=True)
