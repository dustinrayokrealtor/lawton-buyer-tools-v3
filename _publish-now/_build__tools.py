"""The stand-alone tools: property tax, VA residual income, rent vs buy, and the
PCS timeline. (The VA loan calculator is in vacalc.py.) Each page is the tool
first, a short explanation under it, and one ask. The math they share lives in
assets/tools.js.

UPDATE EACH FALL: the mill levies below, from the Comanche County Assessor's
"Millage Levies" sheet, and LEVY_YEAR."""
import json

from common import (FOOT_AREA, RATE, MEDIAN, SITE, breadcrumb_ld, faq_html, faq_ld, footer, head, header, hero,
                    leadform, listform, toolchips, usd)

LEVY_YEAR = 2025
ASSESS_RATIO = 0.1125
# (label, mills)
MILLS = [
    ("Lawton, inside city limits (Lawton schools)", 107.89),
    ("Lawton, outside city limits (Lawton schools)", 97.85),
    ("Lawton city, Cache schools", 116.43),
    ("Lawton city, Geronimo schools", 107.62),
    ("Lawton city, Bishop school", 110.37),
    ("Lawton city, Flower Mound school", 102.02),
    ("Cache", 106.39),
    ("Elgin", 101.17),
    ("Geronimo", 97.58),
    ("Fletcher", 79.03),
    ("Medicine Park, Lawton schools", 97.85),
    ("Medicine Park, Elgin schools", 101.17),
    ("Bishop, outside city limits", 100.33),
    ("Flower Mound, outside city limits", 91.98),
    ("Indiahoma", 82.72),
    ("Sterling", 81.21),
    ("Chattanooga", 93.41),
]

FOOT_TOOL = ("Every figure on this page is an estimate for planning. It is not a loan offer, a commitment to lend, a tax "
             "bill, or tax or legal advice. Rates, taxes, insurance, allowances and program rules are set by third "
             "parties and change. Your lender, the county assessor, and your finance office have the real numbers.")


def app_ld(name, url, desc):
    return {"@context": "https://schema.org", "@type": "WebApplication", "name": name, "url": url,
            "applicationCategory": "FinanceApplication", "operatingSystem": "Any (web browser)",
            "browserRequirements": "Requires JavaScript", "description": desc,
            "offers": {"@type": "Offer", "price": "0", "priceCurrency": "USD"},
            "provider": {"@id": SITE + "/#agent"}, "isAccessibleForFree": True}


def tool_page(path, key, nav, title, desc, h1, eyebrow, intro, tool_html, body_html, script, faqs=None, form=None,
              subject="Moving to Fort Sill", crumb=None, body_class="page-tool"):
    canon = SITE + "/" + path.strip("/") + ("/" if not path.endswith(".html") else "")
    canon = canon.replace(".html/", ".html")
    ld = [breadcrumb_ld([("Moving to Fort Sill", SITE + "/"), ("Tools", SITE + "/tools/"), (crumb or h1, canon)]),
          app_ld(h1, canon, desc)]
    if faqs:
        ld.append(faq_ld(faqs))
    main = body_html
    if form:
        main += '<section class="block">\n%s</section>\n' % form
    if faqs:
        main += faq_html(faqs)
    page = (head(title, desc, canon, ld)
            + header(nav, subject, body_class)
            + hero([("Moving to Fort Sill", "/"), ("Tools", "/tools/"), (crumb or h1, None)], eyebrow, h1, intro)
            + '\n<div class="toolwrap">\n' + tool_html + "</div>\n\n"
            + '<main class="tbody">\n' + main + "</main>\n"
            + toolchips(key)
            + footer(FOOT_TOOL, "Local figures current as of October 2026.", subject, scripts=("tools", "leadform"),
                     inline=script))
    rel = path.strip("/") + ("" if path.endswith(".html") else "/index.html")
    return rel, page, canon


def money(n):
    return "${:,}".format(int(round(n)))


