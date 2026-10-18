"""The two front doors: the home page (/) and the tools page (/tools/).
Both are short on purpose. A visitor should see every tool and every topic
without scrolling far, pick one, and go. The long versions live on their own
pages under /fort-sill/ and /guides/.

The tool tiles come from common.TOOLS, so a new tool shows up here, in the row
at the foot of every page, and on /tools/ from one list."""
import json
import os

from common import HERE, HORIZON, SITE, TOOLS, breadcrumb_ld, footer, head, header, leadform

FOOT_HOME = ("This guide is general information about the area and is not a recommendation of any neighborhood, school, "
             "or school district. School district assignment, utility service, and property condition vary by address "
             "and must be verified for the specific property. Gate hours, access requirements, and installation "
             "policies are set by Fort Sill and change without notice. Nothing here is a loan offer, a commitment to "
             "lend, or a guarantee of terms or eligibility.")
FOOT_TOOLS = ("Every figure these tools produce is an estimate for planning. None of it is a loan offer, a commitment to "
              "lend, a tax bill, or tax or legal advice. Rates, taxes, insurance, allowances and program rules are set "
              "by third parties and change. Your lender has the real numbers.")


def tiles(keys=None, cls="hubgrid tight"):
    out = '<ul class="%s">\n' % cls
    for key, href, name, line, kind in TOOLS:
        if keys and key not in keys:
            continue
        out += '      <li><a href="%s"><b>%s</b><span>%s</span><i>%s</i></a></li>\n' % (href, name, line, kind)
    return out + "    </ul>"


def topic(title, body, links):
    go = "".join('<a href="%s">%s &rarr;</a>' % (h, t) for h, t in links)
    return '    <div class="topic">\n      <h3>%s</h3>\n      %s\n      <p class="go">%s</p>\n    </div>\n' % (title, body, go)


