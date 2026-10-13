/* Shared math for the calculators on movingtoftsill.com (the VA loan
   calculator, the residual income calculator, rent vs buy, property tax).
   One copy of the payment math, the VA funding fee tiers, the VA residual
   income tables and the live-rate loader, so every tool agrees with the
   others and with the BAH calculator.

   Local defaults: Lawton property tax 1.11% of value a year, homeowners
   insurance $19.28 per $1,000 of coverage a year. The rate and the median
   price come from /data/market.json (the rate refreshes itself every Monday). */
window.LBT = (function () {
  "use strict";

  var TAX_RATE = 0.0111, INS_PER_K = 19.28;

  function $(id) { return document.getElementById(id); }
  function usd(n) { if (!isFinite(n)) return "$0"; n = Math.round(n); return (n < 0 ? "-$" : "$") + Math.abs(n).toLocaleString("en-US"); }
  function val(id, fallback, lo, hi) {
    var el = $(id), v = el ? parseFloat(el.value) : NaN;
    if (!isFinite(v)) v = fallback;
    if (lo != null && v < lo) v = lo;
    if (hi != null && v > hi) v = hi;
    return v;
  }

  // monthly payment per dollar borrowed
  function factor(ratePct, years) {
    var i = ratePct / 100 / 12, n = (years || 30) * 12;
    if (i <= 0) return 1 / n;
    var g = Math.pow(1 + i, n);
    return i * g / (g - 1);
  }

  // VA funding fee as a fraction of the loan. mode: "first" | "again" | "exempt"
  function fundingFee(mode, downPct) {
    if (mode === "exempt") return 0;
    if (downPct >= 10) return 0.0125;
    if (downPct >= 5) return 0.015;
    return mode === "again" ? 0.033 : 0.0215;
  }

  // Full monthly payment on a VA purchase.
  function payment(price, ratePct, o) {
    o = o || {};
    var years = o.years || 30, downPct = o.downPct || 0;
    var taxRate = o.taxRate != null ? o.taxRate : TAX_RATE;
    var insPerK = o.insPerK != null ? o.insPerK : INS_PER_K;
    var base = price * (1 - downPct / 100);
    var fee = base * fundingFee(o.fee || "first", downPct);
    var loan = base + fee;
    var pi = loan * factor(ratePct, years);
    var tax = price * taxRate / 12;
    var ins = price * insPerK / 12000;
    var hoa = o.hoa || 0;
    return { price: price, base: base, fee: fee, loan: loan, pi: pi, tax: tax, ins: ins, hoa: hoa,
             total: pi + tax + ins + hoa, down: price * downPct / 100 };
  }

  // The price whose full payment equals a monthly budget.
  function maxPrice(budget, ratePct, o) {
    if (!(budget > 0)) return 0;
    var lo = 0, hi = 5000000;
    for (var k = 0; k < 60; k++) {
      var mid = (lo + hi) / 2;
      if (payment(mid, ratePct, o).total > budget) hi = mid; else lo = mid;
    }
    return lo;
  }

  // Loan balance after m monthly payments.
  function balance(loan, ratePct, years, m) {
    var i = ratePct / 100 / 12, n = years * 12;
    if (i <= 0) return loan * (1 - m / n);
    var g = Math.pow(1 + i, m);
    return loan * g - loan * factor(ratePct, years) * (g - 1) / i;
  }

  // VA residual income minimums, 38 CFR 36.4340. Family sizes 1 to 5.
  var RESIDUAL = {
    hi: { ne: [450, 755, 909, 1025, 1062], mw: [441, 738, 889, 1003, 1039],
          south: [441, 738, 889, 1003, 1039], west: [491, 823, 990, 1117, 1158], add: 80 },
    lo: { ne: [390, 654, 788, 888, 921], mw: [382, 641, 772, 868, 902],
          south: [382, 641, 772, 868, 902], west: [425, 713, 859, 967, 1004], add: 75 }
  };
  function residualRequired(region, size, loan) {
    var t = (loan != null && loan < 80000) ? RESIDUAL.lo : RESIDUAL.hi;
    var row = t[region] || t.south;
    size = Math.max(1, Math.round(size));
    if (size <= 5) return row[size - 1];
    return row[4] + Math.min(size - 5, 2) * t.add;   // the table adds per person up to a family of seven
  }

  // Live rate and median. Inputs keep whatever the visitor typed.
  function market(cb) {
    function touched(el) { el.addEventListener("input", function () { el.setAttribute("data-touched", "1"); }); }
    var rate = $("rate"), price = $("price");
    if (rate) touched(rate);
    if (price) touched(price);
    if (!window.fetch) { cb(null); return; }
    fetch("/data/market.json", { cache: "no-cache" })
      .then(function (r) { if (!r.ok) throw new Error(r.status); return r.json(); })
      .then(function (m) {
        var r = m.rate && Number(m.rate.value), med = m.market && Number(m.market.medianPrice);
        if (rate && r > 1 && r < 15 && !rate.getAttribute("data-touched")) rate.value = r;
        if (price && price.hasAttribute("data-median") && med > 20000 && !price.getAttribute("data-touched")) {
          price.value = med;
          try { price.dispatchEvent(new Event("change")); } catch (e) {}   // lets the lead form's price box follow
        }
        var d = String((m.rate && m.rate.asOf) || "").split("-");
        var els = document.querySelectorAll("[data-rate-note]");
        for (var k = 0; k < els.length; k++) {
          if (r && d.length === 3) els[k].textContent = "Freddie Mac average, " + (+d[1]) + "/" + (+d[2]) + "/" + d[0].slice(2);
        }
        cb(m);
      })
      .catch(function () { cb(null); });
  }

  // Re-run fn whenever any input inside root changes.
  function watch(root, fn) {
    var els = (root || document).querySelectorAll("input, select");
    for (var k = 0; k < els.length; k++) {
      els[k].addEventListener("input", fn);
      els[k].addEventListener("change", fn);
    }
  }

  function setText(id, text) { var el = $(id); if (el) el.textContent = text; }

  // Phone layout: mirror the headline answer in a slim bar that sticks under the tool bar.
  (function () {
    var out = document.querySelector(".tout"), calc = document.querySelector(".tcalc");
    if (!out || !calc || !window.MutationObserver) return;
    var big = out.querySelector(".big"), lab = out.querySelector(".lab");
    if (!big || !lab) return;
    var strip = document.createElement("a"), s = document.createElement("span"), b = document.createElement("b");
    strip.className = "tstrip"; strip.setAttribute("aria-hidden", "true"); strip.tabIndex = -1;
    strip.appendChild(s); strip.appendChild(b);
    calc.parentNode.insertBefore(strip, calc);
    var nav = document.querySelector(".toolnav");
    function sync() {
      s.textContent = lab.textContent.replace(/\s+/g, " ").trim();
      b.textContent = big.textContent;
      strip.style.top = (nav ? nav.offsetHeight : 0) + "px";
    }
    strip.addEventListener("click", function () { out.scrollIntoView({ behavior: "smooth", block: "start" }); });
    new MutationObserver(sync).observe(out, { childList: true, characterData: true, subtree: true });
    window.addEventListener("resize", sync);
    sync();
  })();

  var yr = $("yr");
  if (yr) yr.textContent = new Date().getFullYear();
  var printBtn = $("btn-print");
  if (printBtn) printBtn.addEventListener("click", function () { window.print(); });

  return { $: $, usd: usd, val: val, factor: factor, fundingFee: fundingFee, payment: payment, maxPrice: maxPrice,
           balance: balance, residualRequired: residualRequired, RESIDUAL: RESIDUAL, market: market, watch: watch,
           setText: setText, TAX_RATE: TAX_RATE, INS_PER_K: INS_PER_K };
})();