# ============================================================================ property tax
def property_tax():
    price0 = int(MEDIAN)
    rows = ""
    for label, mills in MILLS:
        tax = price0 * ASSESS_RATIO * mills / 1000
        rows += ('      <tr data-mills="%s"><td>%s</td><td class="num">%s</td><td class="num" data-c="yr">%s</td>'
                 '<td class="num" data-c="mo">%s</td></tr>\n' % (mills, label, mills, money(tax), money(tax / 12)))
    opts = "".join('<option value="%s"%s>%s</option>' % (m, " selected" if i == 0 else "", l)
                   for i, (l, m) in enumerate(MILLS))
    t0 = price0 * ASSESS_RATIO * MILLS[0][1] / 1000
    tool = """<div class="tcalc">
  <div class="tin">
    <h2>The house</h2>
    <div class="flds">
      <div class="fld"><label for="price">Price or market value</label><input type="number" id="price" data-median value="{price}" min="10000" max="3000000" step="1000" inputmode="numeric"><span class="hint">A house you just bought is taxed on about what you paid.</span></div>
      <div class="fld"><label for="area">Where it is</label><select id="area">{opts}</select><span class="hint">The school district sets most of the rate. It follows the address.</span></div>
    </div>
    <p class="grp">Exemptions</p>
    <label class="chk"><input type="radio" name="ex" value="none" checked><span>None. Most active-duty buyers who keep another state as their legal residence.</span></label>
    <label class="chk"><input type="radio" name="ex" value="home"><span>Homestead exemption. Oklahoma residents who own and live in the house on January 1.</span></label>
    <label class="chk"><input type="radio" name="ex" value="home2"><span>Homestead plus the additional exemption, for households with gross income of $30,000 or less.</span></label>
    <label class="chk"><input type="radio" name="ex" value="dav"><span>100% permanent disabled veteran who is an Oklahoma resident. The whole homestead is exempt.</span></label>
  </div>
  <div class="tout" aria-live="polite">
    <span class="lab">Property tax each month</span>
    <div class="big" id="o-mo">{mo}</div>
    <div class="sub" id="o-sub">{yr} a year on a {pricefmt} house</div>
    <div class="kv">
      <div><span>Market value</span><b id="o-val">{pricefmt}</b></div>
      <div><span>Assessed at 11.25%</span><b id="o-assessed">{assessed}</b></div>
      <div><span>Exemption</span><b id="o-ex">$0</b></div>
      <div><span>Mill levy, {year}</span><b id="o-mills">{mills}</b></div>
      <div class="tot"><span>Tax for the year</span><b id="o-yr">{yr}</b></div>
      <div><span>As a share of value</span><b id="o-eff">{eff}%</b></div>
    </div>
    <div class="acts"><button type="button" class="tbtn" id="btn-print">Print</button><a class="tbtn" href="/payment-toolkit.html">See the whole payment</a></div>
  </div>
</div>
""".format(price=price0, opts=opts, mo=money(t0 / 12), yr=money(t0), pricefmt=money(price0),
           assessed=money(price0 * ASSESS_RATIO), mills=MILLS[0][1], year=LEVY_YEAR,
           eff="%.2f" % (t0 / price0 * 100))
    body = """<section class="block">
  <h2>The same house in every district</h2>
  <div class="tscroll">
  <table id="cmp">
    <caption>{year} levies from the Comanche County Assessor. Tax shown is for the price and exemption you entered.</caption>
    <thead><tr><th>Area</th><th class="num">Mills</th><th class="num">Per year</th><th class="num">Per month</th></tr></thead>
    <tbody>
{rows}    </tbody>
  </table>
  </div>
  <p class="tnote">New levies come out each fall. The assessor's office, 580-355-1052, has the final word on value and exemptions. The treasurer, 580-355-5763, sends the bill.</p>
</section>
<section class="block">
  <h2>How the bill is figured</h2>
  <p>The county taxes 11.25% of what the house is worth. That is the assessed value. Exemptions come off the assessed value, and what is left is multiplied by the mill levy for the area. A mill is $1 of tax per $1,000 of assessed value.</p>
  <p><strong>Do not budget off the seller's tax bill.</strong> Oklahoma caps how fast a home's taxable value rises while the same person owns it. When the house sells, the cap comes off and the county can value it at about what you paid. Your first full bill can come in higher than the one the seller was paying. Ask your lender to set the escrow from the purchase price.</p>
  <p>Exemptions go by who owns and lives in the house on January 1, so the year you buy can be billed differently from the years after. The assessor's office will tell you what applies to you.</p>
  <p>The other calculators on this site use 1.11% of value, the median across all Lawton homes. This page uses the actual levy for the area you pick, which runs closer to 1.2% for a house you just bought inside Lawton.</p>
</section>
""".format(year=LEVY_YEAR, rows=rows)
    script = """(function(){
  var L = window.LBT, RATIO = __RATIO__;
  function ex(){ var r = document.querySelector('input[name="ex"]:checked'); return r ? r.value : "none"; }
  function tax(price, mills, e){
    if (e === "dav") return 0;
    var assessed = price * RATIO - (e === "home" ? 1000 : e === "home2" ? 2000 : 0);
    return Math.max(assessed, 0) * mills / 1000;
  }
  function run(){
    var price = L.val("price", __PRICE__, 0, 5000000), mills = parseFloat(L.$("area").value), e = ex();
    var t = tax(price, mills, e);
    L.setText("o-mo", L.usd(t / 12));
    L.setText("o-sub", L.usd(t) + " a year on a " + L.usd(price) + " house");
    L.setText("o-val", L.usd(price));
    L.setText("o-assessed", L.usd(price * RATIO));
    L.setText("o-ex", e === "dav" ? "Fully exempt" : e === "home" ? "$1,000 off assessed" : e === "home2" ? "$2,000 off assessed" : "$0");
    L.setText("o-mills", mills.toFixed(2));
    L.setText("o-yr", L.usd(t));
    L.setText("o-eff", (price > 0 ? (t / price * 100).toFixed(2) : "0.00") + "%");
    var rows = document.querySelectorAll("#cmp tbody tr");
    for (var k = 0; k < rows.length; k++){
      var m = parseFloat(rows[k].getAttribute("data-mills")), v = tax(price, m, e);
      rows[k].querySelector('[data-c="yr"]').textContent = L.usd(v);
      rows[k].querySelector('[data-c="mo"]').textContent = L.usd(v / 12);
    }
    window.LEAD_SUMMARY = function(){ return "Property tax estimate: " + L.usd(t) + " a year on " + L.usd(price) + ", " + L.$("area").options[L.$("area").selectedIndex].text; };
  }
  L.watch(document, run);
  L.market(run);
  run();
})();""".replace("__RATIO__", str(ASSESS_RATIO)).replace("__PRICE__", str(price0))
    faqs = [
        ("What is the property tax rate in Lawton, Oklahoma?",
         "Inside Lawton city limits in the Lawton school district, the %d levy was 107.89 mills. On a house taxed at "
         "what it is worth, that works out to about 1.21%% of value a year before exemptions." % LEVY_YEAR),
        ("How is property tax calculated in Comanche County?",
         "Market value times 11.25% gives the assessed value. Exemptions come off that. The rest is multiplied by the "
         "mill levy for the school district and city the house is in."),
        ("Do disabled veterans pay property tax in Oklahoma?",
         "A veteran with a 100% permanent service-connected disability who is an Oklahoma resident pays no property tax "
         "on their homestead. You file Form 998 with the county assessor."),
    ]
    form = listform("t-property-tax", "Want the tax figured on a specific house?",
                    "Send me an address or a price range. I will send what is listed and what the tax should run on "
                    "each one after you buy it.", "Send it to me",
                    notes_hint="An address, a part of town, when you need to move")
    return tool_page(
        "property-tax-calculator", "tax", "tax",
        "Lawton Property Tax Calculator | Comanche County, OK",
        "Figure the property tax on any home price in Lawton, Elgin, Cache, Geronimo, Fletcher or Medicine Park, "
        "using the county's real mill levies and exemptions.",
        "Lawton property tax calculator", "Comanche County, Oklahoma",
        "Put in a price and pick the area. This uses the county's actual levy for each school district, so you see "
        "the bill a new owner would get.",
        tool, body, script, faqs, form, crumb="Property tax calculator")


