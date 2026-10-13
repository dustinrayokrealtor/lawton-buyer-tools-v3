"""The pay grade pages under /bah/: one page per grade, with and without
dependents. UPDATE THE TABLE BELOW EVERY JANUARY when DoD publishes the new
rates (and the year, BAS and the weight table if they changed), then run
`python3 _build/gen.py` from the repo root. The articles that quote BAH rates
(the price-point guides and the yearly BAH article) pull from this table, but
read _build/content/guides/fort-sill-bah-2027.html again in January: its text
talks about the changeover and needs a human pass."""
import os

from common import (FOOT_BAH, MORETOOLS, ROOT, SITE, breadcrumb_ld, cta, esc, expand, faq_html, faq_ld,
                    footer, head, header, hero, leadform)

YEAR = 2026
PUBLISHED = "2026-10-12"

# 2026 BAH, Fort Sill / Lawton OK military housing area. Source: DTMO.
# (label, with dependents, without dependents, E or O for the BAS rate)
BAH = [
    ("E-1 to E-4", 1203, 969, "E"),
    ("E-5", 1233, 1092, "E"),
    ("E-6", 1494, 1170, "E"),
    ("E-7", 1587, 1209, "E"),
    ("E-8", 1692, 1290, "E"),
    ("E-9", 1842, 1383, "E"),
    ("W-1", 1509, 1206, "O"),
    ("W-2", 1632, 1287, "O"),
    ("W-3", 1761, 1386, "O"),
    ("W-4", 1872, 1509, "O"),
    ("W-5", 2013, 1611, "O"),
    ("O-1E", 1605, 1230, "O"),
    ("O-2E", 1740, 1344, "O"),
    ("O-3E", 1893, 1482, "O"),
    ("O-1", 1272, 1167, "O"),
    ("O-2", 1491, 1227, "O"),
    ("O-3", 1758, 1395, "O"),
    ("O-4", 2055, 1587, "O"),
    ("O-5", 2271, 1704, "O"),
    ("O-6", 2286, 1740, "O"),
    ("O-7", 2298, 1767, "O"),
]
BAS = {"E": 476.95, "O": 328.48}

# Household goods weight allowance in pounds (Joint Travel Regulations): with, without dependents.
WEIGHT = {
    "E-5": (9000, 7000), "E-6": (11000, 8000), "E-7": (13000, 11000), "E-8": (14000, 12000),
    "E-9": (15000, 13000),
    "W-1": (12000, 10000), "W-2": (13500, 12500), "W-3": (14500, 13000), "W-4": (17000, 14000),
    "W-5": (17500, 16000),
    "O-1E": (12000, 10000), "O-2E": (13500, 12500), "O-3E": (14500, 13000),
    "O-1": (12000, 10000), "O-2": (13500, 12500), "O-3": (14500, 13000), "O-4": (17000, 14000),
    "O-5": (17500, 16000), "O-6": (18000, 18000), "O-7": (18000, 18000),
}

RENT_LO, RENT_HI = 1200, 1300      # single-family rent in Lawton, per month


def slug(label, deps):
    return label.lower().replace(" ", "-") + ("-with-dependents" if deps else "-without-dependents")


def url(label, deps):
    return "/bah/%s/" % slug(label, deps)


def money(n):
    return "${:,}".format(n)


def money2(n):
    return "${:,.2f}".format(n)


def who(label, deps, cap=True):
    d = " with dependents" if deps else " without dependents"
    if label == "E-1 to E-4":
        s = "a soldier E-1 through E-4" + d
    else:
        s = ("a " if label.startswith("W") else "an ") + label + d
    return s[0].upper() + s[1:] if cap else s


