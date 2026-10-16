/* Raven Eye Records: shared layout, helpers and page renderers. No build step. */
(function () {
  "use strict";

  var SIGIL =
    '<svg viewBox="0 0 100 100" aria-hidden="true" fill="none" stroke="currentColor">' +
    '<circle cx="50" cy="50" r="46" stroke-width="1.2" opacity=".5"/>' +
    '<circle cx="50" cy="50" r="40" stroke-width=".6" opacity=".35"/>' +
    '<g stroke-width="1" opacity=".55">' +
    '<path d="M50 4v12M50 84v12M4 50h12M84 50h12M17.5 17.5l8.5 8.5M74 74l8.5 8.5M82.5 17.5L74 26M26 74l-8.5 8.5"/></g>' +
    '<path d="M14 50 Q50 16 86 50 Q50 84 14 50Z" stroke-width="2.2"/>' +
    '<circle cx="50" cy="50" r="14" fill="#8c1c1c" stroke="none"/>' +
    '<circle cx="50" cy="50" r="6" fill="#000" stroke="none"/>' +
    '<path d="M43 44 l4 3" stroke="#efe9dc" stroke-width="2" stroke-linecap="round"/>' +
    '</svg>';

  var NAV = [
    ["index.html", "Home"],
    ["roster.html", "Artists"],
    ["lyrics.html", "Lyrics Codex"],
    ["arsenal.html", "Arsenal"],
    ["news.html", "News"],
    ["about.html", "About"],
    ["submit.html", "Demos"]
  ];

  function esc(s) {
    return String(s == null ? "" : s).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }

  function slugify(s) {
    return String(s).normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase()
      .replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "");
  }

  // Deterministic "cover art" so every artist has a distinct tile before real art exists.
  function hash(s) { var h = 2166136261; for (var i = 0; i < s.length; i++) { h ^= s.charCodeAt(i); h = Math.imul(h, 16777619); } return h >>> 0; }
  function artStyle(name) {
    var h = hash(name);
    var hues = [0, 355, 210, 200, 30, 270, 120, 190];
    var hue = hues[h % hues.length];
    var a = (h >> 3) % 360, x = 20 + (h >> 7) % 60, y = 20 + (h >> 11) % 60;
    return "background:" +
      "radial-gradient(circle at " + x + "% " + y + "%, hsla(" + hue + ",45%,28%,.85), transparent 60%)," +
      "linear-gradient(" + a + "deg, hsl(" + hue + ",18%,9%), hsl(" + hue + ",10%,4%))";
  }
  function initial(name) { var m = String(name).match(/[A-Za-z0-9]/); return m ? m[0].toUpperCase() : "?"; }

  function val(v) { return v ? esc(v) : '<span class="pending">Researching</span>'; }

  function bands() {
    return (window.RER_BANDS || []).slice().sort(function (a, b) { return a.name.localeCompare(b.name); });
  }
  function findBand(slug) { return bands().filter(function (b) { return b.slug === slug; })[0]; }
  function bandUrl(b) { return "band.html?b=" + encodeURIComponent(b.slug); }
  function maUrl(b) {
    return b.ma_url || "https://www.metal-archives.com/search?searchString=" + encodeURIComponent(b.name) + "&type=band_name";
  }

  function bandCard(b) {
    var art = b.image ? '<img src="' + esc(b.image) + '" alt="" loading="lazy">' : "<span>" + esc(initial(b.name)) + "</span>";
    return '<a class="band-card" href="' + bandUrl(b) + '">' +
      (b.country ? '<span class="flag">' + esc(b.country) + "</span>" : "") +
      '<div class="art" style="' + artStyle(b.name) + '">' + art + "</div>" +
      '<div class="body"><h3>' + esc(b.name) + '</h3><div class="meta">' +
      (b.genre ? esc(b.genre) : '<span class="pending">Genre being researched</span>') + "</div></div></a>";
  }

  /* ---------- layout ---------- */
  function layout() {
    var here = location.pathname.split("/").pop() || "index.html";
    var top = document.createElement("div");
    top.className = "topbar";
    top.innerHTML = '<div class="wrap"><span>Grassroots black metal &middot; Est. 2026</span>' +
      '<span class="hide-sm"><a href="submit.html">Submit a demo</a> &nbsp;/&nbsp; <a href="lyrics.html">Read the lyrics</a></span></div>';

    var header = document.createElement("header");
    header.className = "site";
    header.innerHTML = '<div class="wrap">' +
      '<a class="brand" href="index.html" aria-label="Raven Eye Records home">' + SIGIL +
      '<span><span class="name">Raven Eye</span><span class="sub">Records</span></span></a>' +
      '<button class="menu-btn" aria-expanded="false" aria-controls="mainnav">Menu</button>' +
      '<nav class="main" id="mainnav" aria-label="Main"><ul>' +
      NAV.map(function (n) {
        return '<li><a href="' + n[0] + '"' + (n[0] === here ? ' aria-current="page"' : "") + ">" + n[1] + "</a></li>";
      }).join("") + "</ul></nav></div>";

    var footer = document.createElement("footer");
    footer.className = "site";
    footer.innerHTML = '<div class="wrap"><div class="cols">' +
      '<div><a class="brand" href="index.html">' + SIGIL + '<span><span class="name">Raven Eye</span><span class="sub">Records</span></span></a>' +
      '<p style="margin-top:1rem">An independent label and lyrics codex for black, pagan, folk and melodic extreme metal. The words matter here.</p>' +
      '<form class="newsletter" onsubmit="event.preventDefault();this.innerHTML=\'<span>Thank you. The ravens will find you.</span>\'">' +
      '<label class="sr-only" for="nl">Email</label><input id="nl" type="email" placeholder="Your email" required><button class="btn blood" type="submit">Join</button></form></div>' +
      '<div><h4>Label</h4><ul><li><a href="about.html">About</a></li><li><a href="news.html">News</a></li><li><a href="submit.html">Demo submissions</a></li></ul></div>' +
      '<div><h4>Explore</h4><ul><li><a href="roster.html">Artists</a></li><li><a href="lyrics.html">Lyrics Codex</a></li><li><a href="lyrics.html#themes">Lyrical themes</a></li></ul></div>' +
      '<div><h4>Elsewhere</h4><ul><li><a href="https://www.metal-archives.com" rel="noopener">Encyclopaedia Metallum</a></li><li><a href="https://bandcamp.com/tag/black-metal" rel="noopener">Bandcamp</a></li></ul></div>' +
      '</div><div class="fine"><span>&copy; ' + new Date().getFullYear() + ' Raven Eye Records</span>' +
      '<span>Band names and marks belong to their owners. Lyrics are quoted only with permission.</span></div></div>';

    document.body.insertBefore(header, document.body.firstChild);
    document.body.insertBefore(top, header);
    document.body.appendChild(footer);

    var btn = header.querySelector(".menu-btn"), nav = header.querySelector("nav");
    btn.addEventListener("click", function () {
      var open = nav.classList.toggle("open");
      btn.setAttribute("aria-expanded", open ? "true" : "false");
    });
  }

  /* ---------- pages ---------- */
  function renderHome() {
    var el = document.getElementById("featured");
    if (el) {
      var list = bands();
      var featured = list.filter(function (b) { return b.featured; });
      if (featured.length < 10) {
        // Stable daily rotation through the roster.
        var day = Math.floor(Date.now() / 864e5);
        var rest = list.filter(function (b) { return !b.featured; });
        for (var i = 0; featured.length < 10 && i < rest.length; i++) featured.push(rest[(day * 7 + i * 11) % rest.length]);
        featured = featured.filter(function (b, i, a) { return a.indexOf(b) === i; });
      }
      el.innerHTML = featured.slice(0, 10).map(bandCard).join("");
    }
    var stat = document.getElementById("roster-count");
    if (stat) stat.textContent = bands().length;
    var countries = document.getElementById("country-count");
    if (countries) countries.textContent = unique("country").length || "Many";
    renderNews("latest-news", 3);
  }

  // Metal Archives genres read like "Atmospheric Black/Doom Metal", so the genre
  // filter works on style keywords rather than raw strings.
  var STYLES = ["Atmospheric", "Avant-garde", "Black", "Blackened", "Celtic", "Death", "Doom", "Epic", "Folk", "Gothic",
    "Heavy", "Melodic", "Pagan", "Post", "Power", "Progressive", "Symphonic", "Thrash", "Viking"];
  function values(b, field) {
    var raw = String(b[field] || "");
    if (!raw) return [];
    if (field === "genre" && b.families && b.families.length) return b.families;
    if (field === "genre") return STYLES.filter(function (s) { return new RegExp("\\b" + s + "\\b", "i").test(raw); });
    if (field === "label") return raw.split(/\s*;\s*/);
    return raw.split(/\s*[\/,;]\s*/);
  }
  function unique(field) {
    var seen = {};
    bands().forEach(function (b) { values(b, field).forEach(function (v) { if (v) seen[v] = 1; }); });
    return Object.keys(seen).sort();
  }

  function renderRoster() {
    var grid = document.getElementById("roster");
    if (!grid) return;
    var q = document.getElementById("q"), c = document.getElementById("country"),
        g = document.getElementById("genre"), l = document.getElementById("label"),
        count = document.getElementById("count");
    function fill(sel, field, label) {
      sel.innerHTML = '<option value="">All ' + label + "</option>" +
        unique(field).map(function (v) { return '<option value="' + esc(v) + '">' + esc(v) + "</option>"; }).join("");
    }
    fill(c, "country", "countries");
    fill(g, "genre", "genres");
    fill(l, "label", "labels");

    var params = new URLSearchParams(location.search);
    if (params.get("country")) c.value = params.get("country");
    if (params.get("genre")) g.value = params.get("genre");
    if (params.get("q")) q.value = params.get("q");

    function has(field, v) { return function (b) { return !v || values(b, field).indexOf(v) > -1; }; }
    function draw() {
      var term = q.value.trim().toLowerCase();
      var list = bands()
        .filter(function (b) { return !term || [b.name, b.genre, b.country, b.label, (b.themes || []).join(" ")].join(" ").toLowerCase().indexOf(term) > -1; })
        .filter(has("country", c.value)).filter(has("genre", g.value)).filter(has("label", l.value));
      count.textContent = list.length + " of " + bands().length + " artists";
      grid.innerHTML = list.length ? list.map(bandCard).join("") : '<p class="muted">No artists match. The void stares back.</p>';
    }
    [q, c, g, l].forEach(function (x) { x.addEventListener("input", draw); });
    draw();
  }

  function renderBand() {
    var root = document.getElementById("band");
    if (!root) return;
    var slug = new URLSearchParams(location.search).get("b");
    var b = slug && findBand(slug);
    if (!b) {
      root.innerHTML = '<section class="block"><div class="wrap"><h1>Not found</h1><p>That artist is not in the roster. <a href="roster.html">Browse all artists</a>.</p></div></section>';
      return;
    }
    document.title = b.name + " | Raven Eye Records";
    var themes = (b.themes || []);
    var art = b.image ? '<img src="' + esc(b.image) + '" alt="' + esc(b.name) + '">' : "<span>" + esc(initial(b.name)) + "</span>";
    var codex = (window.RER_CODEX || []).filter(function (e) { return e.band === b.slug; });
    var related = bands().filter(function (x) {
      return x !== b && ((b.country && x.country === b.country) || themes.some(function (t) { return (x.themes || []).indexOf(t) > -1; }));
    }).slice(0, 4);

    root.innerHTML =
      '<section class="band-hero"><div class="wrap">' +
      '<div class="art" style="' + artStyle(b.name) + '">' + art + "</div>" +
      '<div><span class="eyebrow">Artist</span><h1>' + esc(b.name) + "</h1>" +
      (b.summary ? "<p>" + esc(b.summary) + "</p>" : "") +
      '<dl class="facts">' +
      "<div><dt>Country</dt><dd>" + val(b.country) + "</dd></div>" +
      "<div><dt>Genre</dt><dd>" + val(b.genre) + "</dd></div>" +
      (b.families && b.families.length ? "<div><dt>Family</dt><dd>" + b.families.map(function (f) { return '<a href="roster.html?genre=' + encodeURIComponent(f) + '">' + esc(f) + "</a>"; }).join(", ") + "</dd></div>" : "") +
      "<div><dt>Current label</dt><dd>" + val(b.label) + "</dd></div>" +
      (b.formed ? "<div><dt>Formed</dt><dd>" + esc(b.formed) + "</dd></div>" : "") +
      (b.status ? "<div><dt>Status</dt><dd>" + esc(b.status) + "</dd></div>" : "") +
      "</dl>" +
      (b.provisional ? '<p class="pending">Several bands share this name; we are still confirming this is the right one.</p>' : "") +
      '<div class="btn-row"><a class="btn blood" href="' + esc(maUrl(b)) + '" target="_blank" rel="noopener">Encyclopaedia Metallum</a>' +
      (b.bandcamp ? '<a class="btn" href="' + esc(b.bandcamp) + '" target="_blank" rel="noopener">Bandcamp</a>' : "") +
      (b.website ? '<a class="btn" href="' + esc(b.website) + '" target="_blank" rel="noopener">Official site</a>' : "") +
      "</div></div></div></section>" +

      '<section class="block alt"><div class="wrap"><div class="section-head"><h2>Lyrical themes</h2><a class="more" href="lyrics.html#themes">All themes</a></div>' +
      (themes.length
        ? themes.map(function (t) { return '<a class="tag blood" href="lyrics.html?theme=' + encodeURIComponent(t) + '#themes">' + esc(t) + "</a>"; }).join("")
        : '<p class="pending">Lyrical themes are being catalogued.</p>') +
      (codex.length ? '<hr class="rule">' + codex.map(codexEntry).join("") :
        '<p class="muted" style="margin-top:1rem">Full lyrics for this artist are archived on <a href="' + esc(maUrl(b)) +
        '" target="_blank" rel="noopener">Encyclopaedia Metallum</a>. Raven Eye publishes lyric excerpts and commentary here only with the band\'s permission.</p>') +
      "</div></section>" +

      arsenalSection(b) +

      (related.length ? '<section class="block"><div class="wrap"><div class="section-head"><h2>Kindred spirits</h2><a class="more" href="roster.html">Full roster</a></div>' +
        '<div class="grid bands">' + related.map(bandCard).join("") + "</div></div></section>" : "");
    if (location.hash) { var t = document.getElementById(location.hash.slice(1)); if (t) t.scrollIntoView(); }
  }

  /* ---------- gear ---------- */
  var REPO = "https://github.com/goldydev30/raven-eye-records";
  var REL = {
    endorsement: ["Endorsed", "blood"],
    signature_model: ["Signature model", "blood"],
    seen_using: ["Seen using", ""],
    fan_submitted: ["Fan submitted", ""]
  };
  function gearFor(b) { return (window.RER_GEAR || {})[b.slug] || []; }
  function submitGearUrl(b) {
    return REPO + "/issues/new?template=gear-submission.yml" + (b ? "&title=" + encodeURIComponent("[Gear] " + b.name) + "&band=" + encodeURIComponent(b.name) : "");
  }
  function gearItem(g) {
    var rel = REL[g.relationship] || REL.seen_using;
    return '<li class="gear-item"><span class="gear-cat">' + esc(g.category) + "</span>" +
      '<span class="gear-name"><strong>' + esc(g.brand) + "</strong> " + esc(g.model) + "</span>" +
      '<span class="gear-meta"><span class="tag ' + rel[1] + '">' + rel[0] + "</span>" +
      (g.confidence === "low" ? '<span class="tag">Unconfirmed</span>' : "") +
      (g.source ? '<a href="' + esc(g.source) + '" target="_blank" rel="noopener">Source</a>' : "") + "</span></li>";
  }
  function arsenalSection(b) {
    var gear = gearFor(b);
    var byMember = {};
    gear.forEach(function (g) {
      var k = (g.member || "Band") + (g.role ? " \u00b7 " + g.role : "");
      (byMember[k] = byMember[k] || []).push(g);
    });
    return '<section class="block" id="gear"><div class="wrap"><div class="section-head"><div><span class="eyebrow">A musician\'s armour</span><h2>The Arsenal</h2></div>' +
      '<a class="more" href="' + submitGearUrl(b) + '" target="_blank" rel="noopener">Submit gear</a></div>' +
      (gear.length
        ? '<div class="grid three">' + Object.keys(byMember).map(function (m) {
            return '<div class="panel"><h3>' + esc(m) + '</h3><ul class="gear-list">' + byMember[m].map(gearItem).join("") + "</ul></div>";
          }).join("") + "</div>"
        : '<p class="muted">No rig information catalogued yet. Seen them live or in a playthrough? <a href="' + submitGearUrl(b) + '" target="_blank" rel="noopener">Tell us what they play</a>.</p>') +
      "</div></section>";
  }
  function renderArsenal() {
    var el = document.getElementById("arsenal");
    if (!el) return;
    var withGear = bands().filter(function (b) { return gearFor(b).length; });
    var brands = {};
    withGear.forEach(function (b) { gearFor(b).forEach(function (g) { if (g.brand && !/^unknown$/i.test(g.brand)) (brands[g.brand] = brands[g.brand] || {})[b.slug] = b; }); });
    var top = Object.keys(brands).sort(function (a, b) { return Object.keys(brands[b]).length - Object.keys(brands[a]).length || a.localeCompare(b); });
    el.innerHTML =
      '<div class="section-head"><h2>Armouries by band</h2><span class="count">' + withGear.length + " bands catalogued</span></div>" +
      '<div class="grid bands">' + withGear.map(function (b) {
        var g = gearFor(b), endorsed = g.filter(function (x) { return x.relationship === "endorsement" || x.relationship === "signature_model"; });
        return '<a class="band-card" href="' + bandUrl(b) + '#gear"><div class="art" style="' + artStyle(b.name) + '"><span>' + esc(initial(b.name)) + "</span></div>" +
          '<div class="body"><h3>' + esc(b.name) + '</h3><div class="meta">' + g.length + (g.length === 1 ? " piece" : " pieces") + (endorsed.length ? " &middot; " + endorsed.length + " endorsed" : "") + "</div></div></a>";
      }).join("") + "</div>" +
      '<hr class="rule"><h2>Forges</h2><p class="muted">The makers behind the roster\'s rigs.</p>' +
      top.map(function (br) {
        var bs = Object.keys(brands[br]).map(function (k) { return brands[br][k]; });
        return '<span class="tag" title="' + esc(bs.map(function (x) { return x.name; }).join(", ")) + '">' + esc(br) + " &middot; " + bs.length + "</span>";
      }).join("");
    document.querySelectorAll("[data-submit-gear]").forEach(function (a) { a.href = submitGearUrl(); });
  }

  function codexEntry(e) {
    var b = findBand(e.band);
    return '<article class="codex-entry"><span class="eyebrow">' + esc(b ? b.name : e.artist || "") + (e.album ? " &middot; " + esc(e.album) : "") + "</span>" +
      "<h3>" + esc(e.title) + "</h3>" +
      (e.excerpt ? '<div class="verse">' + esc(e.excerpt) + "</div>" : "") +
      (e.commentary ? "<p>" + esc(e.commentary) + "</p>" : "") +
      (e.source ? '<p class="muted" style="font-size:.85rem">' + esc(e.source) + "</p>" : "") + "</article>";
  }

  function renderLyrics() {
    var themesEl = document.getElementById("themes-grid");
    if (themesEl) {
      var map = {};
      bands().forEach(function (b) { (b.themes || []).forEach(function (t) { (map[t] = map[t] || []).push(b); }); });
      var keys = Object.keys(map).sort(function (a, b) { return map[b].length - map[a].length || a.localeCompare(b); });
      var want = new URLSearchParams(location.search).get("theme");
      var common = keys.filter(function (k) { return map[k].length > 1; });
      var bar = document.getElementById("theme-filter");
      function draw(active) {
        if (bar) bar.innerHTML = '<button class="tag" aria-pressed="' + (!active) + '" data-t="">All</button>' +
          common.map(function (k) { return '<button class="tag" aria-pressed="' + (k === active) + '" data-t="' + esc(k) + '">' + esc(k) + "</button>"; }).join("");
        var shown = active ? [active] : common;
        var rare = active ? [] : keys.filter(function (k) { return map[k].length < 2; });
        themesEl.innerHTML = (shown.length ? shown.map(function (k) {
          return '<div class="theme-card"><h3>' + esc(k) + "<small>" + map[k].length + (map[k].length === 1 ? " artist" : " artists") + "</small></h3><ul>" +
            map[k].map(function (b) { return '<li><a href="' + bandUrl(b) + '">' + esc(b.name) + "</a></li>"; }).join("") + "</ul></div>";
        }).join("") : '<p class="pending">Themes appear here as each artist\'s lyrical themes are catalogued.</p>') +
          (rare.length ? '<div class="theme-card" style="grid-column:1/-1"><h3>Also sung of</h3><ul>' +
            rare.sort(function (a, b) { return a.localeCompare(b); }).map(function (k) {
              return '<li><a href="' + bandUrl(map[k][0]) + '">' + esc(k) + '</a> <span class="muted">(' + esc(map[k][0].name) + ")</span></li>";
            }).join("") + "</ul></div>" : "");
      }
      if (bar) bar.addEventListener("click", function (ev) {
        var t = ev.target.closest("button"); if (!t) return;
        draw(t.getAttribute("data-t") || null);
      });
      draw(want && map[want] ? want : null);
    }
    var codexEl = document.getElementById("codex");
    if (codexEl) {
      var entries = window.RER_CODEX || [];
      codexEl.innerHTML = entries.length ? entries.map(codexEntry).join("") : '<p class="pending">The first codex entries are being prepared.</p>';
    }
  }

  function renderNews(id, limit) {
    var el = document.getElementById(id);
    if (!el) return;
    var items = (window.RER_NEWS || []).slice(0, limit || 99);
    el.innerHTML = items.map(function (n) {
      return '<article class="news-card"><div class="art" style="' + artStyle(n.title) + '"><span>' + esc(initial(n.title)) + "</span></div>" +
        '<div class="body"><time datetime="' + esc(n.date) + '">' + esc(new Date(n.date + "T00:00:00").toLocaleDateString("en-US", { year: "numeric", month: "long", day: "numeric" })) + "</time>" +
        "<h3>" + (n.link ? '<a href="' + esc(n.link) + '">' + esc(n.title) + "</a>" : esc(n.title)) + "</h3><p>" + esc(n.body) + "</p></div></article>";
    }).join("");
  }

  document.addEventListener("DOMContentLoaded", function () {
    layout();
    renderHome();
    renderRoster();
    renderBand();
    renderLyrics();
    renderNews("news-list");
    renderArsenal();
  });

  window.RER = { slugify: slugify, esc: esc };
})();