# ============================================================================ VA residual income
def residual():
    def chart(tier, add):
        t = {"hi": {"Northeast": [450, 755, 909, 1025, 1062], "Midwest": [441, 738, 889, 1003, 1039],
                    "South (Oklahoma)": [441, 738, 889, 1003, 1039], "West": [491, 823, 990, 1117, 1158]},
             "lo": {"Northeast": [390, 654, 788, 888, 921], "Midwest": [382, 641, 772, 868, 902],
                    "South (Oklahoma)": [382, 641, 772, 868, 902], "West": [425, 713, 859, 967, 1004]}}[tier]
        rows = ""
        for i in range(5):
            rows += "      <tr><td>%d</td>%s</tr>\n" % (i + 1, "".join('<td class="num">%s</td>' % money(t[r][i]) for r in t))
        rows += '      <tr><td>Over 5</td><td colspan="4">Add $%d for each additional person, up to a family of seven</td></tr>\n' % add
        return ('<div class="tscroll">\n  <table>\n    <caption>%s</caption>\n    <thead><tr><th>Family size</th>%s</tr></thead>\n'
                '    <tbody>\n%s    </tbody>\n  </table>\n  </div>\n' % (
                    "Loan amounts of $80,000 and above" if tier == "hi" else "Loan amounts of $79,999 and below",
                    "".join('<th class="num">%s</th>' % r for r in t), rows))
    tool = """<div class="tcalc">
  <div class="tin">
    <h2>Your household</h2>
    <div class="flds">
      <div class="fld"><label for="fam">Family size</label><select id="fam"><option>1</option><option>2</option><option>3</option><option selected>4</option><option>5</option><option>6</option><option>7</option></select><span class="hint">Everyone in the house, borrowers included.</span></div>
      <div class="fld"><label for="region">Region</label><select id="region"><option value="south" selected>South (Oklahoma)</option><option value="mw">Midwest</option><option value="ne">Northeast</option><option value="west">West</option></select></div>
    </div>
    <p class="grp">Money in, each month</p>
    <div class="flds">
      <div class="fld"><label for="taxable">Taxable pay</label><input type="number" id="taxable" value="4300" min="0" step="50" inputmode="numeric"><span class="hint">Base pay, wages, retirement. Before taxes.</span></div>
      <div class="fld"><label for="taxfree">Tax-free income</label><input type="number" id="taxfree" value="1971" min="0" step="10" inputmode="numeric"><span class="hint">BAH, BAS, VA disability.</span></div>
      <div class="fld"><label for="taxes">Taxes taken out</label><input type="number" id="taxes" value="860" min="0" step="10" inputmode="numeric"><span class="hint" id="taxhint">Estimated at 20% of taxable pay. Use your LES.</span></div>
    </div>
    <p class="grp">The house</p>
    <div class="flds">
      <div class="fld"><label for="price">Purchase price</label><input type="number" id="price" data-median value="{price}" min="20000" step="1000" inputmode="numeric"></div>
      <div class="fld"><label for="rate">Interest rate %</label><input type="number" id="rate" value="{rate}" min="1" max="15" step="0.125" inputmode="decimal"><span class="hint" data-rate-note>Freddie Mac average</span></div>
      <div class="fld"><label for="fee">VA funding fee</label><select id="fee"><option value="first">First use (2.15%)</option><option value="again">Used before (3.3%)</option><option value="exempt">Exempt</option></select></div>
      <div class="fld"><label for="sqft">Square feet</label><input type="number" id="sqft" value="1600" min="400" max="8000" step="50" inputmode="numeric"><span class="hint">The VA counts 14 cents a foot for upkeep and utilities.</span></div>
    </div>
    <p class="grp">Money out, each month</p>
    <div class="flds">
      <div class="fld"><label for="debts">Other debts</label><input type="number" id="debts" value="450" min="0" step="10" inputmode="numeric"><span class="hint">Car, cards, student loans, child support.</span></div>
      <div class="fld"><label for="care">Child care</label><input type="number" id="care" value="0" min="0" step="10" inputmode="numeric"></div>
    </div>
  </div>
  <div class="tout" aria-live="polite">
    <span class="lab">Residual income <span class="tpill ok" id="o-pill">Clears</span></span>
    <div class="big" id="o-res">$0</div>
    <div class="sub" id="o-sub"></div>
    <div class="kv">
      <div><span>Income after taxes</span><b id="o-net">$0</b></div>
      <div><span>House payment</span><b id="o-pay">$0</b></div>
      <div><span>Upkeep and utilities</span><b id="o-mu">$0</b></div>
      <div><span>Debts and child care</span><b id="o-debt">$0</b></div>
      <div class="tot"><span>Left over</span><b id="o-res2">$0</b></div>
      <div><span>VA minimum for your family</span><b id="o-req">$0</b></div>
      <div><span>Debt-to-income ratio</span><b id="o-dti">0%</b></div>
    </div>
    <div class="verdict" id="o-verdict"></div>
    <div class="acts"><button type="button" class="tbtn" id="btn-print">Print</button><a class="tbtn" href="/va-loan-calculator.html">Full VA loan calculator</a></div>
  </div>
</div>
""".format(price=int(MEDIAN), rate=RATE)
    body = """<section class="block">
  <h2>What residual income is</h2>
  <p>It is what your household has left each month after taxes, the house payment, upkeep and utilities, and your other debts. The VA sets a minimum by family size and region. Clear it and you are past the harder of the two tests. Miss it and a lender needs strong reasons to approve the loan, even when the debt-to-income ratio looks fine.</p>
  <p>Two things work in your favor. Lenders can take 5% off the minimum for active-duty and retired military who use the post's facilities. And if you clear the minimum by 20% or more, a lender can approve a debt-to-income ratio above the usual 41% without extra justification.</p>
</section>
<section class="block">
  <h2>The VA residual income chart</h2>
  {hi}
  {lo}
  <p class="tnote">From the VA's underwriting standards, 38 CFR 36.4340. Oklahoma is in the South region. The debt-to-income figure above counts tax-free income at 125%, the most a lender can use.</p>
</section>
""".format(hi=chart("hi", 80), lo=chart("lo", 75))
    script = """(function(){
  var L = window.LBT, taxesTouched = false;
  L.$("taxes").addEventListener("input", function(){ taxesTouched = true; });
  function run(){
    var taxable = L.val("taxable", 0, 0), taxfree = L.val("taxfree", 0, 0);
    if (!taxesTouched) L.$("taxes").value = Math.round(taxable * 0.20);
    L.setText("taxhint", taxesTouched ? "Federal, state, Social Security, Medicare." : "Estimated at 20% of taxable pay. Use your LES.");
    var taxes = L.val("taxes", 0, 0);
    var p = L.payment(L.val("price", __PRICE__, 0), L.val("rate", __RATE__, 0.1, 25), { fee: L.$("fee").value });
    var mu = L.val("sqft", 1600, 0) * 0.14;
    var debts = L.val("debts", 0, 0) + L.val("care", 0, 0);
    var net = taxable + taxfree - taxes;
    var res = net - p.total - mu - debts;
    var fam = parseInt(L.$("fam").value, 10), region = L.$("region").value;
    var req = L.residualRequired(region, fam, p.loan);
    var gross = taxable + taxfree * 1.25;     // tax-free income grossed up 25%, same as the VA loan calculator
    var dti = gross > 0 ? (p.total + debts) / gross * 100 : 0;
    var ok = res >= req, cushion = res >= req * 1.2;
    L.setText("o-res", L.usd(res)); L.setText("o-res2", L.usd(res));
    L.setText("o-net", L.usd(net)); L.setText("o-pay", L.usd(p.total)); L.setText("o-mu", L.usd(mu));
    L.setText("o-debt", L.usd(debts)); L.setText("o-req", L.usd(req)); L.setText("o-dti", dti.toFixed(1) + "%");
    L.setText("o-sub", "Family of " + fam + (fam >= 7 ? " or more" : "") + ". The VA minimum is " + L.usd(req) + " a month.");
    var pill = L.$("o-pill"); pill.textContent = ok ? "Clears" : "Short"; pill.className = "tpill " + (ok ? "ok" : "no");
    var v = L.$("o-verdict"); v.className = "verdict " + (ok ? "ok" : "no");
    v.textContent = cushion ? "You clear the minimum by " + L.usd(res - req) + ", which is more than 20% over. That cushion can carry a debt-to-income ratio above 41%."
      : ok ? "You clear the minimum by " + L.usd(res - req) + " a month. Getting to " + L.usd(req * 1.2) + " would give you the 20% cushion lenders like to see."
      : "You are " + L.usd(req - res) + " a month short. If your lender applies the 5% military reduction, the minimum drops to " + L.usd(req * 0.95) + ". A lower price or paying off a debt moves this the fastest.";
    window.LEAD_SUMMARY = function(){ return "Residual income: " + L.usd(res) + " (VA minimum " + L.usd(req) + ", family of " + fam + ")\\nPrice: " + L.usd(p.price) + ", payment " + L.usd(p.total) + "\\nDTI: " + dti.toFixed(1) + "%"; };
  }
  L.watch(document, run);
  L.market(run);
  run();
})();""".replace("__PRICE__", str(int(MEDIAN))).replace("__RATE__", str(RATE))
    faqs = [
        ("What is the VA residual income requirement in Oklahoma?",
         "Oklahoma is in the VA's South region. On loans of $80,000 and up the monthly minimum is $441 for one person, "
         "$738 for two, $889 for three, $1,003 for a family of four and $1,039 for five, plus $80 for each additional "
         "person up to seven."),
        ("How do you calculate VA residual income?",
         "Start with gross monthly income. Subtract taxes, the full house payment, an allowance for upkeep and "
         "utilities at 14 cents per square foot, child care, and your other monthly debts. What is left is residual "
         "income."),
        ("Does BAH count toward VA residual income?",
         "Yes. BAH, BAS and VA disability compensation all count as income, and because they are not taxed, every "
         "dollar of them goes straight into the calculation."),
    ]
    form = listform("t-residual", "Want to see houses that fit this number?",
                    "Tell me your range and I will send what is listed. I leave off the ones that likely will not get "
                    "through a VA appraisal and send you the rest myself.", "Send me the list")
    return tool_page(
        "va-residual-income-calculator", "residual", "va",
        "VA Residual Income Calculator and 2026 Chart",
        "Figure your VA residual income and see whether it clears the minimum for your family size and region. "
        "Includes the full VA residual income chart.",
        "VA residual income calculator", "The test that decides close VA files",
        "Put in your income, the house, and your debts. You get what is left over each month and the VA minimum it "
        "has to clear.",
        tool, body, script, faqs, form, subject="VA loan question", crumb="VA residual income")


