/* Live numbers for the guide pages (BAH pay grade pages, /guides/ articles).
   Every figure that depends on the mortgage rate or the MLS medians is printed
   into the page when it is built, wrapped in a <span data-live="...">. This
   script reads /data/market.json (the rate refreshes itself every Monday) and
   rewrites those spans so the page never drifts from the calculators. If the
   file can't be loaded the page keeps the numbers already printed in it.

   The math is the same as the BAH calculator: VA loan, nothing down, funding
   fee financed, Lawton tax and insurance.

     data-live="rate" | "ratedate" | "median" | "dom" | "supply"
     data-live="price"   data-budget="1233" [data-ff="2.15"]   price a budget carries
     data-live="pay"     data-price="199900|median" [data-part="pi|tax|ins|loan"] [data-ff]
     data-live="pay"     data-budget="1233" data-part="..."    parts of the payment at that budget
     data-live="share"   data-budget="1233"                    price as a share of the median
     data-live="gap"     data-budget="1233"                    dollars between the budget and the median payment
     data-live="gapline" data-budget="1233"                    the sentence that goes with it
     data-live="per100"                                        house bought by each extra $100 a month
*/
(function () {
  "use strict";
  var TAX_RATE = 0.0111, INS_PER_K = 19.28, FF_DEFAULT = 2.15;

  function usd(n) { return "$" + Math.round(n).toLocaleString("en-US"); }
  function num(v, lo, hi) { v = Number(v); return isFinite(v) && v >= lo && v <= hi ? v : null; }
  function factor(pct) {
    var i = pct / 100 / 12;
    if (i <= 0) return 1 / 360;
    var g = Math.pow(1 + i, 360);
    return i * g / (g - 1);
  }
  function ffOf(el) {
    var v = parseFloat(el.getAttribute("data-ff"));
    return 1 + (isFinite(v) && v >= 0 ? v : FF_DEFAULT) / 100;
  }
  function perDollar(rate, ffMult) { return ffMult * factor(rate) + TAX_RATE / 12 + INS_PER_K / 12000; }
  function parts(price, rate, ffMult) {
    var loan = price * ffMult, pi = loan * factor(rate), tax = price * TAX_RATE / 12, ins = price * INS_PER_K / 12000;
    return { loan: loan, pi: pi, tax: tax, ins: ins, total: pi + tax + ins };
  }
  function shortDate(iso) {
    var p = String(iso || "").split("-");
    return p.length === 3 ? (+p[1]) + "/" + (+p[2]) + "/" + p[0].slice(2) : null;
  }

  function run(m) {
    var rate = m.rate ? num(m.rate.value, 1, 15) : null;
    var mk = m.market || {};
    var median = num(mk.medianPrice, 20000, 5000000);
    if (!rate || !median) return;
    var els = document.querySelectorAll("[data-live]");
    for (var k = 0; k < els.length; k++) {
      var el = els[k], kind = el.getAttribute("data-live"), mult = ffOf(el), out = null;
      var budget = parseFloat(el.getAttribute("data-budget"));
      var priceAttr = el.getAttribute("data-price");
      var price = priceAttr === "median" ? median : parseFloat(priceAttr);
      var part = el.getAttribute("data-part") || "total";
      if (kind === "rate") out = rate.toFixed(2) + "%";
      else if (kind === "ratedate") out = shortDate(m.rate.asOf);
      else if (kind === "median") out = usd(median);
      else if (kind === "dom") out = num(mk.daysOnMarket, 1, 999) ? String(Math.round(mk.daysOnMarket)) : null;
      else if (kind === "supply") out = num(mk.monthsSupply, 0.1, 99) ? Number(mk.monthsSupply).toFixed(1) : null;
      else if (kind === "price" && isFinite(budget)) out = usd(Math.floor(budget / perDollar(rate, mult) / 100) * 100);
      else if (kind === "pay") {
        if (isFinite(budget)) price = budget / perDollar(rate, mult);
        if (isFinite(price)) out = usd(parts(price, rate, mult)[part]);
      }
      else if (kind === "share" && isFinite(budget)) out = Math.round(budget / perDollar(rate, mult) / median * 100) + "%";
      else if (kind === "gap" && isFinite(budget)) out = usd(Math.abs(parts(median, rate, mult).total - budget));
      else if (kind === "gapline" && isFinite(budget)) {
        var d = parts(median, rate, mult).total - budget;
        out = d > 0
          ? "That is about " + usd(d) + " a month short of the payment on a median-priced house."
          : "That covers the payment on a median-priced house with about " + usd(-d) + " a month to spare.";
      }
      else if (kind === "per100") out = usd(Math.round(100 / perDollar(rate, mult) / 100) * 100);
      if (out != null) el.textContent = out;
    }
  }

  var yr = document.getElementById("yr");
  if (yr) yr.textContent = new Date().getFullYear();

  if (!document.querySelector("[data-live]") || !window.fetch) return;
  fetch("/data/market.json", { cache: "no-cache" })
    .then(function (r) { if (!r.ok) throw new Error(r.status); return r.json(); })
    .then(run)
    .catch(function () { /* keep the numbers already on the page */ });
})();
