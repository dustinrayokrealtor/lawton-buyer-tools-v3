"""Article pages: the /fort-sill/ area pages and the /guides/ articles.

Each article is one file under _build/content/. It starts with a META block
(JSON inside an HTML comment) and the rest is the body: plain <p>, <h2>, <ul>,
tables and notes. Every <h2> starts a new section. Rate-dependent numbers are
written as {{tokens}} (see common.expand) so they stay live on the page.

META keys
  path      "fort-sill/elgin" or "guides/closing-costs-oklahoma"
  title, desc, h1, eyebrow, intro      (desc and intro may use {{tokens}})
  stats     optional [[big, label], ...] tiles in the hero
  form      {source, head, lede, button, checked, notes}
  faqs      [[question, answer], ...]
  related   [[href, title, blurb], ...]
  card      blurb used on the /guides/ hub
  queue     {"order": 3, "notBefore": "2026-12-14"}  -> written to /_queue/ instead of published
"""
import glob
import json
import os
import re

import bah
from common import (FOOT_AREA, HERE, SITE, toolchips, article_ld, breadcrumb_ld, cta, esc, expand, faq_html,
                    faq_ld, footer, head, header, hero, leadform, strip_tags)

PUBLISHED = "2026-10-12"
META = re.compile(r"^\s*<!--META\s*(\{.*?\})\s*-->", re.S)


def bah_macros(text):
    """[[bah:year]], [[bah:E-5:w]] / [[bah:E-5:wo]], [[bah:short]] and [[bah:full]] are filled from the
    table in bah.py, so the articles that quote BAH rates follow the January update."""
    rates = {l: (w, wo) for l, w, wo, _k in bah.BAH}

    def cell(label, deps):
        w, wo = rates[label]
        return '<a href="%s">%s</a>' % (bah.url(label, deps), bah.money(w if deps else wo))

    def short():
        left, right = ["E-5", "E-6", "E-7", "E-8", "E-9"], ["W-2", "O-1", "O-2", "O-3", "O-4"]
        rows = "".join('    <tr><td><a href="%s">%s</a></td><td class="num">%s</td><td><a href="%s">%s</a></td>'
                       '<td class="num">%s</td></tr>\n' % (bah.url(a, True), a, bah.money(rates[a][0]),
                                                           bah.url(b, True), b, bah.money(rates[b][0]))
                       for a, b in zip(left, right))
        return ('<div class="tscroll">\n<table>\n  <caption>%d Fort Sill BAH with dependents. Compare yours to the '
                'payment above.</caption>\n  <thead><tr><th>Pay grade</th><th class="num">BAH</th><th>Pay grade</th>'
                '<th class="num">BAH</th></tr></thead>\n  <tbody>\n%s  </tbody>\n</table>\n</div>' % (bah.YEAR, rows))

    def full():
        rows = "".join('    <tr><td>%s</td><td class="num">%s</td><td class="num">%s</td></tr>\n' % (
            l, cell(l, True), cell(l, False)) for l in rates)
        return ('<div class="tscroll">\n<table>\n  <caption>%d BAH, Fort Sill / Lawton. In effect through '
                'December 31, %d.</caption>\n  <thead><tr><th>Pay grade</th><th class="num">With dependents</th>'
                '<th class="num">Without</th></tr></thead>\n  <tbody>\n%s  </tbody>\n</table>\n</div>' % (
                    bah.YEAR, bah.YEAR, rows))

    text = text.replace("[[bah:year]]", str(bah.YEAR))
    text = re.sub(r"\[\[bah:([A-Z0-9-]+):(wo?)\]\]",
                  lambda m: bah.money(rates[m.group(1)][0 if m.group(2) == "w" else 1]), text)
    if "[[bah:short]]" in text:
        text = text.replace("[[bah:short]]", short())
    if "[[bah:full]]" in text:
        text = text.replace("[[bah:full]]", full())
    return text


def load():
    arts = []
    for fn in sorted(glob.glob(os.path.join(HERE, "content", "*", "*.html"))):
        raw = open(fn, encoding="utf-8").read()
        m = META.match(raw)
        if not m:
            raise SystemExit("no META block in " + fn)
        meta = json.loads(m.group(1))
        meta = json.loads(bah_macros(m.group(1)))
        meta["body"] = bah_macros(raw[m.end():].strip())
        meta["file"] = fn
        arts.append(meta)
    return arts


