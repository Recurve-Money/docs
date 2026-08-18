#!/usr/bin/env python3
"""Renders the docs pages from a shared shell so nav and chrome stay in sync."""
import html as H
import os
import re

OUT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

LOGO_PATH = re.search(
    r'<path d="([^"]+)"', open(os.path.join(OUT, "logo.svg")).read()
).group(1)

MARK = (
    f'<svg viewBox="0 0 612 759" fill="currentColor" aria-hidden="true">'
    f'<path d="{LOGO_PATH}"/></svg>'
)

# slug, title, section
NAV = [
    ("Getting started", [
        ("index", "Introduction"),
        ("quickstart", "Quickstart"),
        ("concepts", "Core concepts"),
    ]),
    ("Protocol", [
        ("vaults", "Vaults"),
        ("governance", "Governance"),
        ("watchers", "Watchers"),
        ("fees", "Fees and settlement"),
    ]),
    ("Building", [
        ("sdk", "SDK reference"),
        ("agent-skill", "Agent skill"),
        ("watcher-skill", "Watcher skill"),
    ]),
    ("Reference", [
        ("contracts", "Contracts"),
        ("errors", "Errors"),
    ]),
]

ORDER = [slug for _, items in NAV for slug, _ in items]
TITLES = {slug: title for _, items in NAV for slug, title in items}


def sidebar(active):
    out = []
    for section, items in NAV:
        out.append(f'<div class="side-group"><h4>{section}</h4>')
        for slug, title in items:
            href = "/" if slug == "index" else f"/{slug}"
            cls = ' class="on"' if slug == active else ""
            out.append(f'<a href="{href}"{cls}>{title}</a>')
        out.append("</div>")
    return "\n".join(out)


def toc(body):
    """Builds the on-page nav from h2/h3 already carrying ids."""
    heads = re.findall(r'<(h2|h3) id="([^"]+)">(.*?)</\1>', body, re.S)
    if not heads:
        return ""
    links = []
    for tag, hid, text in heads:
        text = re.sub(r"<[^>]+>", "", text).strip()
        cls = ' class="sub"' if tag == "h3" else ""
        links.append(f'<a href="#{hid}"{cls}>{H.escape(text)}</a>')
    return '<nav class="toc"><h4>On this page</h4>' + "\n".join(links) + "</nav>"


def pager(slug):
    if slug not in ORDER:
        return ""
    i = ORDER.index(slug)
    parts = ['<div class="pager">']
    if i > 0:
        p = ORDER[i - 1]
        href = "/" if p == "index" else f"/{p}"
        parts.append(
            f'<a href="{href}"><span class="dir">Previous</span>'
            f'<span class="ttl">{TITLES[p]}</span></a>'
        )
    if i < len(ORDER) - 1:
        n = ORDER[i + 1]
        parts.append(
            f'<a class="next" href="/{n}"><span class="dir">Next</span>'
            f'<span class="ttl">{TITLES[n]}</span></a>'
        )
    parts.append("</div>")
    return "\n".join(parts) if len(parts) > 2 else ""


SHELL = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title} - Recurve Docs</title>
<meta name="description" content="{desc}">
<link rel="icon" href="/favicon.ico?v=3" sizes="any">
<link rel="icon" href="/icon.png?v=3" type="image/png" sizes="256x256">
<link rel="apple-touch-icon" href="/apple-icon.png?v=3">
<link rel="manifest" href="/site.webmanifest">
<meta name="theme-color" content="#0A0A0A">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/style.css">
<link rel="stylesheet" href="/docs.css">
</head>
<body>

<header class="hdr">
  <div class="hdr-left">
    <a class="brand" href="/" aria-label="Recurve Docs">
      {mark}
      <span>Recurve</span>
    </a>
    <span class="sm muted" style="border-left:1px solid var(--rule);padding-left:14px">Docs</span>
  </div>
  <div style="display:flex;align-items:center;gap:14px">
    <a class="sm muted" href="https://recurvemoney.xyz" style="font-size:15px">Website</a>
    <a class="sm muted" href="https://github.com/recurveprotocol" style="font-size:15px">GitHub</a>
    <a class="btn btn-dark btn-sm" href="https://recurvemoney.xyz/app">Open app</a>
  </div>
</header>

<div class="docs-shell">
  <nav class="side">
{sidebar}
  </nav>

  <article class="doc">
    <p class="crumb">{crumb}</p>
    <h1>{title}</h1>
    <p class="subtitle">{subtitle}</p>
{body}
{pager}
  </article>

{toc}
</div>

</body>
</html>
"""


def render(slug, title, subtitle, crumb, body, desc=None):
    page = SHELL.format(
        title=H.escape(title),
        desc=H.escape(desc or subtitle),
        mark=MARK,
        sidebar=sidebar(slug),
        crumb=H.escape(crumb),
        subtitle=subtitle,
        body=body,
        pager=pager(slug),
        toc=toc(body),
    )
    name = "index.html" if slug == "index" else f"{slug}.html"
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(page)
    return name