# ============================================================================ rent vs buy
def rent_vs_buy():
    tool = """<div class="tcalc">
  <div class="tin">
    <h2>Renting</h2>
    <div class="flds">
      <div class="fld"><label for="rent">Monthly rent</label><input type="number" id="rent" value="1250" min="300" max="6000" step="25" inputmode="numeric"><span class="hint">A single-family house here runs $1,200 to $1,300.</span></div>
      <div class="fld"><label for="years">Years you will be here</label><select id="years"><option>1</option><option>2</option><option selected>3</option><option>4</option><option>5</option><option>6</option><option>7</option><option>8</option><option>9</option><option>10</option></select></div>
    </div>
    <p class="grp">Buying</p>
    <div class="flds">
      <div class="fld"><label for="price">Purchase price</label><input type="number" id="price" value="175000" min="40000" max="2000000" step="1000" inputmode="numeric"></div>
      <div class="fld"><label for="rate">Interest rate %</label><input type="number" id="rate" value="{rate}" min="1" max="15" step="0.125" inputmode="decimal"><span class="hint" data-rate-note>Freddie Mac average</span></div>
      <div class="fld"><label for="fee">VA funding fee</label><select id="fee"><option value="first">First use (2.15%)</option><option value="again">Used before (3.3%)</option><option value="exempt">Exempt</option></select></div>
      <div class="fld"><label for="closing">Closing costs you pay</label><input type="number" id="closing" value="0" min="0" step="100" inputmode="numeric"><span class="hint">Zero if the seller covers them, which is common here.</span></div>
    </div>
    <details class="more"><summary>Assumptions you can change</summary><div>
      <div class="flds">
        <div class="fld"><label for="apprec">Home value growth % a year</label><input type="number" id="apprec" value="3" min="-5" max="15" step="0.5" inputmode="decimal"></div>
        <div class="fld"><label for="rentup">Rent growth % a year</label><input type="number" id="rentup" value="3" min="0" max="15" step="0.5" inputmode="decimal"></div>
        <div class="fld"><label for="sell">Cost to sell %</label><input type="number" id="sell" value="6" min="0" max="12" step="0.5" inputmode="decimal"><span class="hint">Of the sale price.</span></div>
        <div class="fld"><label for="maint">Upkeep % of price a year</label><input type="number" id="maint" value="1" min="0" max="5" step="0.25" inputmode="decimal"></div>
      </div>
    </div></details>
  </div>
  <div class="tout" aria-live="polite">
    <span class="lab">Over your <span id="o-yrs">3</span> years here</span>
    <div class="big" id="o-head">$0</div>
    <div class="sub" id="o-sub"></div>
    <div class="kv">
      <div><span>Full house payment</span><b id="o-pay">$0</b></div>
      <div><span>Rent paid over the stay</span><b id="o-rent">$0</b></div>
      <div><span>Cost of owning, after you sell</span><b id="o-own">$0</b></div>
      <div class="tot"><span>Buying comes out ahead</span><b id="o-be">never</b></div>
    </div>
    <div class="verdict" id="o-keep"></div>
    <div class="acts"><button type="button" class="tbtn" id="btn-print">Print</button><a class="tbtn" href="/bah/">What your BAH buys</a></div>
  </div>
</div>
""".format(rate=RATE)
    body = """<section class="block">
  <h2>Year by year</h2>
  <div class="tscroll">
  <table id="yt">
    <caption>What each choice has cost you by the end of each year. Owning assumes you sell that year.</caption>
    <thead><tr><th>Year</th><th class="num">Renting</th><th class="num">Buying, then selling</th><th class="num">Buying is ahead by</th></tr></thead>
    <tbody></tbody>
  </table>
  </div>
</section>
<section class="block">
  <h2>How to read it</h2>
  <p>Renting costs you the rent. Owning costs you the payments, upkeep, and what it takes to sell, and gives you back whatever equity you walk away with. Early on, selling costs eat the equity, so renting wins. The longer you stay, the more the loan pays down and the further buying pulls ahead.</p>
  <p>Selling is not the only exit. A lot of Fort Sill families keep the house and rent it out when they PCS. The line under the numbers shows what that would look like the month you leave. The page on <a href="/fort-sill/rent-it-out-when-you-pcs/">keeping the house when you PCS</a> covers the rest.</p>
  <p class="tnote">The payment includes Lawton property tax and insurance and stays flat. Tax benefits are left out. This is a planning tool. It cannot tell you what a house will be worth.</p>
</section>
"""
    script = """(function(){
  var L = window.LBT;
  function run(){
    var rent = L.val("rent", 1250, 0), years = parseInt(L.$("years").value, 10), price = L.val("price", 175000, 0);
    var rate = L.val("rate", __RATE__, 0.1, 25), closing = L.val("closing", 0, 0);
    var g = L.val("apprec", 3, -20, 30) / 100, rg = L.val("rentup", 3, 0, 30) / 100;
    var sell = L.val("sell", 6, 0, 20) / 100, maint = L.val("maint", 1, 0, 10) / 100;
    var p = L.payment(price, rate, { fee: L.$("fee").value });
    var rows = "", be = null, rentTot = 0, own = 0, stay = {};
    for (var y = 1; y <= 10; y++){
      rentTot += rent * Math.pow(1 + rg, y - 1) * 12;
      var paid = closing + p.total * 12 * y + price * maint * y;
      var equity = price * Math.pow(1 + g, y) * (1 - sell) - L.balance(p.loan, rate, 30, y * 12);
      own = paid - equity;
      var diff = rentTot - own;
      if (be === null && diff >= 0) be = y;
      if (y === years) stay = { rent: rentTot, own: own, diff: diff };
      rows += "<tr" + (y === years ? ' class="tot"' : "") + "><td>" + y + '</td><td class="num">' + L.usd(rentTot) + '</td><td class="num">' + L.usd(own) + '</td><td class="num">' + L.usd(diff) + "</td></tr>";
    }
    document.querySelector("#yt tbody").innerHTML = rows;
    L.setText("o-yrs", years);
    L.setText("o-head", L.usd(Math.abs(stay.diff)));
    L.setText("o-sub", stay.diff >= 0 ? "is what buying saves you over renting, if you sell when you leave." : "is what renting saves you over buying, if you sell when you leave.");
    L.setText("o-pay", L.usd(p.total) + " a month");
    L.setText("o-rent", L.usd(stay.rent));
    L.setText("o-own", L.usd(stay.own));
    L.setText("o-be", be === null ? "not within 10 years" : be === 1 ? "from the first year" : "from year " + be + " on");
    var rentThen = rent * Math.pow(1 + rg, years), flow = rentThen * 0.9 - p.total - price * maint / 12;
    var k = L.$("o-keep"); k.className = "verdict " + (flow >= 0 ? "ok" : "no");
    k.textContent = "Keep it as a rental instead: at about " + L.usd(rentThen) + " in rent, after a 10% manager and upkeep, it " +
      (flow >= 0 ? "puts about " + L.usd(flow) + " a month in your pocket." : "costs you about " + L.usd(-flow) + " a month to hold.");
    window.LEAD_SUMMARY = function(){ return "Rent vs buy: " + years + " years, rent " + L.usd(rent) + ", price " + L.usd(price) + ", payment " + L.usd(p.total) + "\\nBuying ahead: " + L.$("o-be").textContent; };
  }
  L.watch(document, run);
  L.market(run);
  run();
})();""".replace("__RATE__", str(RATE))
    faqs = [
        ("Should I buy or rent at Fort Sill?",
         "It depends on how long you will be here and what you do with the house when you leave. Buying and then "
         "selling inside two or three years is tight, because selling costs eat the equity. Staying longer, or keeping "
         "the house as a rental, changes the math."),
        ("How much is rent near Fort Sill?",
         "A single-family house in Lawton rents for somewhere around $1,200 to $1,300 a month. Citywide averages run "
         "lower because they count apartments, and most military families here rent houses."),
        ("How long do you need to stay for buying to make sense?",
         "Put your numbers in above. The break-even year moves with the rent, the price, the rate, and how fast "
         "values rise. At today's rates it often takes several years if you sell, which is why what you do with the "
         "house when you leave matters as much as the price."),
    ]
    form = listform("t-rent-vs-buy", "Want to see it with real houses?",
                    "Tell me your range. I will send what is for sale, and what similar houses are renting for, so "
                    "you can compare the two with real numbers.", "Send it to me")
    return tool_page(
        "rent-vs-buy", "rentbuy", "rentbuy",
        "Rent vs Buy at Fort Sill Calculator | Lawton, OK",
        "Rent or buy at Fort Sill? Put in your rent, a price, and how long you will be here. See the year buying comes "
        "out ahead, with real Lawton tax and insurance.",
        "Rent or buy at Fort Sill", "Rent vs buy calculator",
        "Put in the rent, a price, and how long you will be here. You get the year buying pulls ahead, and what the "
        "house does as a rental after you PCS.",
        tool, body, script, faqs, form, crumb="Rent vs buy")


