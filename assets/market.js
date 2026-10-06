/* Live market numbers for the payment toolkit.
   Reads /data/market.json (rate is refreshed every Monday by a GitHub Action,
   the MLS numbers are edited by hand) and fills in the stat tiles, the hint
   labels, the footer date and the calculator inputs. If the file can't be
   loaded the page just keeps the numbers already printed in it. */
(function () {
  "use strict";
  var KEY = "lbpt.mkt";
  var LEGACY_RATE = 6.76, LEGACY_PRICE = 199500; // what the page shipped with

  function $(id) { return document.getElementById(id); }
  function near(a, b) { return Math.abs(a - b) < 0.0005; }
  function num(v, lo, hi) { v = Number(v); return isFinite(v) && v >= lo && v <= hi ? v : null; }
  function usd(n) { return "$" + Math.round(n).toLocaleString("en-US"); }
  function parts(iso) { var p = String(iso || "").split("-"); return p.length === 3 ? p : null; }
  function shortDate(iso) { var p = parts(iso); return p ? (+p[1]) + "/" + (+p[2]) + "/" + p[0].slice(2) : null; }
  function longDate(iso) { var p = parts(iso); return p ? (+p[1]) + "/" + (+p[2]) + "/" + p[0] : null; }
  function load() { try { return JSON.parse(localStorage.getItem(KEY)) || {}; } catch (e) { return {}; } }
  function save(o) { try { localStorage.setItem(KEY, JSON.stringify(o)); } catch (e) {} }

  function setInput(id, val) {
    var el = $(id);
    if (!el) return;
    el.value = val;
    el.dispatchEvent(new Event("input", { bubbles: true }));
    el.dispatchEvent(new Event("change", { bubbles: true }));
  }

  function setTile(labelRx, text) {
    var spans = document.querySelectorAll(".phstats span");
    for (var i = 0; i < spans.length; i++) {
      if (labelRx.test(spans[i].textContent)) {
        var b = spans[i].parentNode.querySelector("b");
        if (b) b.textContent = text;
      }
    }
  }

  function setHint(startRx, text) {
    var hints = document.querySelectorAll(".hint");
    for (var i = 0; i < hints.length; i++) {
      if (startRx.test(hints[i].textContent)) hints[i].textContent = text;
    }
  }

  function setFooterDate(date) {
    var w = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT, null), n;
    while ((n = w.nextNode())) {
      if (/year to date through/i.test(n.nodeValue)) {
        n.nodeValue = n.nodeValue.replace(/(year to date through )\d{1,2}\/\d{1,2}\/\d{2,4}/i, "$1" + date);
      }
    }
  }

  function apply(m, force) {
    var prev = load();
    var rate = m.rate ? num(m.rate.value, 1, 15) : null;
    var mk = m.market || {};
    var price = num(mk.medianPrice, 20000, 5000000);
    var dom = num(mk.daysOnMarket, 1, 999);
    var supply = num(mk.monthsSupply, 0.1, 99);

    // Stat tiles and labels (always safe to overwrite).
    if (price) { setTile(/median sale price/i, usd(price)); setHint(/^Lawton median is/i, "Lawton median is " + usd(price)); }
    if (rate) {
      setTile(/30yr rate/i, rate.toFixed(2) + "%");
      var d = shortDate(m.rate.asOf);
      if (d) setHint(/^Freddie Mac survey/i, "Freddie Mac survey, " + d);
    }
    if (dom) setTile(/days on market/i, Math.round(dom) + " days");
    if (supply) setTile(/months of supply/i, supply.toFixed(1) + " mo.");
    if (longDate(mk.throughDate)) setFooterDate(longDate(mk.throughDate));

    // Calculator inputs: only move them if the visitor hasn't typed their own
    // number (i.e. the box still holds a number the site itself put there).
    if (rate) {
      var cur = parseFloat(($("rate") || {}).value);
      var oldRate = prev.rate != null ? prev.rate : LEGACY_RATE;
      if (force || !isFinite(cur) || near(cur, oldRate) || near(cur, LEGACY_RATE)) setInput("rate", rate);
    }
    if (price) {
      var curP = parseFloat(($("price") || {}).value);
      var oldP = prev.price != null ? prev.price : LEGACY_PRICE;
      if (force || !isFinite(curP) || near(curP, oldP) || near(curP, LEGACY_PRICE)) setInput("price", price);
    }
    save({ rate: rate != null ? rate : prev.rate, price: price != null ? price : prev.price });
  }

  function run(m) {
    apply(m, false);
    var reset = $("btn-reset");
    if (reset) reset.addEventListener("click", function () { setTimeout(function () { apply(m, true); }, 0); });
  }

  fetch("/data/market.json", { cache: "no-cache" })
    .then(function (r) { if (!r.ok) throw new Error(r.status); return r.json(); })
    .then(function (m) {
      if (document.readyState === "complete") run(m);
      else window.addEventListener("load", function () { run(m); });
    })
    .catch(function () { /* keep the numbers already on the page */ });
})();