def grade_page(label, w, wo, kind):
    pages = []
    for deps in (True, False):
        bah = w if deps else wo
        other = wo if deps else w
        dtxt = "with dependents" if deps else "without dependents"
        otxt = "without dependents" if deps else "with dependents"
        bas = BAS[kind]
        canon = SITE + url(label, deps)
        if deps:
            title = "%s BAH at Fort Sill %d: %s and What It Buys%s" % (
                label, YEAR, money(bah), "" if len(label) > 4 else " in Lawton")
        else:
            title = "%s BAH Without Dependents, Fort Sill %d: %s" % (label, YEAR, money(bah))
        desc = ("%d Fort Sill BAH for %s is %s a month. See what that buys in Lawton with a VA loan, "
                "using real local tax and insurance." % (YEAR, who(label, deps, cap=False), money(bah)))
        h1 = "%s BAH at Fort Sill: %s %s" % (label, money(bah), dtxt)
        crumbs = [("Moving to Fort Sill", "/"), ("BAH", "/bah/"), ("%s %s" % (label, dtxt), None)]
        intro = ("That is the %d rate for the Fort Sill / Lawton housing area. Here is what it buys in Lawton "
                 "with a VA loan, figured on real Comanche County tax and insurance numbers." % YEAR)
        stamp = expand("Rates effective January 1, %d. Payment math at {{rate}}, the Freddie Mac average "
                       "as of {{ratedate}}." % YEAR)
        stats = [
            (money(bah), "%s BAH %s, per month" % (label, dtxt)),
            (expand("{{price budget=%d}}" % bah), "What it carries with a VA loan and nothing down"),
            (expand("{{share budget=%d}}" % bah), expand("Of Lawton's {{median}} median sale price")),
            (money2(bas), "BAS for %s in %d, on top of BAH" % ("enlisted" if kind == "E" else "officers", YEAR)),
        ]

        # ---- the rate
        s1 = '<section class="block">\n  <h2>The rate</h2>\n'
        s1 += ("  <p>%s at Fort Sill draws <strong>%s a month</strong> in BAH in %d. "
               "<a href=\"%s\">%s it is %s</a>.</p>\n" % (who(label, deps), money(bah), YEAR,
                                                            url(label, not deps), otxt.capitalize(), money(other)))
        s1 += ("  <p>BAH is tax free and it follows the duty station. The published rate is the same for everyone at "
               "your grade and dependency status, whether they rent or buy.</p>\n")
        if not deps and label in ("E-1 to E-4", "E-5"):
            s1 += ('  <div class="note warn"><div class="ntext"><p><strong>Check this first.</strong> Single soldiers '
                   "E-5 and below normally live in the barracks at Fort Sill and do not draw BAH unless the command "
                   "authorizes it. If that is you, get that sorted before you plan around this number.</p></div></div>\n")
        s1 += ("  <p>If the rate drops next year you keep the higher number for as long as you stay at Fort Sill at "
               "the same grade and dependency status. That is called rate protection. New arrivals get the current "
               "year's rate. DoD usually publishes next year's rates in mid-December and they start January 1.</p>\n")
        s1 += "</section>\n"

        # ---- what it buys
        b = "budget=%d" % bah
        s2 = '<section class="block alt">\n  <h2>What %s buys in Lawton</h2>\n' % money(bah)
        s2 += expand("""  <div class="result">
    <div class="rlabel">Purchase price %s a month carries</div>
    <div class="rbig">{{price %s}}</div>
    <div class="rsub">VA loan, nothing down, {{rate}} on a 30 year fixed</div>
    <div class="breakdown">
      <div class="brow"><span>Loan amount, funding fee included</span><span>{{pay %s part=loan}}</span></div>
      <div class="brow"><span>Principal and interest</span><span>{{pay %s part=pi}}</span></div>
      <div class="brow"><span>Property tax</span><span>{{pay %s part=tax}}</span></div>
      <div class="brow"><span>Homeowners insurance</span><span>{{pay %s part=ins}}</span></div>
      <div class="brow tot"><span>Total monthly payment</span><span>%s</span></div>
    </div>
    <p class="rnote">The rate is the Freddie Mac weekly average as of {{ratedate}}, and this number moves with it. <a href="/bah/">Run your own numbers</a> with BAS, disability pay, or a second income.</p>
  </div>
""" % (money(bah), b, b, b, b, b, money(bah)))
        s2 += ("  <p>Property tax is figured at 1.11% of value a year and insurance at $19.28 per $1,000 of coverage. "
               "Those are Lawton numbers. A house you just bought can run a little higher on tax, closer to 1.2% "
               "inside Lawton city limits.</p>\n")
        s2 += expand("  <p>The median sale in Comanche County is {{median}} so far this year. {{gapline %s}} "
                     "Every extra $100 a month you put toward the payment is roughly {{per100}} more house, so base "
                     "pay or a second income moves you up quickly.</p>\n" % b)
        s2 += expand("  <p>If you have a service-connected disability rating of 10%% or higher, the VA funding fee is "
                     "waived and the same %s carries about {{price %s ff=0}}.</p>\n" % (money(bah), b))
        s2 += "</section>\n"

        # ---- BAS
        s3 = '<section class="block">\n  <h2>Adding BAS or base pay</h2>\n'
        s3 += expand("  <p>BAS is %s a month for %s in %d. It is tax free and lenders count it. Put all of it "
                     "toward the payment and the price goes to about {{price budget=%.2f}}.</p>\n" % (
                         money2(bas), "enlisted" if kind == "E" else "officers", YEAR, bah + bas))
        s3 += ("  <p>I would not plan on spending all of it. BAS is your grocery money. What it tells you is that "
               "there is room above the BAH number if you want it. The <a href=\"/bah/\">BAH calculator</a> lets you "
               "run it both ways, and the <a href=\"/va-loan-calculator.html\">VA loan calculator</a> adds base pay "
               "and a spouse's income to the picture.</p>\n")
        s3 += "</section>\n"

        # ---- rent
        s4 = '<section class="block alt">\n  <h2>Renting on the same allowance</h2>\n'
        s4 += ("  <p>A single-family house in Lawton rents for somewhere around %s to %s a month. This is a "
               "single-family-home town on both sides of the deal, so that is the number to compare against.</p>\n" % (
                   money(RENT_LO), money(RENT_HI)))
        if bah < RENT_LO:
            s4 += expand("  <p>At %s your BAH comes in under that, so renting a house means covering the difference "
                         "out of pocket. Buying at about {{price %s}} keeps the whole payment inside your allowance, "
                         "and the principal and interest stay fixed for thirty years.</p>\n" % (money(bah), b))
        elif bah <= RENT_HI:
            s4 += expand("  <p>Your %s lands right in that range. The same money carries about {{price %s}} if you "
                         "buy, and the principal and interest stay fixed for thirty years while rent can go up every lease.</p>\n"
                         % (money(bah), b))
        else:
            s4 += expand("  <p>Your %s is above that range. Put the whole allowance toward a purchase "
                         "and it carries about {{price %s}}, with the principal and interest fixed for thirty "
                         "years.</p>\n" % (money(bah), b))
        s4 += ("  <p>What decides it is usually how long you will be here and what you do with the house when you "
               "leave. Fort Sill turns over enough tenants that <a href=\"/fort-sill/rent-it-out-when-you-pcs/\">"
               "keeping it as a rental</a> works more often than people expect.</p>\n")
        s4 += "</section>\n"

        # ---- PCS numbers
        s5 = '<section class="block">\n  <h2>Other PCS numbers for %s</h2>\n' % who(label, deps, cap=False)
        if label == "E-1 to E-4":
            wt = "8,000 lb" if deps else "7,000 lb for an E-4, 5,000 lb for E-1 through E-3"
        else:
            wt = "{:,} lb".format(WEIGHT[label][0 if deps else 1])
        s5 += """  <div class="tscroll">
  <table>
    <tbody>
      <tr><td>Household goods weight allowance, %s</td><td class="num">%s</td></tr>
      <tr><td>Professional gear, on top of that</td><td class="num">2,000 lb</td></tr>
      <tr><td>BAS, per month</td><td class="num">%s</td></tr>
      <tr><td>Temporary lodging (TLE) on a stateside move</td><td class="num">up to 21 days</td></tr>
    </tbody>
  </table>
  </div>
""" % (dtxt, wt, money2(bas))
        s5 += ("  <p>The weight allowance comes from the Joint Travel Regulations. Confirm yours with the "
               "transportation office when you get counseled. The <a href=\"/fort-sill/pcs-checklist/\">Fort Sill "
               "PCS checklist</a> walks through the move itself.</p>\n</section>\n")

        # ---- form
        src = "bah-" + slug(label, deps).replace("-dependents", "")
        s6 = '<section class="block alt">\n' + leadform(
            src, "Want the houses at this number texted to you?",
            "I&rsquo;ll go through what&rsquo;s listed right now at your number and text you the ones worth a look. "
            "It comes straight from me, and you can text back any time.",
            "Text them to me", checked=("listings",), grade=label) + "</section>\n"

        # ---- questions
        faqs = [
            ("How much is %s BAH at Fort Sill in %d?" % (label, YEAR),
             "%s a month with dependents and %s a month without. Those rates took effect January 1, %d for the "
             "Fort Sill / Lawton military housing area." % (money(w), money(wo), YEAR)),
            ("How much house can %s buy at Fort Sill on BAH alone?" % who(label, deps, cap=False),
             "About {{price %s}} with a VA loan and nothing down at {{rate}}, counting Lawton property tax and "
             "homeowners insurance. Base pay, BAS, or a second income raises that." % b),
            ("Can I use my Fort Sill BAH to qualify before I get there?",
             "Yes. With orders in hand a lender can qualify you on the Fort Sill rate before you report. "
             "Plenty of families close within a week or two of arriving."),
        ]
        s7 = faq_html(faqs)

        # ---- other grades
        s8 = '<section class="block alt">\n  <h2>Other pay grades, %s</h2>\n  <ul class="linkgrid">\n' % dtxt
        for l2, w2, wo2, _k in BAH:
            cur = ' aria-current="page"' if l2 == label else ""
            s8 += '    <li><a href="%s"%s>%s<span>%s a month</span></a></li>\n' % (
                url(l2, deps), cur, l2, money(w2 if deps else wo2))
        s8 += "  </ul>\n"
        s8 += '  <p><a class="readmore" href="/bah/">The full Fort Sill BAH table and calculator &rarr;</a></p>\n</section>\n'

        ld = [breadcrumb_ld([("Moving to Fort Sill", SITE + "/"), ("What Your BAH Buys at Fort Sill", SITE + "/bah/"),
                             ("%s %s" % (label, dtxt), canon)]),
              faq_ld(faqs)]
        subj = "Fort Sill BAH question"
        page = (head(title, desc, canon, ld)
                + header("bah", subj)
                + hero(crumbs, "%d Fort Sill BAH" % YEAR, h1, intro, stamp, stats)
                + '\n<main class="wrap">\n\n' + s1 + s2 + s3 + s4 + s5 + s6 + s7 + s8
                + cta("Want the version with your actual numbers in it?",
                      "I am a buyer specialist with Pam &amp; Barry's Team at RE/MAX Professionals in Lawton. Send me "
                      "your pay grade and your timeline and I will put together what is actually available in your "
                      "range right now. The list costs nothing, and there is no obligation to work with me.",
                      subj,
                      'Want the whole payment picture including FHA, USDA and conventional? Use the '
                      '<a href="/payment-toolkit.html">Buyer Payment Toolkit</a>. New to the area? Start with the '
                      '<a href="/">Fort Sill guide</a>.')
                + "\n</main>\n\n" + MORETOOLS
                + footer(FOOT_BAH, "Market data from Comanche County records and MLS statistics current as of "
                                   "October 2026.", subj))
        pages.append((url(label, deps).strip("/") + "/index.html", page, canon, title))
    return pages


def build():
    out = []
    for label, w, wo, kind in BAH:
        out.extend(grade_page(label, w, wo, kind))
    return out