# ============================================================================ PCS timeline
PCS_STEPS = [
    # (days before report date, tags, title, text)   tags: all | buy | rent | post | kids | pets | ppm
    (120, "all", "Go to the transportation office",
     "As soon as you have orders. The Army hires the movers, and scheduling is first come, first served. You set the shipment up in DPS through Military OneSource."),
    (120, "all", "Ask for a sponsor",
     "Your gaining unit assigns one. A good sponsor will tell you which gate your unit uses and what the drive is like."),
    (100, "buy", "Talk to a lender and get pre-approved",
     "With orders in hand a lender can use your Fort Sill BAH. Ask them to run your residual income, and ask about REI Home100 and OHFA."),
    (100, "post", "Call Corvias about on-post housing",
     "Corvias runs family housing on post. Ask what is open for your rank and family size and whether there is a wait."),
    (90, "buy", "Send me your price range",
     "I start sending what is listed and walk the good ones on video. Settle the gate you will use and the school district first."),
    (90, "ppm", "Get your do-it-yourself move approved",
     "The transportation office has to counsel and approve a PPM before you move anything. No approval, no reimbursement."),
    (75, "rent", "Start watching rentals",
     "A single-family house here rents for around $1,200 to $1,300. Stop at the Housing Services Office before you sign a lease."),
    (60, "buy", "Be under contract",
     "Most loans take 30 to 45 days from contract to closing, so this leaves you some room. Earnest money is due within three days of signing."),
    (55, "buy", "Inspections and your insurance quote",
     "The standard Oklahoma contract gives you ten days unless a different number is written in. Get the insurance quote inside that window, while it can still change your mind."),
    (45, "kids", "Start school enrollment",
     "Request records from the old school now. The district follows the address, so you can enroll as soon as you have one."),
    (45, "pets", "Get vet records together",
     "Oklahoma has no quarantine. Lawton requires pets to be registered, and the on-post hotel has a limited number of pet rooms."),
    (30, "all", "Confirm pack and pickup dates with the movers",
     "Set aside professional gear so it is weighed separately. Up to 2,000 pounds of it does not count against your weight allowance."),
    (30, "buy", "Appraisal, underwriting, and how you will sign",
     "If you will not be in town for closing, ask the lender and title company now about signing by mail or a power of attorney."),
    (21, "all", "Book lodging for the gap",
     "You have up to 21 days of temporary lodging expense. On-post lodging is IHG Army Hotels. Check-in is at 5676 Fergusson Road."),
    (14, "all", "Line up utilities and passes",
     "In Lawton, water, sewer and trash go through the city. The other towns have their own setups. Family without a military ID needs a visitor pass. With a REAL ID they can request one online ahead of time."),
    (14, "ppm", "Plan your weight tickets",
     "You need certified empty and full weight tickets for every vehicle and every trip. Find the scales on your route now."),
    (7, "buy", "Final walk-through and closing",
     "We walk the house one more time before you sign. Bring your ID. The first year of insurance is paid at closing."),
    (0, "all", "Report to the Welcome Center",
     "Building 4700 on Mow-Way Road, staffed around the clock except Thanksgiving and Christmas. Bring orders and your leave form. In-processing takes three to five duty days. Students and trainees report where their orders say."),
    (-3, "all", "Stop by ACS and the Housing Services Office",
     "Both are in Building 4700. The ACS loan closet lends kitchen basics and sleeping mats, free, while you wait on your shipment."),
    (-10, "all", "Tags, pets, and schools",
     "The military vehicle tag is about $26 a year with Form 779. Register pets with the city. Finish school enrollment."),
    (-21, "all", "Your lodging days run out",
     "Temporary lodging expense covers up to 21 days. Be in your house, your rental, or on-post quarters by now."),
]


