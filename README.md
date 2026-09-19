# Lawton Buyer Tools (v3)

Client-facing buyer tools for Lawton and Southwest Oklahoma, published with GitHub
Pages at **[movingtoftsill.com](https://movingtoftsill.com/)**.

v3 carries every page and every tool over from v2 unchanged. The only thing
that changed is the look: a warm cream ground in place of white, and the
Mount Scott / Saddle Mountain skyline — the ridgeline as it actually reads
from the Lawton side — in the navy hero band on every page. See "Design
language" below for what's new and what deliberately didn't move.

| Page | Path |
| --- | --- |
| Moving to Fort Sill (homepage) | `/` |
| Tools landing page | `/tools/` |
| Buyer Payment Toolkit | `/payment-toolkit.html` |
| VA Loan Calculator (household income & residual income) | `/va-loan-calculator.html` |
| Rate Buydown vs Price Cut | `/buydown.html` |
| Buying a Home in Lawton (consult packet) | `/buying-guide.html` |
| What Your BAH Buys at Fort Sill | `/bah/` |
| `/fort-sill/` | redirect stub &rarr; `/` (the old URL, kept alive) |

The Fort Sill relocation guide sits at the site root because the domain is
`movingtoftsill.com` and that is what people search for. The calculators live one
click away at `/tools/`.

Plain static HTML. No build step. Edit a page and push to `main`, and Pages redeploys in a minute or two.

## Lead capture

Every "Print or save as PDF" button runs through `assets/leadgate.js`. The first
click asks for name, email and phone (remembered in that browser), then the page
is snapshotted to a PDF in the browser and posted, with the contact details and a
plain-text summary of the scenario, to a Google Apps Script that emails Dustin,
emails the buyer their copy, and logs the lead to a Google Sheet. The print
dialog opens either way, so a network hiccup never costs a visitor their printout.

One-time setup (about five minutes) is in [`setup/README.md`](setup/README.md).
The web app URL lives in `ENDPOINT` at the top of `assets/leadgate.js`.

Pages that use it: the payment toolkit, the VA loan calculator, the buydown
tool, the BAH calculator, and the buying guide. A page opts in by including the
script and having a `#btn-print` button; an optional `window.LEAD_SUMMARY`
function or `data-lead="Label"` attributes improve the email summary.

## Search / SEO

Every page carries a unique `<title>` and meta description, a `rel=canonical` on
its `https://movingtoftsill.com` URL, Open Graph and Twitter card tags pointing at
`/og-image.png` (1200x630), and JSON-LD. The homepage declares `RealEstateAgent`,
`WebSite` and `Article`; the rest declare `BreadcrumbList`.

`sitemap.xml` lists all seven real pages and is referenced from `robots.txt`.
The `/fort-sill/` stub is `noindex, follow` and canonicalises to `/`, so the old
URL keeps working without competing in search.

**If you add a page,** add it to `sitemap.xml` and give it a canonical tag, or
Google will treat it as an orphan.

Regenerate the share image by editing the source and re-rendering it at 1200x630;
it is a screenshot of the site's own horizon graphic, so it stays on-brand.

## Design language

Every page loads `assets/site.css` first, then its own `<style>` block for
page-specific layout, then `assets/palette-v3.css` last so it can win on
equal specificity. The shared file holds the design language, matched to
pamandbarry.com so these tools read as part of the same business:

| | Value |
| --- | --- |
| Blue | `#004A9A` — headings, links, figures |
| Red | `#B4090B` — actions and the heading rule only |
| Navy band | `#272D3E` · alt ground `#EAEAEA` · pale `#C2D0E0` |
| Display | Playfair Display, 400, always uppercase |
| Body & UI | Outfit — body, labels, and all figures |
| Geometry | `border-radius: 0` on everything, 2px borders, no shadows or gradients |
| Signature | a 205 × 1.6px rule under every section heading |

Two rules that are easy to break by accident:

- **Nothing is rounded.** One rounded corner and the page stops matching.
- **Red does not go on navy** — it comes out at 1.9:1 and disappears. On dark
  bands the action button and the heading rule both turn white. That inversion
  is already in `site.css`; keep it if you add a dark section.

To restyle everything at once, edit the custom properties at the top of
`assets/site.css`. The old RE/MAX-corporate token names (`--rx-blue`, `--cream`,
`--dark`, and so on) are still defined there, remapped onto the new palette, so
any inline `var(--...)` left in the markup keeps working.

### v3: the cream ground and the horizon graphic

`assets/palette-v3.css` layers on top of everything above:

| | Value |
| --- | --- |
| Page ground | `#F7F5EE` (RE/MAX cream), was white |
| Cards & inputs | stay white/`#FFFFFF` so they lift off the cream |
| Tool-card accent | `#B9948A` (ochre), was pale blue |

Every navy `.hero`/`.pagehero` band gets a `.horizon` SVG under the copy: the
Wichita Mountains skyline as seen from Lawton, traced so it reads correctly —
Mount Scott (flat summit, west) is unmistakably a parking lot on top, and
Saddle Mountain (the notch, east) is the other iconic peak. Get either shape
wrong and locals will notice. `.horizon--tall` runs the full band on the
three pages with a `.hero` (home, BAH, Fort Sill); `.horizon--short` sits at
about half that height on the three `.pagehero` calculator pages (payment
toolkit, VA loan calculator, buydown). The buying guide's masthead is
deliberately left alone — it's a print-to-PDF deliverable, single-theme by
design, and doesn't carry a navy band to put a horizon in.

**One deliberate exception to "no gradients":** the sky inside the horizon
SVG is a `linearGradient`, so the navy header blends into the graphic instead
of showing a seam. That exception is scoped to this one SVG. Buttons, cards,
and panels stay flat — don't let a gradient creep in anywhere else.

Dustin Ray, Buyer Specialist · Pam & Barry's Team, RE/MAX Professionals · Each Office Independently Owned and Operated.
