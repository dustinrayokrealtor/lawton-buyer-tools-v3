"""Shared pieces for the page generator: site chrome, the payment math, and
the {{token}} expander that prints rate-dependent numbers as live spans.

The math here must stay identical to assets/guide-live.js and to the BAH
calculator on /bah/ (VA loan, nothing down, funding fee financed, Lawton tax
and insurance)."""
import html
import json
import math
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)                      # repo root
SITE = "https://movingtoftsill.com"
CSS_V = "2"                                       # assets/guide.css?v=
V5 = "1"
SHARE_V = "1"                                    # assets/share.js?v=                                          # assets/v5.css?v= and assets/tools.js?v=
JS_V = "1"                                        # assets/guide-live.js?v=
SITE_V = "4"                                      # site.css / palette / leadform version already on the site
ENDPOINT = "https://script.google.com/macros/s/AKfycbwSkkgNvZqNTFDnO9jp5sIiXGEer16rfLo08lX2XEH41uk5IcsiAI7GPcQ3n-Jxdi2d/exec"

TAX_RATE = 0.0111
INS_PER_K = 19.28
FF_DEFAULT = 2.15

with open(os.path.join(ROOT, "data", "market.json")) as _f:
    MARKET = json.load(_f)
RATE = float(MARKET["rate"]["value"])
RATE_ASOF = MARKET["rate"]["asOf"]
MEDIAN = float(MARKET["market"]["medianPrice"])
DOM = MARKET["market"]["daysOnMarket"]
SUPPLY = MARKET["market"]["monthsSupply"]


# ---------------------------------------------------------------- math
def factor(pct):
    i = pct / 100 / 12
    if i <= 0:
        return 1 / 360
    g = (1 + i) ** 360
    return i * g / (g - 1)


def per_dollar(ff=FF_DEFAULT, rate=None):
    rate = RATE if rate is None else rate
    return (1 + ff / 100) * factor(rate) + TAX_RATE / 12 + INS_PER_K / 12000


def price_for(budget, ff=FF_DEFAULT):
    return budget / per_dollar(ff)


def parts(price, ff=FF_DEFAULT):
    loan = price * (1 + ff / 100)
    pi = loan * factor(RATE)
    tax = price * TAX_RATE / 12
    ins = price * INS_PER_K / 12000
    return {"loan": loan, "pi": pi, "tax": tax, "ins": ins, "total": pi + tax + ins}


def jsround(x):
    """Math.round: halves go up."""
    return int(math.floor(x + 0.5))


def usd(n):
    return "${:,}".format(jsround(n))


def short_date(iso):
    y, m, d = iso.split("-")
    return "%d/%d/%s" % (int(m), int(d), y[2:])


def gapline(budget, ff=FF_DEFAULT):
    d = parts(MEDIAN, ff)["total"] - budget
    if d > 0:
        return "That is about %s a month short of the payment on a median-priced house." % usd(d)
    return "That covers the payment on a median-priced house with about %s a month to spare." % usd(-d)


def live_value(kind, a):
    ff = float(a.get("ff", FF_DEFAULT))
    budget = float(a["budget"]) if "budget" in a else None
    price = None
    if "price" in a:
        price = MEDIAN if a["price"] == "median" else float(a["price"])
    part = a.get("part", "total")
    if kind == "rate":
        return "%.2f%%" % RATE
    if kind == "ratedate":
        return short_date(RATE_ASOF)
    if kind == "median":
        return usd(MEDIAN)
    if kind == "dom":
        return str(jsround(DOM))
    if kind == "supply":
        return "%.1f" % SUPPLY
    if kind == "price":
        return usd(math.floor(price_for(budget, ff) / 100) * 100)
    if kind == "pay":
        if budget is not None:
            price = price_for(budget, ff)
        return usd(parts(price, ff)[part])
    if kind == "share":
        return "%d%%" % jsround(price_for(budget, ff) / MEDIAN * 100)
    if kind == "gap":
        return usd(abs(parts(MEDIAN, ff)["total"] - budget))
    if kind == "gapline":
        return gapline(budget, ff)
    if kind == "per100":
        return usd(jsround(100 / per_dollar(ff) / 100) * 100)
    raise ValueError("unknown live kind: " + kind)


TOKEN = re.compile(r"\{\{\s*([a-z0-9]+)((?:\s+[a-z]+=[^\s}]+)*)\s*\}\}")


