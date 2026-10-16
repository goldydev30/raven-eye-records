#!/usr/bin/env python3
"""Rebuild data/bands.js from a CSV of band research.

Usage: python3 scripts/build_data.py path/to/bands.csv

Column names are matched loosely (case-insensitive). Recognised columns:
  name|band, country|nationality, genre, label|current_label, family|families|genre_family,
  themes|lyrical_themes, status, formed|formed_in, location, url|ma_url|metallum_url,
  bandcamp, website, image, summary, featured, ambiguous|provisional
Multi-value cells (families, themes) may be separated by ';' or '|'. Themes also accept ','.
Existing fields in data/bands.js that the CSV leaves blank are kept.
"""
import csv, json, re, sys, unicodedata, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "bands.js"

ALIASES = {
    "name": ["name", "band", "band_name"],
    "country": ["country", "nationality", "country_of_origin"],
    "genre": ["genre", "genres", "metallum_genre"],
    "label": ["label", "current_label", "labels"],
    "families": ["families", "family", "genre_family", "genre_families"],
    "themes": ["themes", "lyrical_themes", "lyrical_theme"],
    "status": ["status"],
    "formed": ["formed", "formed_in", "year_formed"],
    "location": ["location"],
    "ma_url": ["ma_url", "url", "metallum_url", "metal_archives_url", "encyclopaedia_metallum"],
    "bandcamp": ["bandcamp"],
    "website": ["website", "official_site"],
    "image": ["image"],
    "summary": ["summary", "bio", "notes_public"],
    "featured": ["featured"],
    "provisional": ["ambiguous", "provisional"],
}

def clean_label(v):
    # "Indie Recordings (latest album); 2026 singles self-released" -> "Indie Recordings"
    v = re.sub(r"\s*\([^)]*\)", "", v)
    return v.split(";")[0].strip()

def clean_themes(v):
    # Drop research notes in brackets, normalise case, de-duplicate, skip sentence-length entries.
    v = re.sub(r"\s*[\(\[][^\)\]]*[\)\]]?", "", v)
    out, seen = [], set()
    for t in split(v, commas=True):
        t = t.strip(" .-")
        if not t or len(t) > 40 or t.lower() in ("unknown", "n/a", "unverified"):
            continue
        t = t[0].upper() + t[1:]
        if t.lower() not in seen:
            seen.add(t.lower())
            out.append(t)
    return out

def clean_status(v):
    # Keep a short "future uncertain" note; other parentheticals are research notes.
    if re.search(r"\(\s*future uncertain\s*\)", v, re.I):
        return re.sub(r"\s*\([^)]*\)", "", v).strip() + ", future uncertain"
    return re.sub(r"\s*\([^)]*\)", "", v).strip()

def slugify(s):
    s = unicodedata.normalize("NFD", s).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")

def split(v, commas=False):
    parts = re.split(r"[;|]" if not commas else r"[;|,]", v or "")
    return [p.strip() for p in parts if p.strip()]

def load_existing():
    if not OUT.exists():
        return []
    text = OUT.read_text(encoding="utf-8")
    return json.loads(text[text.index("["): text.rindex("]") + 1])

def main(path):
    existing = {b["slug"]: b for b in load_existing()}
    with open(path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        cols = {c.strip().lower().replace(" ", "_"): c for c in reader.fieldnames}
        pick = {k: next((cols[a] for a in al if a in cols), None) for k, al in ALIASES.items()}
        if not pick["name"]:
            sys.exit("CSV needs a name or band column; found: %s" % reader.fieldnames)
        for row in reader:
            name = (row[pick["name"]] or "").strip()
            if not name:
                continue
            slug = slugify(name)
            b = existing.get(slug, {"name": name, "slug": slug})
            for key, col in pick.items():
                if key == "name" or not col:
                    continue
                raw = (row.get(col) or "").strip()
                if not raw or raw.lower() in ("n/a", "unknown", "?"):
                    continue
                if key == "families":
                    b[key] = split(raw)
                elif key == "themes":
                    b[key] = clean_themes(raw)
                elif key in ("featured", "provisional"):
                    b[key] = raw.lower() in ("1", "true", "yes", "y")
                elif key == "label":
                    b[key] = clean_label(raw)
                elif key in ("genre", "country", "location"):
                    # Research notes like "(unverified; ...)" stay in the CSV, not on the site.
                    v = re.sub(r"\s*\([^)]*(unverified|wording|MA |Discogs|likely)[^)]*\)", "", raw, flags=re.I).strip()
                    if key == "country":
                        v = {"USA": "United States", "US": "United States", "UK": "United Kingdom"}.get(v, v)
                    if v and v.lower() != "unverified":
                        b[key] = v
                    else:
                        b.pop(key, None)
                elif key == "status":
                    b[key] = clean_status(raw)
                else:
                    b[key] = raw
            existing[slug] = b
    bands = sorted(existing.values(), key=lambda b: b["name"].lower())
    OUT.write_text("/* Generated by scripts/build_data.py. Edit the CSV and rebuild, or edit by hand. */\n"
                   "window.RER_BANDS = " + json.dumps(bands, ensure_ascii=False, indent=2) + ";\n", encoding="utf-8")
    print("wrote %d bands to %s" % (len(bands), OUT))

if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    main(sys.argv[1])
