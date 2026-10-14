/* Shareable calculator links.

   Any input, select, checkbox, radio or toggle button marked
   data-share="name" can be set from the address bar, so
     /bah/?grade=E-6&dep=w
   opens the BAH calculator with E-6 and dependents already picked. The
   visitor can still change anything.

   Which fields go into a link: the ones the visitor actually touched, plus
   any marked data-share-key (the few that make a link make sense, like the
   pay grade). Numbers the site fills in by itself, like the live rate or the
   median price, stay out, so an old link still picks up today's rate.

   Markup:
     data-share="name"     the parameter name
     data-share-key        always included
     data-share-text       a select shares its option text ("E-6"), not its value
     data-share-value="v"  on a toggle button: the value that button stands for

   A button with id="btn-share" copies the link, or opens the phone's share
   sheet. The address bar follows along too, so a bookmark or the browser's
   own share button carries the same numbers.

   Each page calls LBTShare.init() after its own listeners are wired up.
   Only numbers and picks ever go in a link. Never a name or a contact. */
window.LBTShare = (function () {
  "use strict";

  var MARK = "data-sh";        // set on a field the visitor touched or a link filled in
  var started = false;

  function norm(s) { return String(s == null ? "" : s).toLowerCase().replace(/[^a-z0-9.]/g, ""); }
  function all() { return [].slice.call(document.querySelectorAll("[data-share]")); }
  function fire(el, type) { try { el.dispatchEvent(new Event(type, { bubbles: true })); } catch (e) {} }

  // fields grouped by parameter name, in page order
  function groups() {
    var out = [], seen = {};
    all().forEach(function (el) {
      var n = el.getAttribute("data-share");
      if (!seen[n]) { seen[n] = { name: n, els: [] }; out.push(seen[n]); }
      seen[n].els.push(el);
    });
    return out;
  }

  function current(g) {
    var el = g.els[0];
    if (el.tagName === "BUTTON") {
      for (var i = 0; i < g.els.length; i++) if (g.els[i].getAttribute("aria-pressed") === "true") return g.els[i].getAttribute("data-share-value");
      return null;
    }
    if (el.type === "radio") {
      for (var j = 0; j < g.els.length; j++) if (g.els[j].checked) return g.els[j].value;
      return null;
    }
    if (el.type === "checkbox") return el.checked ? "1" : "0";
    if (el.tagName === "SELECT" && el.hasAttribute("data-share-text")) {
      var o = el.options[el.selectedIndex];
      return o ? o.text.replace(/\s+/g, "") : null;
    }
    return el.value === "" ? null : String(el.value);
  }

  function pickOption(sel, v) {
    var n = norm(v), alt = /^e[1-4]$/.test(n) ? "e1toe4" : null;   // E-1 through E-4 share one BAH rate
    for (var i = 0; i < sel.options.length; i++) {
      var o = sel.options[i], t = norm(o.text), val = norm(o.value);
      if (val === n || t === n || (alt && t === alt)) { sel.selectedIndex = i; return true; }
    }
    return false;
  }

  // put one value from the link into its field; true if it took
  function apply(g, v) {
    var el = g.els[0], ok = false, target = el;
    if (el.tagName === "BUTTON") {
      for (var i = 0; i < g.els.length; i++) {
        if (norm(g.els[i].getAttribute("data-share-value")) === norm(v)) {
          if (g.els[i].getAttribute("aria-pressed") !== "true") g.els[i].click();
          target = g.els[i]; ok = true; break;
        }
      }
      if (ok) g.els.forEach(function (b) { b.setAttribute(MARK, "1"); });
      return ok;
    }
    if (el.type === "radio") {
      for (var j = 0; j < g.els.length; j++) {
        if (norm(g.els[j].value) === norm(v)) { g.els[j].checked = true; target = g.els[j]; ok = true; break; }
      }
    } else if (el.type === "checkbox") {
      el.checked = /^(1|y|yes|true|on)$/i.test(v); ok = true;
    } else if (el.tagName === "SELECT") {
      ok = pickOption(el, v);
    } else if (el.type === "date") {
      if (/^\d{4}-\d{2}-\d{2}$/.test(v)) { el.value = v; ok = true; }
    } else {
      var num = parseFloat(String(v).replace(/[$,\s]/g, ""));
      if (isFinite(num)) { el.value = num; ok = true; }
    }
    if (!ok) return false;
    g.els.forEach(function (x) { x.setAttribute(MARK, "1"); x.setAttribute("data-touched", "1"); });
    fire(target, "input");
    fire(target, "change");
    return true;
  }

  function link() {
    var q = [];
    groups().forEach(function (g) {
      var keep = g.els.some(function (x) { return x.hasAttribute("data-share-key") || x.hasAttribute(MARK); });
      if (!keep) return;
      var v = current(g);
      if (v == null || v === "") return;
      q.push(encodeURIComponent(g.name) + "=" + encodeURIComponent(v).replace(/%2C/gi, ","));
    });
    return location.origin + location.pathname + (q.length ? "?" + q.join("&") : "");
  }

  var pending = null;
  function sync() {
    clearTimeout(pending);
    pending = setTimeout(function () {
      try { history.replaceState(history.state, "", link()); } catch (e) {}
    }, 250);
  }

  function touched(e) {
    if (!e.isTrusted) return;
    var el = e.target && e.target.closest ? e.target.closest("[data-share]") : null;
    if (!el) return;
    var name = el.getAttribute("data-share");
    all().forEach(function (x) { if (x.getAttribute("data-share") === name) x.setAttribute(MARK, "1"); });
    sync();
  }

  function shareButton() {
    var btn = document.getElementById("btn-share");
    if (!btn) return;
    var phone = !!navigator.share && window.matchMedia && matchMedia("(pointer: coarse)").matches;
    var label = phone ? "Share these numbers" : "Copy link to these numbers";
    btn.textContent = label;
    function flash(t) { btn.textContent = t; setTimeout(function () { btn.textContent = label; }, 2500); }
    btn.addEventListener("click", function () {
      var url = link();
      try { history.replaceState(history.state, "", url); } catch (e) {}
      if (phone) {
        navigator.share({ title: document.title.split(" | ")[0], url: url }).catch(function () {});
        return;
      }
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(url).then(function () { flash("Link copied"); },
          function () { window.prompt("Copy this link:", url); });
      } else {
        window.prompt("Copy this link:", url);
      }
    });
  }

  function init() {
    if (started) return;
    started = true;
    var params = {};
    try { new URLSearchParams(location.search).forEach(function (v, k) { params[k.toLowerCase()] = v; }); } catch (e) {}
    var used = false;
    groups().forEach(function (g) {
      var v = params[g.name.toLowerCase()];
      if (v != null && v !== "" && apply(g, v)) used = true;
    });
    document.addEventListener("input", touched, true);
    document.addEventListener("change", touched, true);
    document.addEventListener("click", function (e) {
      if (e.isTrusted && e.target && e.target.closest && e.target.closest("button[data-share]")) touched(e);
    }, true);
    shareButton();
    if (used || location.search) sync();
    return used;
  }

  return { init: init, link: link };
})();