def expand(text, plain=False):
    """{{price budget=1233}} -> <span data-live="price" data-budget="1233">$126,200</span>.
    plain=True returns just the number (for JSON-LD and meta tags)."""
    def sub(m):
        kind = m.group(1)
        a = dict(kv.split("=", 1) for kv in m.group(2).split())
        val = live_value(kind, a)
        if plain:
            return val
        attrs = "".join(' data-%s="%s"' % (k, html.escape(v)) for k, v in sorted(a.items()))
        return '<span data-live="%s"%s>%s</span>' % (kind, attrs, html.escape(val))
    return TOKEN.sub(sub, text)


def strip_tags(s):
    return html.unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", s))).strip()


# ---------------------------------------------------------------- chrome
PHONE_SVG = '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72c.127.96.362 1.903.7 2.81a2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45c.907.338 1.85.573 2.81.7A2 2 0 0 1 22 16.92z"/></svg>'
PHONE_SVG_BTN = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 16.9v3a2 2 0 0 1-2.2 2 19.8 19.8 0 0 1-8.6-3.1 19.5 19.5 0 0 1-6-6 19.8 19.8 0 0 1-3.1-8.7A2 2 0 0 1 4.1 2h3a2 2 0 0 1 2 1.7c.1 1 .3 2 .6 2.9a2 2 0 0 1-.4 2.1L8.1 9.9a16 16 0 0 0 6 6l1.2-1.2a2 2 0 0 1 2.1-.4c.9.3 1.9.5 2.9.6a2 2 0 0 1 1.7 2z"/></svg>'
MAIL_SVG_BTN = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 4h16v16H4z"/><path d="M22 6l-10 7L2 6"/></svg>'

HORIZON = """  <svg class="horizon horizon--short" viewBox="0 0 1600 410" preserveAspectRatio="none" aria-hidden="true">
  <defs><linearGradient id="sky-g" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#272D3E"/><stop offset="0.28" stop-color="#4F5866"/><stop offset="0.62" stop-color="#B7BFBE"/><stop offset="0.8" stop-color="#C9CFC9"/></linearGradient></defs>
  <rect width="1600" height="410" fill="url(#sky-g)"/>
  <g transform="translate(0,150)">
  <path fill="#56707E" d="M0 170 L134 165 Q250 130 368 80 Q430 58 480 50 L535 44 L636 44 Q690 62 714 80 Q780 118 814 135 L870 143 L948 135 L1004 147 L1070 150 L1150 138 L1215 112 L1250 108 L1285 128 L1310 138 L1340 130 L1400 98 L1445 86 L1490 100 L1561 143 L1600 155 L1600 260 L0 260Z"/>
  <path fill="#7C8F97" d="M0 200 C80 196 140 186 200 184 C270 182 320 192 390 190 C460 188 520 176 600 176 C680 176 740 188 820 190 C900 192 960 180 1040 178 C1120 176 1180 188 1260 186 C1340 184 1400 176 1470 178 C1530 180 1570 190 1600 192 L1600 260 L0 260Z"/>
  <path fill="#B9948A" d="M0 224 C120 220 220 212 340 214 C460 216 560 226 700 224 C840 222 940 212 1080 214 C1220 216 1320 226 1440 224 C1520 222 1570 220 1600 220 L1600 260 L0 260Z"/>
  <path fill="#D9B893" d="M0 244 L1600 244 L1600 260 L0 260Z"/>
  </g>
</svg>"""

# The tool bar. Same eight links, in this order, on every page of the site.
NAV = [("/", "Fort Sill Guide", "guide"), ("/tools/", "All Tools", "tools"), ("/bah/", "BAH", "bah"),
       ("/payment-toolkit.html", "Payment", "payment"), ("/va-loan-calculator.html", "VA Loan", "va"),
       ("/rent-vs-buy/", "Rent vs Buy", "rentbuy"), ("/property-tax-calculator/", "Property Tax", "tax"),
       ("/guides/", "Guides", "guides")]