def pcs_timeline():
    steps = json.dumps([{"d": d, "t": t, "h": h, "x": x} for d, t, h, x in PCS_STEPS])
    static = "".join('    <li><div class="when">%s</div><div class="what"><b>%s</b><span>%s</span></div></li>\n' % (
        ("%d days before" % d) if d > 0 else ("Report date" if d == 0 else "%d days after" % -d), h, x)
        for d, t, h, x in PCS_STEPS if t in ("all", "buy"))
    tool = """<div class="tcalc">
  <div class="tin">
    <h2>Your move</h2>
    <div class="flds">
      <div class="fld"><label for="report">Report date</label><input type="date" id="report"><span class="hint">The date on your orders.</span></div>
      <div class="fld" style="min-width:230px"><span class="l">Where you plan to live</span>
        <div class="seg" role="radiogroup" aria-label="Where you plan to live">
          <label><input type="radio" name="live" value="buy" checked><span>Buy</span></label>
          <label><input type="radio" name="live" value="rent"><span>Rent</span></label>
          <label><input type="radio" name="live" value="post"><span>On post</span></label>
        </div>
      </div>
    </div>
    <label class="chk"><input type="checkbox" id="kids"><span>Kids in school</span></label>
    <label class="chk"><input type="checkbox" id="pets"><span>Pets</span></label>
    <label class="chk"><input type="checkbox" id="ppm"><span>Moving some or all of it myself (PPM)</span></label>
  </div>
  <div class="tout" aria-live="polite">
    <span class="lab">Days until you report</span>
    <div class="big" id="o-days">120</div>
    <div class="sub" id="o-sub"></div>
    <div class="verdict" id="o-next"></div>
    <div class="acts"><button type="button" class="tbtn" id="btn-print">Print the list</button><button type="button" class="tbtn" id="btn-ics">Add to my calendar</button></div>
  </div>
</div>
"""
    body = """<section class="block">
  <h2>Your list, with dates</h2>
  <ol class="tl" id="tl">
%s  </ol>
  <p class="tnote">Dates are targets, not deadlines set by the Army. Your transportation counselor, your unit, and finance have the final word on anything official. The <a href="/fort-sill/pcs-checklist/">Fort Sill PCS checklist</a> explains each step.</p>
</section>
""" % static
    script = """(function(){
  var L = window.LBT, STEPS = __STEPS__;
  var MON = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"], DOW = ["Sun","Mon","Tue","Wed","Thu","Fri","Sat"];
  function iso(d){ return d.getFullYear() + "-" + ("0" + (d.getMonth() + 1)).slice(-2) + "-" + ("0" + d.getDate()).slice(-2); }
  function today(){ var d = new Date(); return new Date(d.getFullYear(), d.getMonth(), d.getDate()); }
  var rep = L.$("report"), d0 = today(); d0.setDate(d0.getDate() + 120); rep.value = iso(d0);
  function picked(){
    var live = document.querySelector('input[name="live"]:checked').value;
    var on = { all: 1 }; on[live] = 1;
    if (L.$("kids").checked) on.kids = 1;
    if (L.$("pets").checked) on.pets = 1;
    if (L.$("ppm").checked) on.ppm = 1;
    var p = String(rep.value).split("-"), r = p.length === 3 ? new Date(+p[0], +p[1] - 1, +p[2]) : d0;
    var out = [];
    for (var k = 0; k < STEPS.length; k++){
      var s = STEPS[k]; if (!on[s.t]) continue;
      var d = new Date(r.getFullYear(), r.getMonth(), r.getDate() - s.d);
      out.push({ date: d, s: s });
    }
    return { report: r, items: out };
  }
  function run(){
    var P = picked(), now = today(), html = "", next = null;
    for (var k = 0; k < P.items.length; k++){
      var it = P.items[k], past = it.date < now;
      if (!past && !next) next = it;
      html += '<li' + (past ? ' class="past"' : "") + '><div class="when">' + DOW[it.date.getDay()] + ", " + MON[it.date.getMonth()] + " " + it.date.getDate() +
        "<small>" + (past ? "Do this now" : it.s.d > 0 ? it.s.d + " days before" : it.s.d === 0 ? "Report date" : (-it.s.d) + " days after") + "</small></div>" +
        '<div class="what"><b>' + it.s.h + "</b><span>" + it.s.x + "</span></div></li>";
    }
    L.$("tl").innerHTML = html;
    var days = Math.round((P.report - now) / 86400000);
    L.setText("o-days", days >= 0 ? days : 0);
    var behind = P.items.filter(function(i){ return i.date < now && i.s.d > 0; }).length;
    L.setText("o-sub", days < 0 ? "Your report date has passed. The list below still holds." : behind ? behind + (behind === 1 ? " step is" : " steps are") + " already due. Start with those." : "You are ahead of every step on the list.");
    var v = L.$("o-next"); v.className = "verdict " + (behind ? "no" : "ok");
    v.textContent = next ? "Next up, " + MON[next.date.getMonth()] + " " + next.date.getDate() + ": " + next.s.h + "." : "Everything on the list is behind you.";
  }
  function ics(){
    var P = picked(), out = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//movingtoftsill.com//PCS timeline//EN"];
    function ymd(d){ return iso(d).replace(/-/g, ""); }
    for (var k = 0; k < P.items.length; k++){
      var it = P.items[k], on = it.date < today() ? today() : it.date;      // anything already due goes on today
      var end = new Date(on.getFullYear(), on.getMonth(), on.getDate() + 1);
      out.push("BEGIN:VEVENT", "UID:pcs-" + k + "-" + ymd(on) + "@movingtoftsill.com", "DTSTAMP:" + ymd(today()) + "T000000Z",
        "DTSTART;VALUE=DATE:" + ymd(on), "DTEND;VALUE=DATE:" + ymd(end), "SUMMARY:PCS: " + it.s.h.replace(/,/g, "\\\\,"),
        "DESCRIPTION:" + it.s.x.replace(/,/g, "\\\\,") + " movingtoftsill.com/pcs-timeline/", "END:VEVENT");
    }
    out.push("END:VCALENDAR");
    var a = document.createElement("a");
    a.href = URL.createObjectURL(new Blob([out.join("\\r\\n")], { type: "text/calendar" }));
    a.download = "fort-sill-pcs-timeline.ics";
    document.body.appendChild(a); a.click(); document.body.removeChild(a);
  }
  L.watch(document, run);
  L.$("btn-ics").addEventListener("click", ics);
  run();
})();""".replace("__STEPS__", steps)
    faqs = [
        ("How far ahead should I start planning a PCS to Fort Sill?",
         "Start the day you get orders. The transportation office schedules movers first come, first served, and if "
         "you plan to buy, a lender can pre-approve you on your Fort Sill BAH as soon as you have orders in hand."),
        ("When should I start looking for a house before a PCS?",
         "About three months out. Most loans take 30 to 45 days from contract to closing, so being under contract two "
         "months before your report date lets you close around the time you arrive."),
        ("How many days of temporary lodging do I get on a PCS?",
         "Up to 21 days of temporary lodging expense on a move within the continental United States."),
    ]
    form = leadform("t-pcs-timeline", "Buying when you get here?",
                    "Tell me when you report and what you want to spend. I will send what is for sale in your range "
                    "and walk the good ones on video until you get to town.", "Send me the list",
                    checked=("listings",))
    return tool_page(
        "pcs-timeline", "pcs", "guide",
        "Fort Sill PCS Timeline: A Dated Checklist From Your Report Date",
        "Put in your Fort Sill report date and get a dated PCS checklist: movers, pre-approval, house hunting, schools "
        "and lodging. Print it or add it to your calendar.",
        "Fort Sill PCS timeline", "PCS planner",
        "Put in your report date. You get a dated list of what to do and when, and you can print it or drop it in "
        "your calendar.",
        tool, body, script, faqs, form, crumb="PCS timeline")


def build():
    return [property_tax(), residual(), rent_vs_buy(), pcs_timeline()]