def home():
    ld = json.load(open(os.path.join(HERE, "home-ld.json"), encoding="utf-8"))
    title = "Moving to Fort Sill | Housing & Area Guide for Lawton, OK"
    desc = ("Moving to Fort Sill? A straight guide to the Lawton area: gate commutes, school districts, where the "
            "affordable homes are, and what to do when you PCS out.")
    subj = "Moving to Fort Sill"
    hero = """<div class="pagehero hubhero">
  <div class="phin">
    <span class="eyebrow">For incoming Fort Sill families</span>
    <h1>Moving to Fort Sill</h1>
    <p class="intro">Straight answers about the Lawton area, and calculators that run on the real local numbers. Pick what you came for.</p>
    <p class="hublabel">Run your numbers</p>
    %s
  </div>
%s
</div>
""" % (tiles().replace("    </ul>", '      <li><a href="/guides/"><b>Guides</b><span>The area, VA loans, closing costs, and every BAH rate.</span><i>Reading</i></a></li>\n    </ul>'), HORIZON)

    topics = "".join([
        topic("Getting on post",
              "<p>Fort Sill has six gates and they do not all run the same hours. Do not plan your commute around "
              "published gate hours. They change constantly. The My Army Post app carries current gate status. "
              "Any adult without a military ID needs a pass from the Visitor Welcome Center by Bentley Gate, so sort "
              "that out before family shows up to help you move in.</p>",
              [("/fort-sill/gates-and-commute/", "All six gates and the drive from each side of town")]),
        topic("School districts",
              "<p>Five districts cover most of where Fort Sill families buy: Lawton, Elgin, Cache, Fletcher and "
              "Geronimo. The district follows the address, not the mailing city, and Medicine Park is split between "
              "two. I do not rate schools. I will tell you exactly which district serves any address you are looking "
              "at.</p>",
              [("/fort-sill/school-districts/", "Which district serves which address")]),
        topic("The towns outside Lawton",
              "<p>A lot of families end up outside Lawton proper. The tradeoff is mostly price and drive time.</p>\n"
              "      <ul>\n"
              '        <li><a href="/fort-sill/elgin/">Elgin</a>, north, off I-44. Newer houses, its own district.</li>\n'
              '        <li><a href="/fort-sill/cache/">Cache</a>, west on Highway 62. Its own district.</li>\n'
              '        <li><a href="/fort-sill/geronimo/">Geronimo</a>, south. A lot of new construction, still a small town.</li>\n'
              '        <li><a href="/fort-sill/fletcher/">Fletcher</a>, northeast. Farther out, more land for the money.</li>\n'
              '        <li><a href="/fort-sill/medicine-park/">Medicine Park</a>, a cobblestone resort town at the edge of the Wichitas.</li>\n'
              "      </ul>", []),
        topic("What your allowance shops",
              "<p>Before you fall for a house, get the number straight. Lawton property tax runs about 1.1% to 1.2% of "
              "value a year and insurance about $19.28 per $1,000 of coverage. Those two lines move a payment more "
              "than most people expect. If you draw VA disability pay, the funding fee is waived. At a 100% permanent "
              "rating, Oklahoma exempts a resident's homestead from property tax.</p>",
              [("/bah/", "What your BAH buys"), ("/property-tax-calculator/", "Property tax by district")]),
        topic("Buying before you get here",
              "<p>You do not have to wait until you report. With orders in hand a lender can qualify you on your "
              "Fort Sill allowance. I send listings and walk houses on video. Inspections and the appraisal happen "
              "while you are still in transit, and plenty of families close within a week or two of arriving.</p>",
              [("/fort-sill/buying-before-you-arrive/", "Step by step"), ("/pcs-timeline/", "Build your PCS timeline")]),
        topic("Rent, buy, or keep it when you leave",
              "<p>There is a built-in rental market here. The post cycles people through constantly, so there is "
              "steady demand for houses near it. Plenty of families buy, live in it for a tour, and keep it as a "
              "rental when they PCS out. A single-family house rents for somewhere around $1,200 to $1,300 a month. "
              "Run it on the actual house before you count on it.</p>",
              [("/rent-vs-buy/", "Rent vs buy calculator"), ("/fort-sill/rent-it-out-when-you-pcs/", "Keeping the house")]),
        topic("The move itself",
              "<p>The movers, your weight allowance, what the Army pays for, where to report, and the Oklahoma list: "
              "tags, licenses, taxes, pets. Start with the transportation office the day you get orders.</p>",
              [("/fort-sill/pcs-checklist/", "Fort Sill PCS checklist")]),
        topic("The money side",
              "<p>Nothing down does not mean nothing at closing. How a VA loan works in Oklahoma, what closing costs "
              "run here, which parts a seller usually covers, and why the insurance line is bigger than people "
              "expect.</p>",
              [("/guides/va-loan-oklahoma/", "VA loans in Oklahoma"), ("/guides/closing-costs-oklahoma/", "Closing costs")]),
        topic("The thing nobody tells you about",
              "<p>The Wichita Mountains Wildlife Refuge sits about fifteen minutes from post. Roughly 59,000 acres of "
              "granite mountains, prairie, and lakes, with free-roaming bison, longhorn, and elk. A road runs to "
              "the top of Mount Scott when it is open. It is free. People stationed here for three years sometimes go twice. Go more "
              "than that.</p>", []),
    ]).replace('<p class="go"></p>\n', "")

    form = leadform("where-people-look", None,
                    "Tell me your range and I will pull everything listed in it across all of these and send it over, "
                    "so you are comparing actual houses.", "Send me the list")
    main = """<main class="hubwrap">

<section id="honest" class="block">
  <h2>The honest part first</h2>
  <div class="two">
    <div>
      <p>You have probably heard some things about Lawton. Somebody at your last duty station had an opinion, or you went down a thread about it at two in the morning.</p>
      <p>Here is the straight answer. Lawton is a real city and it has real growing pains. It is not a suburb and it does not pretend to be. What it also has is a military community that has been here since 1869 and a support system built around it, which is not something you find in most places this size.</p>
      <p>I am not going to tell you a neighborhood is safe or unsafe. That is not my call to make. What I will do is point you at the same sources for every town so you can read the numbers yourself. Resale and appreciation are different. That is market data, and I will show you the actual numbers on any addresses you are comparing.</p>
    </div>
    <div class="note">
      <div class="ntext">
        <p><strong>Where to look up crime data for any town</strong></p>
        <ul>
          <li><a href="https://cde.ucr.cjis.gov/" rel="nofollow noopener" target="_blank">FBI Crime Data Explorer</a>, the reported data by agency</li>
          <li><a href="https://www.safewise.com/research/safest-cities/oklahoma/" rel="nofollow noopener" target="_blank">SafeWise Oklahoma rankings</a>, cities sorted by reported crime per 1,000 residents</li>
          <li>The police department for the specific city, which publishes local reports and answers questions from the public</li>
        </ul>
        <p>Use the same three for every place you look at. Small towns have small numbers, so one incident can move a rate a long way. Look at more than one year before you conclude anything.</p>
      </div>
    </div>
  </div>
</section>

<section id="guide" class="block">
  <h2>What to know before you pick a house</h2>
  <div class="topics">
%s  </div>
  <p class="tnote">Every one of these has a longer page. They are all listed under <a href="/guides/">Guides</a>, along with VA loans, closing costs, and every 2026 BAH rate by pay grade.</p>
</section>

<section id="where" class="block">
  <h2>Where people actually look</h2>
  <div class="two">
    <div>
      <p>If you are shopping in the $130,000 to $175,000 range, which is where most enlisted allowances land, there are a handful of places that often have houses in that band.</p>
      <div class="pillrow">
        <span class="pill">Crosby Park <b>&middot; Lawton</b></span>
        <span class="pill">Fields and Dunning <b>&middot; Lawton</b></span>
        <span class="pill">MacArthur Park <b>&middot; Lawton</b></span>
        <span class="pill">Sungate <b>&middot; Lawton</b></span>
        <span class="pill">Cache <b>&middot; west of town</b></span>
        <span class="pill">Geronimo <b>&middot; south of town</b></span>
      </div>
      <p>That list moves with the market. Two of those areas have houses in your band some months and nothing in it other months. It is a starting point for a search. I am not ranking these or telling you which one is nicer. Drive them, look at the houses, and use the <a href="#honest">data sources above</a> if you want numbers.</p>
    </div>
    <div>
%s    </div>
  </div>
</section>

</main>
""" % (topics, form)

    return (head(title, desc, SITE + "/", ld, og_title="Moving to Fort Sill")
            + header("guide", subj, "page-home")
            + hero + "\n" + main
            + footer(FOOT_HOME, "Area information current as of October 2026.", subj, scripts=("leadform",)))


