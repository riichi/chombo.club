#!/usr/bin/env python3
"""One-time migration of Polish posts (_posts/**/*.pl.md) to Zola content/posts/<year>/.

Usage: python3 _migrate/migrate_posts.py <baseline-site-dir>
Delete in ticket 10.
"""
import re, subprocess, sys, datetime, glob, os
from zoneinfo import ZoneInfo
from lxml import html as LH

WAW = ZoneInfo("Europe/Warsaw")
B = sys.argv[1]


def parse_dt(s):
    d = datetime.datetime.strptime(s.strip(), "%Y-%m-%d %H:%M:%S %z")
    return d


def toml_str(s):
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def baseline_path(cat, dt, slug):
    w = dt.astimezone(WAW)
    for cand in os.listdir(os.path.join(B, cat, f"{w:%Y}", f"{w:%m}", f"{w:%d}")):
        if cand.lower() == slug.lower():
            return f"{cat}/{w:%Y}/{w:%m}/{w:%d}/{cand}"
    raise SystemExit(f"no baseline url for {slug}")


def heading_ids(path):
    doc = LH.parse(os.path.join(B, path, "index.html"))
    art = doc.xpath('//article[contains(@class,"page-content")]')[0]
    return [h.get("id") for h in art.xpath(".//h1|.//h2|.//h3|.//h4|.//h5|.//h6")]


FIG = re.compile(r'{%\s*include figure\.html alt="([^"]*)" filename="([^"]*)"\s*%}')
CAPTURE = re.compile(
    r'{% capture (\w+) %}\n!\[([^\]]*)\]\({{ "/assets/images/([^"]+)" \| relative_url }}\)\n{% endcapture %}\n\n'
    r'<figure>\n  {{ \1 \| markdownify \| remove: "<p>" \| remove: "</p>" }}\n</figure>')


def convert_body(body):
    body = FIG.sub(lambda m: f'{{{{ <figure alt="{m[1]}" filename="{m[2]}" /> }}}}', body)
    body = CAPTURE.sub(lambda m: f'{{{{ <figure alt="{m[2]}" filename="{m[3]}" /> }}}}', body)
    body = body.replace("{% comment %}", "{#").replace("{% endcomment %}", "#}")
    body = body.replace('{{ page.last_modified_at | date:"%Y-%m-%d %H:%M" }}',
                        '{{ page.updated | date(format="%Y-%m-%d %H:%M", timezone=config.extra.timezone) }}')
    # kramdown ends the figure block at the line end; CommonMark would swallow the next line into the HTML block
    body = re.sub(r'(/> }}\n)(?=[^\n])', r'\1\n', body)
    # kramdown "\\" hard line break -> CommonMark "\"
    body = body.replace('\\\\\n', '\\\n')
    # kramdown treats a line-start <a> as inline and wraps it in <p>; CommonMark makes it an HTML block
    body = re.sub(r'^<a href="(/assets/images/mers-\d+-map\.png)">\n(.*?)\n</a>$', r'<p><a href="\1">\n\2\n</a></p>', body, flags=re.M)
    return body


def add_ids(body, ids):
    out, i, fence, cmt = [], 0, False, False
    for line in body.split("\n"):
        if line.lstrip().startswith("```"):
            fence = not fence
        if "<!--" in line or "{#" in line:
            cmt = True
        m = None if fence or cmt else re.match(r"^(#{1,6}) (.*?)\s*$", line)
        if "-->" in line or "#}" in line:
            cmt = False
        if m:
            line = f"{m[1]} {m[2]} {{#{ids[i]}}}"
            i += 1
        out.append(line)
    assert i == len(ids), (i, ids)
    return "\n".join(out)


for src in sorted(glob.glob("_posts/*/*.pl.md")):
    text = open(src, encoding="utf-8").read()
    _, fm, body = text.split("---\n", 2)
    meta, header = {}, {}
    cur = None
    for line in fm.splitlines():
        if line.startswith("  ") and cur == "header":
            k, v = line.strip().split(":", 1)
            header[k] = v.strip()
            continue
        k, v = line.split(":", 1)
        cur = k
        meta[k] = v.strip()
    title = meta["title"].strip('"')
    dt = parse_dt(meta["date"])
    cat = meta["categories"]
    year = os.path.basename(os.path.dirname(src))
    slug = re.sub(r"^\d{4}-\d{2}-\d{2}-", "", os.path.basename(src)[:-len(".pl.md")])
    path = baseline_path(cat, dt, slug)
    lines = ["+++", f"title = {toml_str(title)}", f"date = {dt.isoformat()}"]
    if "last_modified_at" in meta:
        lines.append(f"updated = {parse_dt(meta['last_modified_at']).isoformat()}")
    lines += [f'path = "{path}"', 'template = "post.html"', "", "[taxonomies]", f'categories = ["{cat}"]']
    if "lang-exclusive" in meta or header:
        lines += ["", "[extra]"]
        if "lang-exclusive" in meta:
            lines.append(f'lang-exclusive = {meta["lang-exclusive"]}')
        if header:
            lines += ["", "[extra.header]"] + [f"{k} = {toml_str(v)}" for k, v in header.items()]
    lines.append("+++")
    body = add_ids(convert_body(body), heading_ids(path))
    dst = f"content/posts/{year}/{os.path.basename(src)[:-len('.pl.md')]}.md"
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    idx = os.path.join(os.path.dirname(dst), "_index.md")
    if not os.path.exists(idx):
        open(idx, "w").write('+++\nrender = false\ntransparent = true\nsort_by = "date"\n+++\n')
    subprocess.run(["git", "mv", src, dst], check=True)
    open(dst, "w", encoding="utf-8").write("\n".join(lines) + "\n" + body)
    print(dst, path)
    subprocess.run([sys.executable, os.path.join(os.path.dirname(__file__), "fix_lists.py"), B, dst], check=True)