# Every tool on the site, for the tools page, the home page and the row at the foot of each page.
# (key, href, short name, one line, kind)
TOOLS = [
    ("bah", "/bah/", "BAH Calculator", "What your Fort Sill housing allowance buys, by pay grade.", "Calculator"),
    ("payment", "/payment-toolkit.html", "Payment Calculator", "The whole monthly payment, with VA, FHA and conventional side by side.", "Calculator"),
    ("va", "/va-loan-calculator.html", "VA Loan Calculator", "Your whole household's income against the two tests a VA lender runs.", "Calculator"),
    ("rentbuy", "/rent-vs-buy/", "Rent vs Buy", "How long you have to stay for buying to beat renting here.", "Calculator"),
    ("tax", "/property-tax-calculator/", "Property Tax Calculator", "The tax on any price in any Comanche County school district.", "Calculator"),
    ("residual", "/va-residual-income-calculator/", "VA Residual Income", "The test that decides close VA files, with the full chart.", "Calculator"),
    ("buydown", "/buydown.html", "Buydown vs Price Cut", "Spend seller help on the price or the rate. See which wins.", "Calculator"),
    ("pcs", "/pcs-timeline/", "PCS Timeline", "Put in your report date and get a dated to-do list.", "Planner"),
    ("buyers", "/buying-guide.html", "Buyer's Guide", "How buying in Lawton goes, start to finish. Prints clean.", "Guide"),
]


def toolchips(current=None):
    links = "".join('<a href="%s"%s>%s</a>' % (href, ' aria-current="page"' if key == current else "", name)
                    for key, href, name, _line, _kind in TOOLS)
    return ('<nav class="toolchips" aria-label="Other tools">\n  <p>Tools</p>\n  <div>%s<a href="/guides/">All guides</a></div>\n</nav>\n'
            % links)

GRADES = ["E-1 to E-4", "E-5", "E-6", "E-7", "E-8", "E-9", "W-1", "W-2", "W-3", "W-4", "W-5",
          "O-1E", "O-2E", "O-3E", "O-1", "O-2", "O-3", "O-4", "O-5", "O-6", "O-7",
          "Retired or veteran", "DoD civilian or contractor", "Other"]


def esc(s):
    return html.escape(s, quote=True)


def head(title, desc, canon, jsonld, og_title=None, robots="index, follow, max-image-preview:large, max-snippet:-1"):
    og_title = og_title or title
    blocks = "\n".join('<script type="application/ld+json">\n%s\n</script>' % json.dumps(j, indent=2, ensure_ascii=False)
                       for j in jsonld)
    return """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{canon}">
<meta name="robots" content="{robots}">
<meta name="theme-color" content="#272D3E">
<meta property="og:site_name" content="Moving to Fort Sill">
<meta property="og:locale" content="en_US">
<meta property="og:type" content="article">
<meta property="og:title" content="{ogt}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{canon}">
<meta property="og:image" content="{site}/og-image.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{ogt}">
<meta name="twitter:description" content="{desc}">
<meta name="twitter:image" content="{site}/og-image.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&family=Playfair+Display:wght@400;500;600&display=swap" rel="stylesheet">
<link rel="icon" type="image/png" href="/team-logo.png">
<link rel="stylesheet" href="/assets/site.css?v={sv}">
<link rel="stylesheet" href="/assets/guide.css?v={cv}">
<link rel="stylesheet" href="/assets/palette-v3.css?v={sv}">
<link rel="stylesheet" href="/assets/v5.css?v={v5}">
{blocks}
</head>
""".format(title=esc(title), desc=esc(desc), canon=canon, robots=robots, ogt=esc(og_title),
           site=SITE, sv=SITE_V, cv=CSS_V, v5=V5, blocks=blocks)