def toolshub():
    canon = SITE + "/tools/"
    title = "Fort Sill & Lawton Home Buyer Tools | Free Calculators"
    desc = ("Free home buying calculators for Fort Sill and Lawton: BAH, VA loans, rent vs buy, property tax, and "
            "payments built on real Comanche County numbers.")
    subj = "Lawton Buyer Tools"
    ld = [breadcrumb_ld([("Moving to Fort Sill", SITE + "/"), ("Fort Sill & Lawton Home Buyer Tools", canon)]),
          {"@context": "https://schema.org", "@type": "ItemList", "name": "Fort Sill and Lawton home buyer tools",
           "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": name,
                                "url": SITE + href} for i, (_k, href, name, _l, _kind) in enumerate(TOOLS)]}]
    hero = """<div class="pagehero hubhero">
  <div class="phin">
    <p class="crumbs"><a href="/">Moving to Fort Sill</a><i>&rsaquo;</i><span>Tools</span></p>
    <h1>Lawton Buyer Tools</h1>
    <p class="intro">The tools I use with every buyer. They run on real local numbers, so what you see here is close to what the lender will see. Use them as much as you want. No sign-up.</p>
  </div>
%s
</div>
""" % HORIZON
    calc = [k for k, _h, _n, _l, kind in TOOLS if kind == "Calculator"]
    other = [k for k, _h, _n, _l, kind in TOOLS if kind != "Calculator"]
    more = ('      <li><a href="/"><b>Moving to Fort Sill</b><span>Gates, school districts, the towns, and the honest '
            'version of the tradeoffs.</span><i>Guide</i></a></li>\n'
            '      <li><a href="/guides/"><b>All Guides</b><span>VA loans, closing costs, the area pages, and every '
            'BAH rate by pay grade.</span><i>Guides</i></a></li>\n')
    main = """<main class="hubwrap">

<section class="block">
  <h2>Calculators</h2>
  %s
</section>

<section class="block">
  <h2>Planners and guides</h2>
  %s
  <p class="tnote">Want to talk it through? Call or text me at <a href="tel:5808964746">580-896-4746</a>. If I do not pick up I am probably at a showing, and I will get right back to you.</p>
</section>

</main>
""" % (tiles(calc, "hubgrid"), tiles(other, "hubgrid").replace("    </ul>", more + "    </ul>"))
    return (head(title, desc, canon, ld, og_title="Fort Sill & Lawton Home Buyer Tools")
            + header("tools", subj, "page-tools")
            + hero + "\n" + main
            + footer(FOOT_TOOLS, "Local figures current as of October 2026.", subj, scripts=()))


def build():
    return [("index.html", home()), ("tools/index.html", toolshub())]
