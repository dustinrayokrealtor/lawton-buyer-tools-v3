# Drop files here to publish them

Anything pushed into this folder is moved into place by the "Publish pages"
workflow (`.github/workflows/publish-queue.yml`) within a minute or two.

The file name is the destination path with `__` where the slashes go:

| Upload this | It lands at |
| --- | --- |
| `fort-sill__elgin__index.html` | `/fort-sill/elgin/index.html` |
| `assets__guide.css` | `/assets/guide.css` |
| `index.html` | `/index.html` |

This exists so a batch of pages in different folders can go up in one flat
upload from the GitHub website. Files under `.github/` cannot be placed this
way. This folder is not served by GitHub Pages.
