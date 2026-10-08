/* ==========================================================================
   Lawton Buyer Tools — "Print or save as PDF"
   --------------------------------------------------------------------------
   Just opens the browser's print dialog, where "Save as PDF" lives too.
   No form, no email, nothing asked of the visitor.

   This file used to gate the printout behind name, email and phone. That
   gate is gone on purpose: we only ask for contact info when we're giving
   something back for it (listings in their range, a payment breakdown).
   Those asks live in assets/leadform.js. The file name stayed the same so
   every page that already loads it keeps working without an edit.
   ========================================================================== */
(function(){
  "use strict";

  function onClick(e){
    e.preventDefault();
    window.print();
  }

  function bind(){
    var btns = document.querySelectorAll("#btn-print, [data-lead-gate]");
    for (var i = 0; i < btns.length; i++) {
      if (btns[i].__lg) continue;
      btns[i].__lg = true;
      btns[i].addEventListener("click", onClick);
    }
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", bind); else bind();
})();
