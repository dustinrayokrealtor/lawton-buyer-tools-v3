/* ==========================================================================
   Lawton Buyer Tools — lead gate for "Print or save as PDF"
   --------------------------------------------------------------------------
   First click asks for name, email and phone (stored in this browser only,
   so a returning visitor is not asked twice). Every print then:
     1. snapshots the page to a PDF in the browser (html2pdf.js),
     2. posts name / email / phone / scenario summary / PDF to ENDPOINT
        (a Google Apps Script web app that emails Dustin and logs the lead),
     3. opens the browser's print dialog.
   Nothing here ever blocks the print: if the PDF library or the network
   fails, the visitor still gets their printout.

   SETUP: paste the deployed Apps Script web app URL into ENDPOINT below.
   ========================================================================== */
(function(){
  "use strict";

  var ENDPOINT = "https://script.google.com/macros/s/AKfycbwSkkgNvZqNTFDnO9jp5sIiXGEer16rfLo08lX2XEH41uk5IcsiAI7GPcQ3n-Jxdi2d/exec";
  var PDF_LIB  = "https://cdnjs.cloudflare.com/ajax/libs/html2pdf.js/0.10.1/html2pdf.bundle.min.js";
  var KEY      = "lbt.lead.v1";

  var $ = function(s, root){ return (root || document).querySelector(s); };

  // ---------- stored contact ----------
  function getLead(){
    try {
      var raw = localStorage.getItem(KEY);
      if (!raw) return null;
      var o = JSON.parse(raw);
      return (o && o.email) ? o : null;
    } catch (e) { return null; }
  }
  function saveLead(o){
    try { localStorage.setItem(KEY, JSON.stringify(o)); } catch (e) { /* private mode: fine */ }
  }

  // ---------- modal ----------
  var backdrop, form, busy = false, pendingBtn = null;

  function buildModal(){
    if (backdrop) return;
    backdrop = document.createElement("div");
    backdrop.className = "lg-backdrop";
    backdrop.hidden = true;
    backdrop.innerHTML =
      '<div class="lg-modal" role="dialog" aria-modal="true" aria-labelledby="lg-title">' +
        '<h2 id="lg-title">Get your copy</h2>' +
        '<p>Tell me where to send it and I\'ll email you a PDF of exactly what you\'re looking at, then the print window opens.</p>' +
        '<form id="lg-form" novalidate>' +
          '<div class="lg-field"><label for="lg-name">Name</label>' +
            '<input id="lg-name" name="name" type="text" autocomplete="name" required></div>' +
          '<div class="lg-field"><label for="lg-email">Email</label>' +
            '<input id="lg-email" name="email" type="email" autocomplete="email" inputmode="email" required></div>' +
          '<div class="lg-field"><label for="lg-phone">Phone</label>' +
            '<input id="lg-phone" name="phone" type="tel" autocomplete="tel" inputmode="tel" required></div>' +
          '<div class="lg-err" id="lg-err" aria-live="polite"></div>' +
          '<div class="lg-row">' +
            '<button type="submit" class="lg-primary" id="lg-go">Send my copy &amp; print</button>' +
            '<button type="button" class="lg-cancel" id="lg-cancel">Not now</button>' +
          '</div>' +
        '</form>' +
        '<p class="lg-fine">Dustin Ray, Buyer Specialist, Pam &amp; Barry\'s Team RE/MAX Professionals. I\'ll follow up personally and never share your info.</p>' +
      '</div>';
    document.body.appendChild(backdrop);
    form = $("#lg-form", backdrop);

    $("#lg-cancel", backdrop).addEventListener("click", closeModal);
    backdrop.addEventListener("click", function(e){ if (e.target === backdrop) closeModal(); });
    document.addEventListener("keydown", function(e){ if (e.key === "Escape" && !backdrop.hidden) closeModal(); });

    form.addEventListener("submit", function(e){
      e.preventDefault();
      var lead = {
        name:  $("#lg-name", form).value.trim(),
        email: $("#lg-email", form).value.trim(),
        phone: $("#lg-phone", form).value.trim()
      };
      var err = validate(lead);
      $("#lg-err", form).textContent = err || "";
      if (err) return;
      lead.since = new Date().toISOString();
      saveLead(lead);
      closeModal();
      run(lead, pendingBtn);
    });
  }

  function validate(l){
    var bad = function(id, on){ var el = $("#" + id, form); if (el) el.setAttribute("aria-invalid", on ? "true" : "false"); };
    var digits = l.phone.replace(/\D/g, "");
    var emailOk = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(l.email);
    bad("lg-name", l.name.length < 2);
    bad("lg-email", !emailOk);
    bad("lg-phone", digits.length < 10);
    if (l.name.length < 2) return "Your name, so I know who I'm sending this to.";
    if (!emailOk) return "That email doesn't look right.";
    if (digits.length < 10) return "A 10-digit phone number, please.";
    return "";
  }

  function openModal(btn){
    buildModal();
    pendingBtn = btn;
    $("#lg-err", form).textContent = "";
    backdrop.hidden = false;
    setTimeout(function(){ $("#lg-name", form).focus(); }, 30);
  }
  function closeModal(){ if (backdrop) backdrop.hidden = true; }

  // ---------- toast ----------
  var toastEl, toastTimer;
  function toast(msg, ms){
    if (!toastEl){
      toastEl = document.createElement("div");
      toastEl.className = "lg-toast";
      toastEl.setAttribute("role", "status");
      document.body.appendChild(toastEl);
    }
    toastEl.textContent = msg;
    toastEl.hidden = false;
    clearTimeout(toastTimer);
    toastTimer = setTimeout(function(){ toastEl.hidden = true; }, ms || 4000);
  }

  // ---------- scenario summary (plain text for the email body) ----------
  function labelFor(el){
    var l = el.id ? document.querySelector('label[for="' + el.id + '"]') : null;
    if (!l) l = el.closest("label");
    if (!l) return "";
    var t = l.cloneNode(true);
    Array.prototype.forEach.call(t.querySelectorAll("input,select,.sub,.hint"), function(x){ x.remove(); });
    return t.textContent.replace(/\s+/g, " ").trim();
  }
  function visible(el){ return !!(el.offsetParent || el.getClientRects().length); }

  function summary(){
    if (typeof window.LEAD_SUMMARY === "function"){
      try { return String(window.LEAD_SUMMARY()); } catch (e) { /* fall through */ }
    }
    var out = [];
    Array.prototype.forEach.call(document.querySelectorAll("input, select"), function(el){
      if (el.closest(".lg-backdrop") || !visible(el)) return;
      var lab = labelFor(el); if (!lab) return;
      var v;
      if (el.type === "checkbox") v = el.checked ? "yes" : "no";
      else if (el.tagName === "SELECT") v = el.options[el.selectedIndex] ? el.options[el.selectedIndex].text : el.value;
      else v = el.value;
      out.push(lab + ": " + v);
    });
    Array.prototype.forEach.call(document.querySelectorAll("[data-lead]"), function(el){
      if (!visible(el)) return;
      out.push((el.getAttribute("data-lead") || "") + ": " + el.textContent.replace(/\s+/g, " ").trim());
    });
    return out.join("\n");
  }

  // ---------- PDF snapshot ----------
  var libPromise = null;
  function loadLib(){
    if (window.html2pdf) return Promise.resolve();
    if (libPromise) return libPromise;
    libPromise = new Promise(function(res, rej){
      var s = document.createElement("script");
      s.src = PDF_LIB; s.async = true;
      s.onload = res; s.onerror = function(){ rej(new Error("pdf lib failed")); };
      document.head.appendChild(s);
    });
    return libPromise;
  }

  function makePdf(){
    return loadLib().then(function(){
      var shown = [];
      Array.prototype.forEach.call(document.querySelectorAll(".panel[hidden]"), function(p){ p.hidden = false; shown.push(p); });
      document.body.classList.add("pdf-mode");
      var y = window.scrollY; window.scrollTo(0, 0);
      var cleanup = function(){
        document.body.classList.remove("pdf-mode");
        shown.forEach(function(p){ p.hidden = true; });
        window.scrollTo(0, y);
      };
      // Render the clone at a fixed desktop width so a phone gets the same
      // PDF as a laptop, and size the canvas to match so nothing is clipped.
      var W = Math.max(document.documentElement.clientWidth || 0, 1120);
      var opts = {
        margin: [8, 8, 10, 8],
        image: { type: "jpeg", quality: 0.8 },
        html2canvas: { scale: 1.25, useCORS: true, scrollX: 0, scrollY: 0, width: W, windowWidth: W, logging: false },
        jsPDF: { unit: "mm", format: "letter", orientation: "portrait" },
        pagebreak: { mode: ["css", "legacy"], avoid: [".card", ".tw", "tr", ".controls", ".hero", ".note", ".result", ".stack"] }
      };
      var timeout = new Promise(function(_, rej){ setTimeout(function(){ rej(new Error("pdf timeout")); }, 25000); });
      var work = window.html2pdf().set(opts).from(document.body).outputPdf("datauristring");
      return Promise.race([work, timeout]).then(function(uri){ cleanup(); return uri; }, function(err){ cleanup(); throw err; });
    });
  }

  // ---------- send ----------
  var lastSig = "";
  function send(lead, pdfUri){
    if (!ENDPOINT){ console.warn("[leadgate] ENDPOINT not set; lead not sent", lead); return Promise.resolve(false); }
    var sum = summary();
    var sig = lead.email + "|" + document.title + "|" + sum;
    if (sig === lastSig) return Promise.resolve(true);   // same scenario re-printed within this visit
    lastSig = sig;
    var payload = {
      name: lead.name, email: lead.email, phone: lead.phone,
      page: document.title, url: location.href,
      summary: sum,
      filename: (document.title.split("|")[0].trim().replace(/[^\w\- ]+/g, "").replace(/\s+/g, "-") || "lawton-buyer-tools") + ".pdf",
      pdf: pdfUri ? pdfUri.split(",")[1] : ""
    };
    return fetch(ENDPOINT, { method: "POST", mode: "no-cors", headers: { "Content-Type": "text/plain" }, body: JSON.stringify(payload) })
      .then(function(){ return true; }, function(e){ console.warn("[leadgate] send failed", e); return false; });
  }

  // ---------- the whole flow ----------
  function run(lead, btn){
    if (busy) return;
    busy = true;
    var label = btn ? btn.textContent : "";
    if (btn){ btn.disabled = true; btn.textContent = "Preparing your PDF…"; }
    toast("Building your PDF…", 20000);
    makePdf().then(null, function(e){ console.warn("[leadgate] pdf failed", e); return null; })
      .then(function(uri){
        var sent = send(lead, uri);
        sent.then(function(ok){
          toast(ok ? "Sent to " + lead.email + ". Opening print…" : "Opening print…", 3500);
        });
        setTimeout(function(){ window.print(); }, 250);
      })
      .then(function(){ done(); }, function(){ done(); });
    function done(){
      busy = false;
      if (btn){ btn.disabled = false; btn.textContent = label; }
    }
  }

  function onClick(e){
    e.preventDefault();
    var btn = e.currentTarget;
    var lead = getLead();
    if (lead) run(lead, btn); else openModal(btn);
  }

  function bind(){
    Array.prototype.forEach.call(document.querySelectorAll("#btn-print, [data-lead-gate]"), function(b){
      if (b.__lg) return;
      b.__lg = true;
      b.addEventListener("click", onClick);
    });
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", bind); else bind();
})();
