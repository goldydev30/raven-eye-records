# Raven Eye Records

Website for **Raven Eye Records**, a grassroots black metal label and lyrics codex. The layout borrows from established metal labels (Metal Blade, Prophecy Productions, Nuclear Blast): a sticky header, a hero, a featured-artist grid, news dispatches, a filterable roster and per-artist pages.

It is a plain static site with no build step. Open `index.html` in a browser, or serve the folder:

```sh
python3 -m http.server 8000
```

## Pages

| Page | What it is |
| --- | --- |
| `index.html` | Home: hero, featured artists (rotates daily), label pillars, latest news |
| `roster.html` | All artists, searchable and filterable by country, genre family and label |
| `band.html?b=<slug>` | Artist page: country, genre, current label, lyrical themes, Metallum link, kindred bands |
| `lyrics.html` | Lyrics Codex: themes atlas plus lyric excerpts and commentary |
| `armory.html` | The Armory: gear behind the roster, with fan submissions |
| `news.html` | News |
| `about.html` | Label manifesto |
| `submit.html` | Demo submission guidelines |

## Data

All content lives in `data/`:

- `bands.js`: the roster (`name`, `slug`, `country`, `genre`, `label`, `families`, `themes`, `status`, `formed`, `ma_url`, `bandcamp`, `website`, `image`, `summary`, `featured`).
- `codex.js`: lyric excerpts, translations and commentary. Only publish lyrics with the band's permission.
- `news.js`: news posts, newest first.
- `gear.js`: each band's gear, built from the gear CSV with `python3 scripts/build_gear.py path/to/gear.csv`.

### Fan gear submissions

Fans submit gear through the **Submit a band's gear** issue form (`.github/ISSUE_TEMPLATE/gear-submission.yml`). Each one arrives as a GitHub issue labelled `gear-submission`. To approve one, add a row to the gear CSV with `relationship` set to `fan_submitted` and the issue's URL as `source_url`, rebuild `gear.js`, and close the issue. To reject, close it with a short note. The repository must be public for fans to open issues.

To refresh the roster from a research spreadsheet:

```sh
python3 scripts/build_data.py path/to/bands.csv
```

Column names are matched loosely (see the script's docstring). Set `featured` to `yes` to pin a band to the home page. Band tiles show a faint album cover behind the band's initial. By default the visitor's browser looks one up on Deezer (falling back to iTunes) by exact band name and caches it for 30 days; bands flagged `provisional` skip the lookup so a namesake's cover never appears. To choose the image yourself, put it in `assets/img/bands/` and set the band's `image` field to its path.

## Logo

The logo, a black metal raven with a narrowed, burning eye and a bloody eyeball clamped in its beak, is drawn in code by `scripts/build_logo.py` (a hand-placed silhouette filled with jittered ink strokes and roughened with an SVG filter). Run `python3 scripts/build_logo.py` after changing it; it writes `assets/js/logo.js` (animated inline versions) plus `assets/img/raven-eye.svg` and the favicon `assets/img/sigil.svg`. The raven's eye blinks when the pointer passes over it; the masthead raven also blinks on its own, narrows its eye shut as you scroll past, and drips blood.

## Publishing on GitHub Pages

Settings → Pages → Deploy from a branch → `main` / root. (Pages on a private repository needs a paid GitHub plan.)

## Placeholders to replace

- `demos@raveneyerecords.com` in `submit.html` and `gear@raveneyerecords.com` in `armory.html` (no domain registered yet)
- The newsletter form in the footer is a visual placeholder; connect it to Buttondown, Mailchimp or similar.