def header(nav_key, mail_subject, body_class="page-article"):
    links = ""
    for href, label, key in NAV:
        cur = ' aria-current="true"' if key == nav_key else ""
        links += '<a href="%s"%s>%s</a>' % (href, cur, label)
    subj = mail_subject.replace(" ", "%20")
    return """<body class="has-sticky %s">

<header class="site site4">
  <div class="hd4">
    <a class="hd4-logos" href="/" aria-label="Moving to Fort Sill, home"><img src="/team-logo.png" alt="Pam and Barry's Real Estate Team" class="pb-logo" width="141" height="180"><span class="rx-chip"><img src="/assets/remax-logo.png" alt="RE/MAX" width="381" height="116"></span></a>
    <div class="hd4-team">
      <b>Pam &amp; Barry's Team <span class="nb">RE/MAX Professionals</span></b>
      <span class="hd4-contact"><a href="tel:+15802488800">(580) 248-8800</a> <i>&middot;</i> <a href="https://www.pamandbarry.com/">pamandbarry.com</a> <i>&middot;</i> <a href="mailto:info@homes-lawton.com">info@homes-lawton.com</a></span>
    </div>
    <div class="hd4-me">
      <span>Dustin Ray, Buyer Specialist</span>
      <a class="hd4-call" href="tel:5808964746">%s580-896-4746</a>
      <a class="hd4-mail" href="mailto:dustin@homes-lawton.com?subject=%s">dustin@homes-lawton.com</a>
    </div>
  </div>
</header>
<nav class="toolnav" aria-label="Tools and guides">
  <div class="tn-in">
    %s
  </div>
</nav>
<script>(function(){var c=document.querySelector(".toolnav [aria-current]");if(c){var r=c.parentNode;if(r.scrollWidth>r.clientWidth)r.scrollLeft=Math.max(0,c.offsetLeft-(r.clientWidth-c.offsetWidth)/2);}})();</script>
""" % (body_class, PHONE_SVG, subj, links)


def hero(crumbs, eyebrow, h1, intro, stamp=None, stats=None):
    c = ""
    for i, (label, href) in enumerate(crumbs):
        if i:
            c += "<i>&rsaquo;</i>"
        c += '<a href="%s">%s</a>' % (href, label) if href else "<span>%s</span>" % label
    st = ""
    if stats:
        st = '\n    <div class="phstats">\n' + "".join(
            "      <div><b>%s</b><span>%s</span></div>\n" % (b, s) for b, s in stats) + "    </div>"
    stamp_html = '\n    <p class="stamp">%s</p>' % stamp if stamp else ""
    return """<div class="pagehero">
  <div class="phin">
    <p class="crumbs">%s</p>
    <span class="eyebrow">%s</span>
    <h1>%s</h1>
    <p class="intro">%s</p>%s%s
  </div>
%s
</div>
""" % (c, eyebrow, h1, intro, stamp_html, st, HORIZON)


def listform(source, head_text, lede, button, sync="price",
             notes_hint="Beds, part of town, a fenced yard, when you need to move"):
    """The short ask used under a calculator: name, email, optional phone, a price ceiling
    that follows the calculator, and the calculator run sent along with it."""
    return """<form class="leadform listform" data-source="{src}" data-phone="optional"{sync} data-scenario action="{ep}" method="post" novalidate>
  <h3 class="lf-head">{h}</h3>
  <p class="lf-lede">{lede}</p>
  <input type="hidden" name="source" value="{src}">
  <input type="hidden" name="kind" value="inquiry">
  <input type="hidden" name="want" value="listings">
  <div class="lf-grid">
    <label class="lf-field"><span>Name</span><input name="name" type="text" autocomplete="name" required></label>
    <label class="lf-field"><span>Email</span><input name="email" type="email" autocomplete="email" inputmode="email" required></label>
    <label class="lf-field"><span>Phone <i>(optional)</i></span><input name="phone" type="tel" autocomplete="tel" inputmode="tel"></label>
    <label class="lf-field"><span>Homes up to</span><input name="maxprice" type="number" min="20000" step="1000" inputmode="numeric"></label>
  </div>
  <label class="lf-field lf-full"><span>Anything I should know <i>(optional)</i></span><textarea name="notes" rows="2" placeholder="{hint}"></textarea></label>
  <div class="lf-hp" aria-hidden="true"><label>Company <input name="company" type="text" tabindex="-1" autocomplete="off"></label></div>
  <div class="lf-err" aria-live="polite"></div>
  <button type="submit" class="lf-go">{btn}</button>
  <p class="lf-fine">It is just me on the other end, Dustin Ray, 580-896-4746. I send these myself. No automated alerts, no cost, no obligation, and I never share your info. If you add a phone number, you&rsquo;re OK with me texting you about homes in your range.</p>
</form>
""".format(src=source, ep=ENDPOINT, h=head_text, lede=lede, btn=button, hint=notes_hint,
           sync=' data-sync-price="%s"' % sync if sync else "")


