#!/usr/bin/env python3
"""Builds the generated pages of movingtoftsill.com. Run from anywhere:

    python3 _build/gen.py

What it writes (everything else on the site is hand-edited and left alone):
  /bah/<grade>-with-dependents/ and -without-dependents/   from _build/bah.py
  /fort-sill/<page>/ and /guides/<page>/                    from _build/content/
  /guides/index.html                                        the hub
  /_queue/NN--<page>.html                                   articles waiting on the weekly publisher
  sitemap.xml                                               adds any URL that is missing

Rate-dependent numbers are printed at today's data/market.json values and kept
live in the browser by assets/guide-live.js, so there is no need to rebuild
when the rate moves. Rebuild when the BAH table changes (January) or when an
article is edited.

An article with a "queue" key in its META is written to /_queue/ until the
weekly publisher (.github/workflows/publish-queue.yml) moves it into place.
Once its page exists, this script treats it as published and rebuilds it in
place, keeping its original publish date.
"""
import datetime
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import articles  # noqa: E402
import bah  # noqa: E402
from common import (FOOT_AREA, JS_V, MORETOOLS, ROOT, SITE, breadcrumb_ld, cta, expand, footer,  # noqa: E402
                    head, header, hero, strip_tags)

TODAY = datetime.date.today().isoformat()
FORT_SILL_ORDER = ["gates-and-commute", "school-districts", "elgin", "cache", "geronimo", "fletcher",
                   "medicine-park", "buying-before-you-arrive", "rent-it-out-when-you-pcs", "pcs-checklist"]


