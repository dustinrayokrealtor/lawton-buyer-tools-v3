/* ==========================================================================
   Lawton Buyer Tools — inline lead form
   --------------------------------------------------------------------------
   Every <form class="leadform" data-source="..."> on a page posts to the
   same Apps Script web app the print gate (leadgate.js) uses, with
   kind "inquiry". The script logs it to the leads sheet, emails Dustin,
   sends the buyer a short confirmation, and copies the lead to Dakno.
   Then the visitor lands on /thanks.html?source=...

   The source tag rides along in the sheet's Page column
   ("Moving to Fort Sill | bah-page") so leads can be counted by placement.
   ========================================================================== */
(function(){
  "use strict";

  var ENDPOINT = "https://script.google.com/macros/s/AKfycbwSkkgNvZqNTFDnO9jp5sIiXGEer16rfLo08lX2XEH41uk5IcsiAI7GPcQ3n-Jxdi2d/exec";
  var KEY      = "lbt.lead.v1";          // shared with leadgate.js so a returning visitor is not asked twice
  var THANKS   = "/thanks.html";

  // Same labels the BAH calculator uses, so the BAH page can pre-fill this.
  var GRADES = ["E-1 to E-4","E-5","E-6","E-7","E-8","E-9","W-1","W-2","W-3","W-4","W-5",
                "O-1E","O-2E","O-3E","O-1","O-2","O-3","O-4","O-5","O-6","O-7",
                "Retired or veteran","DoD civilian or contractor","Other"];
  var WANTS = {
    listings:  "Listings in my price range",
    payment:   "My payment broken down",
    rentcomps: "Rent comps for keeping it as a rental"
  };

  function getLead(){
    try { var o = JSON.parse(localStorage.getItem(KEY) || "null"); return (o && o.email) ? o : null; }
    catch (e) { return null; }
  }
  function saveLead(o){
    try { localStorage.setItem(KEY, JSON.stringify(o)); } catch (e) { /* private mode: fine */ }
  }

  function opt(value, label, selected){
    var o = document.createElement("option");
    o.value = value; o.textContent = label;
    if (selected) o.selected = true;
    return o;
  }

  function fillGrades(sel){
    if (!sel || sel.options.length > 1) return;
    GRADES.forEach(function(g){ sel.appendChild(opt(g, g)); });
  }

  function fillMonths(sel){
    if (!sel || sel.options.length > 2) return;
    var names = ["January","February","March","April","May","June","July",
                 "August","September","October","November","December"];
    var d = new Date(); d.setDate(1);
    for (var i = 0; i < 12; i++) {
      var label = names[d.getMonth()] + " " + d.getFullYear();
      sel.appendChild(opt(label, label));
      d.setMonth(d.getMonth() + 1);
    }
  }

  // BAH page: keep the form's pay grade in step with the calculator until
  // the visitor picks one in the form themselves.
  function syncGrade(form){
    var calc = document.getElementById(form.getAttribute("data-sync-grade") || "");
    var mine = form.elements.grade;
    if (!calc || !mine) return;
    var touched = false;
    mine.addEventListener("change", function(){ touched = true; });
    function pull(){
      if (touched) return;
      var o = calc.options[calc.selectedIndex];
      if (o) mine.value = o.textContent;
    }
    calc.addEventListener("change", pull);
    calc.addEventListener("input", pull);
    pull();
  }

  function bad(input, isBad){
    if (!input) return;
    if (isBad) input.setAttribute("aria-invalid", "true");
    else input.removeAttribute("aria-invalid");
  }

  function setErr(form, msg){
    var el = form.querySelector(".lf-err");
    if (el) el.textContent = msg || "";
  }

  function wants(form){
    var out = [];
    var boxes = form.querySelectorAll('input[name="want"]');
    for (var i = 0; i < boxes.length; i++) if (boxes[i].checked) out.push(boxes[i].value);
    return out;
  }

  function onSubmit(ev){
    ev.preventDefault();
    var form = ev.currentTarget;
    if (form.getAttribute("data-busy") === "1") return;

    var E = form.elements;
    var source = form.getAttribute("data-source") || (E.source && E.source.value) || "site";
    var thanks = THANKS + "?source=" + encodeURIComponent(source);

    // honeypot: a person never sees this field
    if (E.company && E.company.value) { location.href = thanks; return; }

    var name  = (E.name.value  || "").trim();
    var email = (E.email.value || "").trim();
    var phone = (E.phone.value || "").trim();
    var nameBad  = name.length < 2;
    var emailBad = !/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(email);
    var phoneBad = phone.replace(/\D/g, "").length < 10;
    bad(E.name, nameBad); bad(E.email, emailBad); bad(E.phone, phoneBad);
    if (nameBad || emailBad || phoneBad) {
      setErr(form, nameBad ? "Put your name in so I know who I'm talking to."
                 : phoneBad ? "I need a 10-digit phone number to text you."
                 : "That email doesn't look right.");
      (nameBad ? E.name : phoneBad ? E.phone : E.email).focus();
      return;
    }
    setErr(form, "");

    var w = wants(form);
    var grade  = E.grade  ? E.grade.value  : "";
    var report = E.report ? E.report.value : "";
    var notes  = E.notes  ? (E.notes.value || "").trim() : "";

    var L = [];
    L.push("Wants: " + (w.length ? w.map(function(k){ return WANTS[k] || k; }).join("; ") : "Just a conversation"));
    if (grade)  L.push("Pay grade: " + grade);
    L.push("Reports: " + (report || "Not sure yet"));
    if (notes)  L.push("Notes: " + notes);
    L.push("Form: " + source);
    if (w.indexOf("payment") > -1 && typeof window.LEAD_SUMMARY === "function") {
      try { L.push("", "Their calculator run:", window.LEAD_SUMMARY()); } catch (e) {}
    }

    var payload = {
      kind: "inquiry",
      source: source,
      name: name, email: email, phone: phone,
      page: "Moving to Fort Sill | " + source,
      url: location.href.split("#")[0],
      summary: L.join("\n"),
      wants: w.join(","),
      grade: grade, report: report
    };

    saveLead({ name: name, email: email, phone: phone });

    var btn = form.querySelector('button[type="submit"]');
    var label = btn ? btn.textContent : "";
    form.setAttribute("data-busy", "1");
    if (btn) { btn.disabled = true; btn.textContent = "Sending…"; }

    var gone = false;
    function go(){ if (gone) return; gone = true; location.href = thanks; }
    function fail(){
      if (gone) return;
      form.removeAttribute("data-busy");
      if (btn) { btn.disabled = false; btn.textContent = label; }
      setErr(form, "That didn't go through. Try again, or call or text me at 580-351-4683.");
    }

    var req;
    try {
      req = fetch(ENDPOINT, {
        method: "POST", mode: "no-cors", keepalive: true,
        headers: { "Content-Type": "text/plain" },
        body: JSON.stringify(payload)
      });
    } catch (e) { fail(); return; }
    req.then(go, fail);
    // keepalive lets the request finish even if we leave; don't strand a slow phone on "Sending…"
    setTimeout(go, 9000);
  }

  function init(form){
    if (form.getAttribute("data-ready") === "1") return;
    form.setAttribute("data-ready", "1");
    fillGrades(form.elements.grade);
    fillMonths(form.elements.report);
    var lead = getLead();
    if (lead) {
      if (!form.elements.name.value)  form.elements.name.value  = lead.name  || "";
      if (!form.elements.email.value) form.elements.email.value = lead.email || "";
      if (!form.elements.phone.value) form.elements.phone.value = lead.phone || "";
    }
    syncGrade(form);
    form.addEventListener("input", function(ev){
      if (ev.target.getAttribute("aria-invalid")) { bad(ev.target, false); setErr(form, ""); }
    });
    form.addEventListener("submit", onSubmit);
  }

  function boot(){
    var forms = document.querySelectorAll("form.leadform");
    for (var i = 0; i < forms.length; i++) init(forms[i]);
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", boot);
  else boot();
})();