def sections(body):
    chunks = re.split(r"(?=<h2[ >])", body)
    out, i = "", 0
    for c in chunks:
        c = c.strip()
        if not c:
            continue
        out += '<section class="block%s">\n%s\n</section>\n' % (" alt" if i % 2 else "", c)
        i += 1
    return out


def render(a, queued=False):
    path = a["path"].strip("/")
    section = path.split("/")[0]
    url = "/%s/" % path
    canon = SITE + url
    desc = expand(a["desc"], plain=True)
    if section == "fort-sill":
        crumbs = [("Moving to Fort Sill", "/"), (a.get("crumb", a["h1"]), None)]
        ld_crumbs = [("Moving to Fort Sill", SITE + "/"), (a["h1"], canon)]
        nav = "guide"
    else:
        crumbs = [("Moving to Fort Sill", "/"), ("Guides", "/guides/"), (a.get("crumb", a["h1"]), None)]
        ld_crumbs = [("Moving to Fort Sill", SITE + "/"), ("Guides", SITE + "/guides/"), (a["h1"], canon)]
        nav = "guides"
    stats = [(expand(b), expand(s)) for b, s in a.get("stats", [])] or None

    body = a["body"]
    f = a.get("form")
    form_html = ""
    if f:
        form_html = leadform(f["source"], f.get("head"), f["lede"], f["button"],
                             checked=tuple(f.get("checked", ["listings"])), notes_label=f.get("notes", "Anything else"))
    if "{{form}}" in body:
        body = body.replace("{{form}}", form_html)
        form_html = ""
    main = sections(expand(body))
    if form_html:
        main += '<section class="block alt">\n%s</section>\n' % form_html
    faqs = a.get("faqs") or []
    if faqs:
        main += faq_html(faqs)
    rel = a.get("related") or []
    if rel:
        main += '<section class="block">\n  <h2>Keep reading</h2>\n  <ul class="linkgrid wide">\n'
        for href, t, blurb in rel:
            main += '    <li><a href="%s">%s<span>%s</span></a></li>\n' % (href, t, blurb)
        main += "  </ul>\n</section>\n"

    pub = "%%PUBDATE%%" if queued else a.get("published", PUBLISHED)
    ld = [breadcrumb_ld(ld_crumbs), article_ld(strip_tags(a["h1"]), desc, canon, pub)]
    if faqs:
        ld.append(faq_ld(faqs))
    subj = a.get("subject", "Moving to Fort Sill")
    contact = ""
    if not f:
        contact = cta(a.get("cta_h2", "Questions about the move?"),
                      "I am a buyer specialist with Pam &amp; Barry's Team at RE/MAX Professionals in Lawton. If you "
                      "are PCSing in and have questions about the process, the timeline, or a specific house, call "
                      "or text. It costs nothing to ask, and there is no obligation to work with me.",
                      subj,
                      'Also useful: the <a href="/bah/">Fort Sill BAH calculator</a> and '
                      '<a href="/tools/">the rest of the tools</a>.')
    page = (head(a["title"], desc, canon, ld)
            + header(nav, subj)
            + hero(crumbs, a["eyebrow"], a["h1"], expand(a["intro"]), a.get("stamp"), stats)
            + '\n<main class="wrap">\n\n' + main + contact
            + toolchips()
            + "\n</main>\n\n"
            + footer(FOOT_AREA, "Information current as of October 2026.", subj))
    return url, canon, page


def build():
    """Returns (live, queued). live: [(relpath, html, canon, meta)], queued: [(filename, html, meta)]."""
    live, queued = [], []
    for a in load():
        q = a.get("queue")
        url, canon, page = render(a, queued=bool(q))
        rel = url.strip("/") + "/index.html"
        if q:
            info = {"path": rel, "url": url, "title": strip_tags(a["h1"]), "blurb": a.get("card", "")}
            if q.get("notBefore"):
                info["notBefore"] = q["notBefore"]
            name = "%02d--%s.html" % (q["order"], url.strip("/").split("/")[-1])
            queued.append((name, "<!--QUEUE %s -->\n%s" % (json.dumps(info), page), a))
        else:
            live.append((rel, page, canon, a))
    return live, queued