def leadform(source, head_text, lede, button, checked=("listings",), grade=None, notes_label="Anything else"):
    if grade:
        opts = '<option value="">Pick one</option>' + "".join(
            '<option value="%s"%s>%s</option>' % (g, " selected" if g == grade else "", g) for g in GRADES)
    else:
        opts = '<option value="">Pick one</option>'
    def chk(v, label):
        return '    <label class="lf-chk"><input type="checkbox" name="want" value="%s"%s> %s</label>\n' % (
            v, " checked" if v in checked else "", label)
    h = '  <h3 class="lf-head">%s</h3>\n' % head_text if head_text else ""
    return """<form class="leadform" data-source="{src}" action="{ep}" method="post" novalidate>
{h}  <p class="lf-lede">{lede}</p>
  <input type="hidden" name="source" value="{src}">
  <input type="hidden" name="kind" value="inquiry">
  <div class="lf-grid">
    <label class="lf-field"><span>Name</span><input name="name" type="text" autocomplete="name" required></label>
    <label class="lf-field"><span>Phone</span><input name="phone" type="tel" autocomplete="tel" inputmode="tel" required></label>
    <label class="lf-field"><span>Email</span><input name="email" type="email" autocomplete="email" inputmode="email" required></label>
    <label class="lf-field"><span>Pay grade</span><select name="grade">{opts}</select></label>
    <label class="lf-field"><span>When you report</span><select name="report"><option value="">Not sure yet</option><option value="Already here">Already here</option></select></label>
  </div>
  <fieldset class="lf-wants"><legend>Send me</legend>
{c1}{c2}{c3}  </fieldset>
  <label class="lf-field lf-full"><span>{nl} <i>(optional)</i></span><textarea name="notes" rows="2"></textarea></label>
  <div class="lf-hp" aria-hidden="true"><label>Company <input name="company" type="text" tabindex="-1" autocomplete="off"></label></div>
  <div class="lf-err" aria-live="polite"></div>
  <button type="submit" class="lf-go">{btn}</button>
  <p class="lf-fine">I send these myself. No automated alerts, no cost, no obligation, and I never share your info. Sending this means you&rsquo;re OK with me calling or texting the number above about your move.</p>
</form>
""".format(src=source, ep=ENDPOINT, h=h, lede=lede, opts=opts, nl=notes_label, btn=button,
           c1=chk("listings", "Listings in my price range"),
           c2=chk("payment", "My payment broken down"),
           c3=chk("rentcomps", "Rent comps for keeping it as a rental later"))


def cta(h2, lede, mail_subject, foot):
    subj = mail_subject.replace(" ", "%20")
    return """<div class="ctawrap">
  <div class="cta">
    <h2>%s</h2>
    <p class="ctalede">%s</p>
    <div class="btnrow">
      <a class="btn" href="tel:5808964746">
        %s
        Call or text 580-896-4746
      </a>
      <a class="btn alt" href="mailto:dustin@homes-lawton.com?subject=%s">
        %s
        Email me
      </a>
    </div>
    <p class="ctafoot">%s</p>
  </div>
</div>
""" % (h2, lede, PHONE_SVG_BTN, subj, MAIL_SVG_BTN, foot)


MORETOOLS = """<section class="moretools" aria-labelledby="mt-head">
  <h2 id="mt-head" class="mt-head">Tools</h2>
  <div class="mt-grid">
    <a class="mt-card" href="/bah/"><b>BAH Calculator</b><span>What your 2026 Fort Sill housing allowance buys, by pay grade.</span><i>Open &rarr;</i></a>
    <a class="mt-card" href="/payment-toolkit.html"><b>Payment Calculator</b><span>Your full monthly payment, with VA, FHA and conventional side by side.</span><i>Open &rarr;</i></a>
    <a class="mt-card" href="/va-loan-calculator.html"><b>VA Loan Calculator</b><span>Household income, VA residual income, and how much house it supports.</span><i>Open &rarr;</i></a>
    <a class="mt-card" href="/buydown.html"><b>Buydown vs Price Cut</b><span>Spend seller help on a lower price or a lower rate. See which wins.</span><i>Open &rarr;</i></a>
  </div>
</section>
"""

FOOT_AREA = ("This page is general information about the area and the buying process. It is not a recommendation of any "
             "neighborhood, school, or school district, and it is not legal, tax, or lending advice. School district "
             "assignment, utility service, taxes, and property condition vary by address and must be verified for the "
             "specific property. Gate hours, access requirements, allowances, and installation policies are set by "
             "Fort Sill and the Department of Defense and change without notice. Payment figures are estimates for "
             "planning and are not a loan offer, a commitment to lend, or a guarantee of terms or eligibility.")