def write(rel, text):
    p = os.path.join(ROOT, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


def existing_pubdate(rel):
    p = os.path.join(ROOT, rel)
    if not os.path.exists(p):
        return None
    m = re.search(r'"datePublished":\s*"(\d{4}-\d{2}-\d{2})"', open(p, encoding="utf-8").read())
    return m.group(1) if m else None


def build_articles():
    live, queued = [], []
    for a in articles.load():
        rel = a["path"].strip("/") + "/index.html"
        was = existing_pubdate(rel)
        q = a.get("queue")
        if q and not was:
            url, canon, page = articles.render(a, queued=True)
            info = {"path": rel, "url": url, "title": strip_tags(a["h1"]), "blurb": a.get("card", "")}
            if q.get("notBefore"):
                info["notBefore"] = q["notBefore"]
            name = "%02d--%s.html" % (q["order"], a["path"].strip("/").split("/")[-1])
            queued.append((name, "<!--QUEUE %s -->\n%s" % (json.dumps(info), page)))
        else:
            if was:
                a["published"] = was
            url, canon, page = articles.render(a)
            a["published"] = a.get("published", articles.PUBLISHED)
            live.append((rel, page, canon, a))
    return live, queued


def card(href, title, blurb):
    return '    <li><a href="%s">%s<span>%s</span></a></li>\n' % (href, title, blurb)


def hub(live):
    fs = {a["path"].split("/")[-1]: a for _r, _p, _c, a in live if a["path"].startswith("fort-sill/")}
    guides = sorted([a for _r, _p, _c, a in live if a["path"].startswith("guides/")],
                    key=lambda a: (a["published"], a["path"]))
    canon = SITE + "/guides/"
    title = "Fort Sill and Lawton Home Buying Guides"
    desc = ("Plain guides for Fort Sill families and Lawton home buyers: the area, the gates, school districts, "
            "what your BAH buys, VA loans, and closing costs.")
    main = '<section class="block">\n  <h2>The Fort Sill area</h2>\n  <ul class="linkgrid wide">\n'
    for slug in FORT_SILL_ORDER:
        if slug in fs:
            a = fs[slug]
            main += card("/%s/" % a["path"], strip_tags(a["h1"]), a.get("card", ""))
    main += "  </ul>\n</section>\n"
    main += ('<section class="block alt">\n  <h2>Buying in Lawton</h2>\n'
             '  <p>How the money and the paperwork work here. A new one gets added most weeks.</p>\n'
             '  <ul class="linkgrid wide">\n')
    for a in guides:
        main += card("/%s/" % a["path"], strip_tags(a["h1"]), a.get("card", ""))
    main += "    <!-- guides:new  The weekly publisher adds new guides above this line. Leave it here. -->\n"
    main += "  </ul>\n</section>\n"
    main += '<section class="block">\n  <h2>BAH by pay grade</h2>\n'
    main += ("  <p>Every 2026 Fort Sill BAH rate has its own page with what it buys in Lawton. "
             "The full table and the calculator are on the <a href=\"/bah/\">BAH page</a>.</p>\n"
             '  <ul class="linkgrid">\n')
    for label, w, _wo, _k in bah.BAH:
        main += '    <li><a href="%s">%s<span>%s with dependents</span></a></li>\n' % (
            bah.url(label, True), label, bah.money(w))
    main += "  </ul>\n</section>\n"
    ld = [breadcrumb_ld([("Moving to Fort Sill", SITE + "/"), ("Guides", canon)])]
    subj = "Moving to Fort Sill"
    return (head(title, desc, canon, ld)
            + header(None, subj)
            + hero([("Moving to Fort Sill", "/"), ("Guides", None)], "Lawton and Fort Sill", "Guides",
                   "Everything on this site that is not a calculator. Written by a buyer's agent who works this "
                   "market every day, with the local numbers left in.")
            + '\n<main class="wrap">\n\n' + main
            + cta("Questions about the move?",
                  "I am a buyer specialist with Pam &amp; Barry's Team at RE/MAX Professionals in Lawton. If you are "
                  "PCSing in and have questions about the process, the timeline, or a specific house, call or text. "
                  "It costs nothing to ask, and there is no obligation to work with me.", subj,
                  'Start with the <a href="/">Fort Sill guide</a> or the <a href="/bah/">BAH calculator</a>.')
            + "\n</main>\n\n" + MORETOOLS
            + footer(FOOT_AREA, "Information current as of October 2026.", subj, scripts=("live",)))


def sitemap(urls):
    p = os.path.join(ROOT, "sitemap.xml")
    xml = open(p, encoding="utf-8").read()
    add = ""
    for canon, prio, freq in urls:
        if "<loc>%s</loc>" % canon in xml:
            continue
        add += ("  <url>\n    <loc>%s</loc>\n    <lastmod>%s</lastmod>\n    <changefreq>%s</changefreq>\n"
                "    <priority>%s</priority>\n  </url>\n" % (canon, TODAY, freq, prio))
    if add:
        xml = xml.replace("</urlset>", add + "</urlset>")
        write("sitemap.xml", xml)
    return add.count("<url>")


def patch_bah_index():
    """Keeps the table on /bah/ in step with bah.BAH: every rate links to its own page and the
    'buys about' columns are live spans. Safe to run again."""
    p = os.path.join(ROOT, "bah", "index.html")
    s = open(p, encoding="utf-8").read()
    m = re.search(r"(<caption>Fort Sill / Lawton, OK military housing area\..*?</thead>\s*<tbody>)(.*?)(</tbody>)", s, re.S)
    if not m:
        raise SystemExit("bah/index.html: could not find the rate table")
    groups = {"E-1 to E-4": "Enlisted", "W-1": "Warrant officer", "O-1E": "Officer, prior enlisted", "O-1": "Officer"}
    rows = "\n"
    for label, w, wo, _k in bah.BAH:
        if label in groups:
            rows += '      <tr class="grp"><td colspan="5">%s</td></tr>\n' % groups[label]
        rows += ('      <tr><td>%s</td><td class="num"><a href="%s">%s</a></td><td class="num">%s</td>'
                 '<td class="num"><a href="%s">%s</a></td><td class="num">%s</td></tr>\n' % (
                     label, bah.url(label, True), bah.money(w), expand("{{price budget=%d}}" % w),
                     bah.url(label, False), bah.money(wo), expand("{{price budget=%d}}" % wo)))
    s = s[:m.start(2)] + rows + "    " + s[m.end(2):]
    intro = re.compile(r"<p>Purchase prices below assume a VA loan at .*?</p>", re.S)
    new_intro = expand("<p>Purchase prices below assume a VA loan at {{rate}}, the Freddie Mac average as of "
                       "{{ratedate}}, with nothing down, a 2.15% funding fee financed into the loan, and Lawton tax "
                       "and insurance. Rates move, and these numbers move with them. Each rate links to a page for "
                       "that pay grade. Use the calculator above for your own numbers.</p>")
    if not intro.search(s):
        raise SystemExit("bah/index.html: could not find the table intro")
    s = intro.sub(lambda _m: new_intro, s, count=1)
    tag = '<script src="../assets/guide-live.js?v=%s" defer></script>\n' % JS_V
    if "guide-live.js" not in s:
        s = s.replace('<script src="../assets/track.js" defer></script>', tag + '<script src="../assets/track.js" defer></script>')
    if "guide-live.js" not in s:
        raise SystemExit("bah/index.html: could not add guide-live.js")
    write("bah/index.html", s)


def main():
    n = 0
    urls = []
    for rel, page, canon, _title in bah.build():
        write(rel, page)
        urls.append((canon, "0.7", "monthly"))
        n += 1
    live, queued = build_articles()
    for rel, page, canon, _a in live:
        write(rel, page)
        urls.append((canon, "0.8", "monthly"))
        n += 1
    write("guides/index.html", hub(live))
    urls.append((SITE + "/guides/", "0.8", "weekly"))
    qdir = os.path.join(ROOT, "_queue")
    os.makedirs(qdir, exist_ok=True)
    for fn in os.listdir(qdir):
        if re.match(r"\d+--.*\.html$", fn):
            os.remove(os.path.join(qdir, fn))
    for name, text in queued:
        write("_queue/" + name, text)
    patch_bah_index()
    added = sitemap(urls)
    print("pages written: %d, hub: 1, queued: %d, sitemap urls added: %d" % (n, len(queued), added))


if __name__ == "__main__":
    main()
