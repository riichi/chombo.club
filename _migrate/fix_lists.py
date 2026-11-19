#!/usr/bin/env python3
"""One-time fix of loose/tight list differences (kramdown vs CommonMark), guided by the Baseline.

kramdown wraps a list item in <p> per item (roughly: when a blank line follows it);
CommonMark makes a whole list loose if any blank line separates its items.
For each group of sibling items whose Baseline rendering is not "all <p>":
remove the blank lines between them (tight list) and write the items the
Baseline wraps in <p> as an explicit <p>...</p>.

Usage: python3 _migrate/fix_lists.py <baseline-site-dir> content/posts/...md ...
Delete in ticket 10.
"""
import re, sys, os, html
from lxml import html as LH

ITEM = re.compile(r"^(\s*)([*+-]|\d+\.)\s+(.*)$")


def md_inline(s):
    s = re.sub(r"!\[([^\]]*)\]\(([^)]+)\)", r'<img src="\2" alt="\1" />', s)
    s = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"(?<![*\w])\*(?!\s)(.+?)\*", r"<em>\1</em>", s)
    s = re.sub(r"`([^`]+)`", r"<code>\1</code>", s)
    return s


def plain(s):
    s = re.sub(r"!\[[^\]]*\]\([^)]+\)", "", s)
    s = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", s)
    s = re.sub(r"<[^>]+>", "", s)
    return re.sub(r"[*`]", "", s).strip()


def baseline_li(doc):
    """first-line text -> True (wrapped in <p>) / False"""
    out = {}
    for li in doc.iter("li"):
        has_p = (li.text or "").strip() == "" and len(li) and li[0].tag == "p"
        first = li[0] if has_p else li
        txt = re.sub(r"\s+", " ", (first.text_content() if has_p else (li.text or "") + "".join(
            (c.text_content() + (c.tail or "")) for c in li if c.tag not in ("ul", "ol", "div")))).strip()
        # smart punctuation in the Baseline vs ASCII in the source
        txt = txt.translate(str.maketrans("\u2019\u2018\u201c\u201d", "''\"\""))
        out.setdefault(txt[:40], has_p)
    return out


def fix(lines, bl):
    n = len(lines)

    def indent(l):
        return len(l) - len(l.lstrip())

    i = 0
    changed = False
    while i < n:
        m = ITEM.match(lines[i])
        if not m:
            i += 1
            continue
        ind = len(m[1])
        # collect sibling items at this indent
        items = []  # (start, end_exclusive_without_trailing_blanks, end_with_blanks)
        j = i
        while j < n:
            mm = ITEM.match(lines[j])
            if not (mm and len(mm[1]) == ind):
                break
            k = j + 1
            while k < n and (lines[k].strip() == "" or indent(lines[k]) > ind) and not (
                    ITEM.match(lines[k]) and indent(lines[k]) == ind):
                k += 1
            # k: next sibling or end; trailing blanks belong to gap
            e = k
            while e > j + 1 and lines[e - 1].strip() == "":
                e -= 1
            items.append((j, e, k))
            j = k
            if j < n and not (ITEM.match(lines[j]) and indent(lines[j]) == ind):
                break
        simple = all(all(lines[x].strip() != "" for x in range(s, e)) for s, e, _ in items)
        gaps = any(e != k for s, e, k in items[:-1])
        if simple and gaps:
            wraps = []
            for s, e, _ in items:
                key = plain(ITEM.match(lines[s])[3])[:40]
                key = re.sub(r"\s+", " ", key)
                hit = [v for t, v in bl.items() if t[:len(key)] == key or key[:len(t)] == t and t]
                if not hit:
                    raise SystemExit(f"no baseline li for {key!r}")
                wraps.append(hit[0])
            if not all(wraps):
                new = []
                for (s, e, k), w in zip(items, wraps):
                    block = lines[s:e]
                    if w:
                        mm = ITEM.match(block[0])
                        # first paragraph = lines until a nested item
                        p_end = 1
                        while p_end < len(block) and not ITEM.match(block[p_end]):
                            p_end += 1
                        text = " ".join([mm[3]] + [b.strip() for b in block[1:p_end]])
                        block = [f"{mm[1]}{mm[2]} <p>{md_inline(text)}</p>"] + block[p_end:]
                    new += block
                last_k = items[-1][2]
                tail = lines[items[-1][1]:last_k]
                lines[i:last_k] = new + tail
                n = len(lines)
                changed = True
                i += len(new)
                continue
        i += 1
    return changed


if __name__ == "__main__":
    B = sys.argv[1]
    for f in sys.argv[2:]:
        text = open(f, encoding="utf-8").read()
        path = re.search(r'^path = "([^"]+)"', text, re.M)[1]
        doc = LH.parse(os.path.join(B, path, "index.html"))
        bl = baseline_li(doc)
        lines = text.split("\n")
        if fix(lines, bl):
            open(f, "w", encoding="utf-8").write("\n".join(lines))
            print("fixed", f)