FOOT_BAH = ("Every figure on this page is an estimate for planning purposes and is not a loan offer, a commitment to "
            "lend, or a guarantee of terms. Interest rates change daily. The rate used here is the Freddie Mac weekly "
            "average, which is not a quote. Property tax, insurance, and qualification depend on the specific property, "
            "your credit, your debts, and your lender's underwriting. BAH and BAS rates shown are the published 2026 "
            "figures for the Fort Sill / Lawton military housing area and should be confirmed against your LES or the "
            "official Department of Defense calculator. Whether an allowance can be counted as qualifying income is "
            "determined by your lender.")


def footer(disclaimer, stamp, mail_subject, scripts=("leadform", "live"), inline=""):
    subj = mail_subject.replace(" ", "%20")
    s = ""
    if "tools" in scripts:
        s += '<script src="/assets/share.js?v=%s"></script>\n' % SHARE_V
        s += '<script src="/assets/tools.js?v=%s"></script>\n' % V5
    if inline:
        s += "<script>\n%s\n</script>\n" % inline.strip()
    if "leadform" in scripts:
        s += '<script src="/assets/leadform.js?v=%s" defer></script>\n' % SITE_V
    if "live" in scripts:
        s += '<script src="/assets/guide-live.js?v=%s" defer></script>\n' % JS_V
    s += '<script src="/assets/track.js" defer></script>\n'
    return """<footer class="site">
  <div class="wrap">
    <p class="eiooo">Each Office Independently Owned and Operated.</p>
    <p>Pam &amp; Barry's Team RE/MAX Professionals &middot; <a href="tel:+15802488800">(580) 248-8800</a> &middot; <a href="https://www.pamandbarry.com/">pamandbarry.com</a> &middot; <a href="mailto:info@homes-lawton.com">info@homes-lawton.com</a></p>
    <p>Dustin Ray, Buyer Specialist, Pam &amp; Barry's Team RE/MAX Professionals. Oklahoma real estate license #213324. Office on NW Elm Ave, Lawton, Oklahoma. 580-896-4746. dustin@homes-lawton.com</p>
    <p>%s</p>
    <p>This page is not affiliated with, endorsed by, or sponsored by the United States Army, the Department of Defense, the Department of Veterans Affairs, or any government agency.</p>
    <p>We are pledged to the letter and spirit of U.S. policy for the achievement of equal housing opportunity throughout the nation. We encourage and support an affirmative advertising and marketing program in which there are no barriers to obtaining housing because of race, color, religion, sex, handicap, familial status, or national origin.</p>
    <p>&copy; <span id="yr">2026</span> Dustin Ray. %s</p>
  </div>
</footer>

<div class="stickybar">
  <a href="tel:5808964746">%s</a>
  <a class="alt" href="mailto:dustin@homes-lawton.com?subject=%s"><svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M4 4h16v16H4z"/><path d="m22 6-10 7L2 6"/></svg>Email</a>
</div>

%s</body>
</html>
""" % (disclaimer, stamp, PHONE_SVG.replace('width="15" height="15"', 'width="17" height="17"') + "Call / Text", subj, s)


def breadcrumb_ld(items):
    return {"@context": "https://schema.org", "@type": "BreadcrumbList",
            "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": n, "item": u}
                                for i, (n, u) in enumerate(items)]}


def faq_ld(faqs):
    return {"@context": "https://schema.org", "@type": "FAQPage",
            "mainEntity": [{"@type": "Question", "name": strip_tags(expand(q, True)),
                            "acceptedAnswer": {"@type": "Answer", "text": strip_tags(expand(a, True))}}
                           for q, a in faqs]}


def article_ld(headline, desc, url, published, modified=None):
    return {"@context": "https://schema.org", "@type": "Article", "headline": headline, "description": desc,
            "image": SITE + "/og-image.png",
            "author": {"@type": "Person", "name": "Dustin Ray", "url": SITE + "/"},
            "publisher": {"@id": SITE + "/#agent"},
            "datePublished": published, "dateModified": modified or published,
            "mainEntityOfPage": {"@type": "WebPage", "@id": url}}


def faq_html(faqs):
    out = '<section class="block faq">\n  <h2>Common questions</h2>\n'
    for q, a in faqs:
        out += "  <h3>%s</h3>\n  <p>%s</p>\n" % (expand(q), expand(a))
    return out + "</section>\n"
