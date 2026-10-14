"""The VA loan calculator at /va-loan-calculator.html. One flow, no tabs: who is
on the loan, the household, the house, and the answer beside it the whole time.
The math is in assets/tools.js. Pay grades and BAS come from bah.py, so the
January BAH update carries over to the quick-fill here."""
import json

import bah
from common import MEDIAN, RATE, listform
from tools import mark, tool_page


def build():
    # option values double as the link format: ?grade=E-6
    grades = json.dumps({label.replace(" ", ""): [label, w, wo, round(bah.BAS[k])] for label, w, wo, k in bah.BAH})
    gopts = '<option value="none">Not on active duty</option>' + "".join(
        '<option value="%s"%s>%s</option>' % (label.replace(" ", ""), " selected" if label == "E-6" else "", label)
        for label, _w, _wo, _k in bah.BAH)
    tool = """<div class="tcalc">
  <div class="tin">
    <h2>Who is on the loan</h2>
    <div class="flds">
      <div class="fld"><label for="grade">Pay grade</label><select id="grade">{gopts}</select><span class="hint">Fills in {year} Fort Sill BAH and BAS.</span></div>
      <div class="fld"><label for="deps">Dependents</label><select id="deps"><option value="w" selected>With dependents</option><option value="wo">Without</option></select></div>
    </div>
    <div class="flds">
      <div class="fld"><label for="a-base">Taxable pay</label><input type="number" id="a-base" value="4300" min="0" max="40000" step="50" inputmode="numeric"><span class="hint">Base pay, wages or retirement. Monthly, before taxes.</span></div>
      <div class="fld"><label for="a-bah">BAH</label><input type="number" id="a-bah" value="1494" min="0" max="8000" step="1" inputmode="numeric"><span class="hint">Tax-free.</span></div>
      <div class="fld"><label for="a-bas">BAS</label><input type="number" id="a-bas" value="477" min="0" max="1000" step="1" inputmode="numeric"><span class="hint">Tax-free.</span></div>
      <div class="fld"><label for="a-dis">VA disability</label><input type="number" id="a-dis" value="0" min="0" max="12000" step="1" inputmode="numeric"><span class="hint">Tax-free. Any amount waives the funding fee.</span></div>
    </div>
    <label class="chk"><input type="checkbox" id="has-b"><span>Add a spouse or co-borrower</span></label>
    <div class="flds" id="b-wrap" hidden>
      <div class="fld"><label for="b-base">Their taxable pay</label><input type="number" id="b-base" value="0" min="0" max="40000" step="50" inputmode="numeric"><span class="hint">Monthly, before taxes.</span></div>
      <div class="fld"><label for="b-free">Their tax-free income</label><input type="number" id="b-free" value="0" min="0" max="15000" step="10" inputmode="numeric"><span class="hint">BAH, BAS, VA disability.</span></div>
    </div>
    <p class="grp">Your household</p>
    <div class="flds">
      <div class="fld"><label for="fam">Family size</label><select id="fam"><option>1</option><option>2</option><option>3</option><option selected>4</option><option>5</option><option>6</option><option>7</option></select><span class="hint">Everyone in the house.</span></div>
      <div class="fld"><label for="debts">Monthly debts</label><input type="number" id="debts" value="450" min="0" max="20000" step="10" inputmode="numeric"><span class="hint">Car, cards, student loans, child support.</span></div>
      <div class="fld"><label for="care">Child care</label><input type="number" id="care" value="0" min="0" max="6000" step="10" inputmode="numeric"></div>
    </div>
    <p class="grp">The house</p>
    <div class="flds">
      <div class="fld"><label for="price">Price you are looking at</label><input type="number" id="price" data-median value="{price}" min="20000" max="3000000" step="1000" inputmode="numeric"></div>
      <div class="fld"><label for="rate">Interest rate %</label><input type="number" id="rate" value="{rate}" min="1" max="15" step="0.125" inputmode="decimal"><span class="hint" data-rate-note>Freddie Mac average</span></div>
      <div class="fld"><label for="downpct">Down payment %</label><input type="number" id="downpct" value="0" min="0" max="50" step="1" inputmode="numeric"><span class="hint">With full entitlement a VA loan needs none.</span></div>
      <div class="fld"><label for="fee">VA funding fee</label><select id="fee"><option value="first">First use</option><option value="again">Used before</option><option value="exempt">Exempt</option></select><span class="hint" id="feehint">2.15% of the loan, financed.</span></div>
      <div class="fld"><label for="sqft">Square feet</label><input type="number" id="sqft" value="1600" min="400" max="8000" step="50" inputmode="numeric"><span class="hint">For the VA's upkeep and utilities figure.</span></div>
    </div>
    <details class="more"><summary>Assumptions you can change</summary><div>
      <div class="flds">
        <div class="fld"><label for="taxrate">Property tax %</label><input type="number" id="taxrate" value="1.11" min="0" max="5" step="0.01" inputmode="decimal"><span class="hint">Of value, per year. Lawton median.</span></div>
        <div class="fld"><label for="insrate">Insurance per $1,000</label><input type="number" id="insrate" value="19.28" min="0" max="80" step="0.01" inputmode="decimal"><span class="hint">Per year. Lawton average.</span></div>
        <div class="fld"><label for="hoa">HOA per month</label><input type="number" id="hoa" value="0" min="0" max="2000" step="5" inputmode="numeric"></div>
        <div class="fld"><label for="withhold">Taxes withheld %</label><input type="number" id="withhold" value="20" min="0" max="45" step="1" inputmode="numeric"><span class="hint">Of taxable pay. Your LES has the real figure.</span></div>
        <div class="fld"><label for="growup">Tax-free gross-up %</label><input type="number" id="growup" value="25" min="0" max="25" step="1" inputmode="numeric"><span class="hint">Lenders use 15 to 25.</span></div>
        <div class="fld"><label for="dticap">Debt-to-income limit %</label><input type="number" id="dticap" value="41" min="20" max="65" step="1" inputmode="numeric"><span class="hint">The VA guideline is 41.</span></div>
        <div class="fld"><label for="region">Region</label><select id="region"><option value="south" selected>South (Oklahoma)</option><option value="mw">Midwest</option><option value="ne">Northeast</option><option value="west">West</option></select></div>
      </div>
    </div></details>
  </div>
  <div class="tout" aria-live="polite">
    <span class="lab">This household supports about</span>
    <div class="big" id="o-max" data-lead="Supportable purchase price">$0</div>
    <div class="sub" id="o-sub">The lower of the two tests a VA lender runs.</div>
    <div class="kv">
      <div><span>Limit from debt-to-income</span><b id="o-maxdti">$0</b></div>
      <div><span>Limit from residual income</span><b id="o-maxres">$0</b></div>
    </div>
    <span class="lab" style="margin-top:16px">At the price you entered</span>
    <div class="kv" style="margin-top:0">
      <div><span>Full monthly payment</span><b id="o-pay" data-lead="Monthly payment">$0</b></div>
      <div><span>Principal and interest</span><b id="o-pi">$0</b></div>
      <div><span>Tax and insurance</span><b id="o-ti">$0</b></div>
      <div><span>Loan amount, with funding fee</span><b id="o-loan">$0</b></div>
      <div class="tot"><span>Debt-to-income <span class="tpill ok" id="p-dti">OK</span></span><b id="o-dti" data-lead="Debt-to-income ratio">0%</b></div>
      <div><span>Residual income <span class="tpill ok" id="p-res">Clears</span></span><b id="o-res" data-lead="VA residual income">$0</b></div>
      <div><span>VA minimum, family of <i id="o-fam" style="font-style:normal">4</i></span><b id="o-req">$0</b></div>
    </div>
    <div class="verdict" id="o-verdict"></div>
    <div class="acts"><button type="button" class="tbtn" id="btn-print">Print or save as PDF</button><a class="tbtn" href="/payment-toolkit.html">Compare loan types</a></div>
  </div>
</div>
""".format(gopts=gopts, year=bah.YEAR, price=int(MEDIAN), rate=RATE)

    body = """<section class="block">
  <h2>How to read it</h2>
  <p>A VA lender runs two tests. <strong>Debt-to-income</strong> is the house payment plus your other debts, divided by your income before taxes. The guideline is 41%. <strong>Residual income</strong> is the cash left each month after taxes, the house, upkeep, and your debts. It has to clear a minimum set by family size. The price at the top is the lower of the two, which is the safer number to shop with.</p>
  <p>BAH, BAS and VA disability are not taxed. Lenders are allowed to count them for more than face value on the debt-to-income test, usually 15% to 25% more. This calculator uses 25%. Ask your lender which figure they use.</p>
  <p>If the residual number is the tight one, the <a href="/va-residual-income-calculator/">residual income calculator</a> breaks it down line by line. The <a href="/guides/va-loan-oklahoma/">VA loan page</a> covers the funding fee, the appraisal, and what a seller can pay.</p>
  <p class="tnote">A retiree rated below 50% usually has disability pay offset against retirement pay. Check your award letter before you count both. Only a lender can pre-approve you, and their worksheet beats this one.</p>
</section>
"""

    script = """(function(){
  var L = window.LBT, GR = __GR__, feeTouched = false;
  L.$("fee").addEventListener("change", function(){ feeTouched = true; });
  function fill(){
    var g = GR[L.$("grade").value];
    if (!g) { L.$("a-bah").value = 0; L.$("a-bas").value = 0; return; }      // not on active duty: no allowances
    L.$("a-bah").value = L.$("deps").value === "wo" ? g[2] : g[1];
    L.$("a-bas").value = g[3];
  }
  L.$("grade").addEventListener("change", fill);
  L.$("deps").addEventListener("change", fill);
  function opts(){
    return { downPct: L.val("downpct", 0, 0, 90), fee: L.$("fee").value, taxRate: L.val("taxrate", 1.11, 0, 10) / 100,
             insPerK: L.val("insrate", 19.28, 0, 200), hoa: L.val("hoa", 0, 0) };
  }
  function run(){
    var hasB = L.$("has-b").checked;
    L.$("b-wrap").hidden = !hasB;
    var dis = L.val("a-dis", 0, 0);
    if (!feeTouched) L.$("fee").value = dis > 0 ? "exempt" : "first";
    var o = opts(), feePct = L.fundingFee(o.fee, o.downPct) * 100;
    L.setText("feehint", feePct ? feePct.toFixed(2).replace(/0$/, "") + "% of the loan, financed." : "No fee with a VA disability rating or a Purple Heart.");
    var taxable = L.val("a-base", 0, 0) + (hasB ? L.val("b-base", 0, 0) : 0);
    var free = L.val("a-bah", 0, 0) + L.val("a-bas", 0, 0) + dis + (hasB ? L.val("b-free", 0, 0) : 0);
    var qual = taxable + free * (1 + L.val("growup", 25, 0, 25) / 100);
    var net = taxable * (1 - L.val("withhold", 20, 0, 60) / 100) + free;
    var debts = L.val("debts", 0, 0), care = L.val("care", 0, 0);
    var mu = L.val("sqft", 1600, 0) * 0.14;
    var rate = L.val("rate", __RATE__, 0.1, 25), price = L.val("price", __PRICE__, 0);
    var fam = parseInt(L.$("fam").value, 10), region = L.$("region").value, cap = L.val("dticap", 41, 10, 80);
    var p = L.payment(price, rate, o);
    var req = L.residualRequired(region, fam, p.loan);
    var dti = qual > 0 ? (p.total + debts + care) / qual * 100 : 0;
    var res = net - p.total - mu - debts - care;
    var payDti = qual * cap / 100 - debts - care, payRes = net - mu - debts - care - L.residualRequired(region, fam, 100000);
    var maxDti = L.maxPrice(payDti, rate, o), maxRes = L.maxPrice(payRes, rate, o);
    var max = Math.floor(Math.min(maxDti, maxRes) / 100) * 100;
    var okD = dti <= cap, okR = res >= req, income = taxable + free > 0;
    L.setText("o-max", income ? L.usd(max) : "$0");
    L.setText("o-sub", !income ? "Put in your income to get a number." :
      maxRes < maxDti ? "Residual income is the test that sets the limit for you." : "Debt-to-income is the test that sets the limit for you.");
    L.setText("o-maxdti", L.usd(Math.floor(maxDti / 100) * 100));
    L.setText("o-maxres", L.usd(Math.floor(maxRes / 100) * 100));
    L.setText("o-pay", L.usd(p.total)); L.setText("o-pi", L.usd(p.pi)); L.setText("o-ti", L.usd(p.tax + p.ins + p.hoa));
    L.setText("o-loan", L.usd(p.loan));
    L.setText("o-dti", dti.toFixed(1) + "%"); L.setText("o-res", L.usd(res)); L.setText("o-req", L.usd(req)); L.setText("o-fam", fam >= 7 ? "7 or more" : fam);
    var pd = L.$("p-dti"); pd.textContent = okD ? "OK" : "Over"; pd.className = "tpill " + (okD ? "ok" : "no");
    var pr = L.$("p-res"); pr.textContent = okR ? "Clears" : "Short"; pr.className = "tpill " + (okR ? "ok" : "no");
    var v = L.$("o-verdict"); v.className = "verdict " + (okD && okR ? "ok" : "no");
    v.textContent = !income ? "" : max <= 0 ? "On these numbers the two tests do not leave room for a house payment yet. Paying down a debt moves it the fastest." :
      okD && okR ? "At " + L.usd(price) + " this household clears both tests, with " + L.usd(res - req) + " a month to spare on residual income."
      : !okR && okD ? "At " + L.usd(price) + " residual income comes up " + L.usd(req - res) + " a month short. Around " + L.usd(max) + " clears it."
      : okR && !okD ? "At " + L.usd(price) + " the debt-to-income ratio is over " + cap + "%. Residual income of " + L.usd(res) + (res >= req * 1.2 ? " is more than 20% over the minimum, which lenders can accept as an offset." : " clears the minimum, and a lender will want other strengths in the file.")
      : "At " + L.usd(price) + " this household misses both tests. Around " + L.usd(max) + " clears them.";
    window.LEAD_SUMMARY = function(){
      return "VA loan calculator\\nSupportable price: " + L.usd(max) + "\\nPrice entered: " + L.usd(price) + ", payment " + L.usd(p.total) +
        "\\nIncome: " + L.usd(taxable) + " taxable, " + L.usd(free) + " tax-free" + (hasB ? " (two borrowers)" : "") +
        "\\nDebts: " + L.usd(debts + care) + ", family of " + fam + "\\nDTI: " + dti.toFixed(1) + "%, residual " + L.usd(res) + " (minimum " + L.usd(req) + ")";
    };
  }
  L.watch(document, run);
  if (window.LBTShare) LBTShare.init();
  L.market(run);
  run();
})();""".replace("__GR__", grades).replace("__RATE__", str(RATE)).replace("__PRICE__", str(int(MEDIAN)))

    faqs = [
        ("How much house can I afford with a VA loan at Fort Sill?",
         "It comes down to two tests. Your house payment plus other debts should stay near 41% of your income before "
         "taxes, and the cash left over each month has to clear the VA's residual income minimum for your family size. "
         "Put your pay and allowances in above and the calculator runs both."),
        ("Does BAH count as income for a VA loan?",
         "Yes. Lenders count BAH, BAS and VA disability compensation as income, and because they are tax-free a lender "
         "can count them for up to 25% more than face value on the debt-to-income test."),
        ("Who does not pay the VA funding fee?",
         "A veteran who receives VA disability compensation, an active-duty Purple Heart recipient, and a surviving "
         "spouse receiving DIC pay no funding fee. Most other first-time users pay 2.15% with less than 5% down, and "
         "it can be financed into the loan."),
    ]
    form = listform("va-listings", "Want to see what is listed in this range?",
                    "Tell me where to send them and I will go through what is listed right now at or under your price. "
                    "I leave off the ones that likely will not pass a VA appraisal and send you the rest myself. You "
                    "get a direct line to me.", "Send me homes in my range")
    tool = mark(tool, {
        "grade": 'data-share="grade" data-share-key', "deps": 'data-share="dep" data-share-key',
        "a-base": 'data-share="pay"', "a-bah": 'data-share="bah"', "a-bas": 'data-share="bas"',
        "a-dis": 'data-share="dis"', "has-b": 'data-share="spouse"', "b-base": 'data-share="spay"',
        "b-free": 'data-share="sfree"', "fam": 'data-share="fam"', "debts": 'data-share="debts"',
        "care": 'data-share="care"', "price": 'data-share="price"', "downpct": 'data-share="down"',
        "fee": 'data-share="fee"', "sqft": 'data-share="sqft"', "taxrate": 'data-share="tax"',
        "insrate": 'data-share="ins"', "hoa": 'data-share="hoa"', "withhold": 'data-share="withheld"',
        "growup": 'data-share="grossup"', "dticap": 'data-share="dti"', "region": 'data-share="region"'})
    return tool_page(
        "va-loan-calculator.html", "va", "va",
        "VA Loan Calculator for Fort Sill Buyers | BAH &amp; Income".replace("&amp;", "&"),
        "A VA loan calculator for Fort Sill households: combine base pay, BAH, BAS, VA disability and a spouse's income, "
        "and see the price both VA tests support.",
        "VA loan calculator", "For Fort Sill households",
        "Put in everyone's pay and allowances. You get the price this household supports on the two tests a VA "
        "lender runs, and the payment on any house you are looking at.",
        tool, body, script, faqs, form, subject="VA loan question", crumb="VA loan calculator", body_class="page-tool page-va")
