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
| Area pages (gates, schools, each town, PCS checklist...) | `/fort-sill/<page>/` |
| One page per 2026 BAH rate, with and without dependents | `/bah/<grade>-with-dependents/` etc. |
| Guides hub and the articles under it | `/guides/`, `/guides/<page>/` |

The Fort Sill relocation guide sits at the site root because the domain is
`movingtoftsill.com` and that is what people search for. The calculators live one
click away at `/tools/`.

Plain static HTML. No build step. Edit a page and push to `main`, and Pages redeploys in a minute or two.

## Navigation

Every page has the same header (team logos, the team's phone, site and email
next to its name, and Dustin's number) and under it a tool bar that sticks to
the top while you scroll: Fort Sill Guide, Payment, VA Loan, BAH, Buydown,
Buyer's Guide, All Tools. The current page is marked with `aria-current="page"`.
Each tool page ends with a "More tools" row of cards for the other tools. On
phones the same Call / Text and Email bar sits at the bottom of every page, so
the hero doesn't repeat those buttons.

The shared files are linked with a version tag (`assets/site.css?v=4`). When
you change one of them, bump the number on every page so nobody's browser pairs
a cached old stylesheet with new markup.

If you add a page: copy the `<header class="site site4">` block and the
`<nav class="toolnav">` under it from any page, add the new link to the tool bar
on every page, and add a card to the "More tools" rows.

## Lead capture

The rule: we only ask for contact info when we're giving something back for it.
No gates. "Print or save as PDF" just opens the print window (`assets/leadgate.js`
kept its name so no page had to change, but it no longer asks for anything).

The ask is the "Send me homes in my range" form under each calculator result
(payment toolkit, VA loan calculator, buydown tool), plus the existing forms on
the homepage and the BAH page. All of them are `<form class="leadform">` handled
by `assets/leadform.js`, which posts to the Google Apps Script in
`setup/lead-mailer.gs`. That script logs the lead to the Google Sheet, emails
Dustin with the request and the visitor's calculator run, sends the buyer a short
"got it" note, and copies the lead to Dakno.

Useful form attributes: `data-phone="optional"` (email only is fine),
`data-sync-price="price"` (the "Homes up to" box follows the calculator's price
until the visitor types their own), and `data-scenario` (send the calculator run
along). A page's `window.LEAD_SUMMARY` function or `data-lead="Label"` attributes
shape that calculator summary.

One-time Apps Script setup is in [`setup/README.md`](setup/README.md). The web
app URL lives in `ENDPOINT` at the top of `assets/leadform.js` and in each form's
`action` attribute (the no-JavaScript fallback).

## Live market numbers

`data/market.json` holds the 30-year rate and the MLS numbers (median price,
days on market, months of supply, and the "through" date). `assets/market.js`
reads it on the payment toolkit, the VA loan calculator and the buydown tool and
fills in the stat tiles, the "Lawton median is" and "Freddie Mac survey" labels,
the footer date, and the price and rate boxes (unless the visitor typed their
own number).

The rate updates itself every Monday morning
(`.github/workflows/update-rate.yml`, Freddie Mac's weekly survey via FRED). You
can also run it any time from the Actions tab. The MLS numbers are edited by hand
in `data/market.json`. The buying guide and the BAH page still carry these
numbers in written paragraphs with payments worked out from them, so those get
refreshed by hand when the MLS numbers move.

## Generated pages and the weekly queue

The pay grade pages under `/bah/`, the area pages under `/fort-sill/`, the
articles under `/guides/` and the `/guides/` hub are built by
`python3 _build/gen.py`. So are the home page, `/tools/`, the VA loan
calculator, and the four stand-alone tools (`/property-tax-calculator/`,
`/va-residual-income-calculator/`, `/rent-vs-buy/`, `/pcs-timeline/`). Do not
hand-edit those HTML files; the next build overwrites them. Edit the source and
rebuild:

- **BAH rates:** the table at the top of `_build/bah.py`. Update it every
  January, rebuild, and update the same table in the script at the bottom of
  `bah/index.html` (the calculator). The table printed on `/bah/` is rebuilt
  for you, and the pay grade quick-fill on the VA loan calculator follows.
- **Property tax levies:** the `MILLS` table at the top of `_build/tools.py`.
  The county publishes new levies each fall. Update the table and `LEVY_YEAR`.
- **The tools:** `_build/tools.py` (property tax, residual income, rent vs
  buy, PCS timeline) and `_build/vacalc.py` (VA loan calculator). The math they
  share is in `assets/tools.js`, one copy, so every tool agrees with the others.
- **Shareable links:** `assets/share.js`. Any field marked `data-share="name"`
  can be set from the address bar, so `/bah/?grade=E-6&dep=w` opens the BAH
  calculator on E-6 with dependents. The "Copy link with these numbers" button
  on each calculator builds the link from what is on screen. Only fields the
  visitor touched (plus a few key ones) go in a link, never the live rate.
  Keep the property tax area keys in `MILLS` the same from year to year so old
  links keep working.
- **Home page and /tools/:** `_build/hubs.py`. The tool tiles, the tool bar and
  the row of tools at the foot of each page all come from the `TOOLS` and `NAV`
  lists in `_build/common.py`. Add a tool there and it shows up everywhere.
- **Articles:** one file each in `_build/content/`. A META block of settings
  on top, plain HTML below. `_build/articles.py` explains the keys.
- **Look and chrome:** `_build/common.py` and `assets/guide.css`.

Numbers that depend on the mortgage rate or the MLS medians are written as
`{{tokens}}` in the source (`{{pay price=200000}}`, `{{price budget=1233}}`,
`{{rate}}`, `{{median}}`). The build prints today's value and
`assets/guide-live.js` keeps it current in the browser from
`data/market.json`, so nothing needs rebuilding when the rate moves. The
table and the worked sentences on `/bah/` use the same spans.

**The queue.** An article whose META has a `"queue"` entry is written to
`/_queue/` instead of going live. Every Monday morning
`.github/workflows/publish-queue.yml` publishes the oldest one: it moves it to
its address, links it from `/guides/`, and adds it to `sitemap.xml`. A
`"notBefore"` date holds an article back. To publish early, run the workflow
by hand from the Actions tab.

**Uploading without git.** Anything pushed into `/_publish-now/` is moved into
place by the same workflow. See `HOW-THIS-WORKS.md` in that folder.

Folders that start with an underscore (`_build`, `_queue`, `_publish-now`) are
not served by GitHub Pages.

## Search / SEO

Every page carries a unique `<title>` and meta description, a `rel=canonical` on
its `https://movingtoftsill.com` URL, Open Graph and Twitter card tags pointing at
`/og-image.png` (1200x630), and JSON-LD. The homepage declares `RealEstateAgent`,
`WebSite` and `Article`; the rest declare `BreadcrumbList`.

`sitemap.xml` lists every real page and is referenced from `robots.txt`. The build and the weekly publisher add new pages to it.
The `/fort-sill/` stub is `noindex, follow` and canonicalises to `/`, so the old
URL keeps working without competing in search.

**If you add a page,** add it to `sitemap.xml` and give it a canonical tag, or
Google will treat it as an orphan.

Regenerate the share image by editing the source and re-rendering it at 1200x630;
it is a screenshot of the site's own horizon graphic, so it stays on-brand.

## Design language

Every page loads `assets/site.css` first, then its own `<style>` block for
page-specific layout, then `assets/palette-v3.css`, then `assets/v5.css` last.
`v5.css` is the October 2026 tightening: slimmer header and hero bands, the
two-column tool layout (inputs left, answer right), the tools row, and the
home and tools page grids. Take its `<link>` off a page and that page goes
back to the roomier layout. The shared file holds the design language, matched to
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

<!-- rebuild -->
