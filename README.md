# jonahmeadows.com — new static site

A journalist portfolio page modeled on [alexlubben.com](https://alexlubben.com/),
rebuilt from the old Tumblr site's content. Static files, ready for GitHub Pages.

## Structure

- `index.html` — single page: header, Get in touch, Selected work, Latest articles, More work
- `styles.css` — minimal editorial styling
- `latest.js` — renders the Latest articles section from `data/latest.json`
- `data/latest.json` — latest 10 items from the nola.com author RSS feed (regenerated automatically)
- `scripts/fetch_rss.py` — fetches the RSS feed and rewrites `data/latest.json`
- `.github/workflows/update-articles.yml` — runs `fetch_rss.py` every 6 hours and commits changes

## Deploy to GitHub Pages

1. Create a repo (e.g. `jonahmeadows/jonahmeadows.github.io` for a user site,
   or any repo name for a project site) and push this folder's contents to it.
2. Go to **Settings → Pages** → deploy from the `main` branch (`/` root).
3. The site is live at `https://<user>.github.io/...`.

## Custom domain (jonahmeadows.com)

1. Add a file named `CNAME` at the repo root containing `jonahmeadows.com`.
2. In DNS, point the domain at GitHub Pages:
   - `www` → CNAME to `<user>.github.io`
   - apex → the four A records GitHub documents for Pages
     (see <https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site>)
3. In **Settings → Pages**, enable **Enforce HTTPS** once the certificate provisions.

## Local preview

```sh
cd site && python3 -m http.server 8000
# open http://localhost:8000
```

## Refreshing the feed manually

```sh
python3 scripts/fetch_rss.py
```
