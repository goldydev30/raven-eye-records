/* Raven Eye Records: shared layout, helpers and page renderers. No build step. */
(function () {
  "use strict";

  var NAV = [
    ["roster.html", "Artists"],
    ["lyrics.html", "Codex"],
    ["armory.html", "Armory"],
    ["news.html", "News"],
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
    var hues = [0, 356, 352, 4, 10, 348, 0, 20];
    var hue = hues[h % hues.length];
    var a = (h >> 3) % 360, x = 20 + (h >> 7) % 60, y = 20 + (h >> 11) % 60;
    return "background:" +
      "radial-gradient(circle at " + x + "% " + y + "%, hsla(" + hue + ",70%,20%,.8), transparent 60%)," +
      "linear-gradient(" + a + "deg, hsl(" + hue + ",25%,6%), hsl(" + hue + ",15%,2%))";
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

  /* ---------- cover art ----------
     Each band tile shows a faint album cover behind its initial. A cover comes from the
     band's own "image" field when set; otherwise the visitor's browser looks one up on
     Deezer (then iTunes) by exact artist name and caches it for 30 days. Bands whose
     identity is still provisional skip the lookup so a namesake's cover never shows. */
  function artBox(b) {
    return '<div class="art" data-band="' + esc(b.slug) + '" style="' + artStyle(b.name) + '"><span>' + esc(initial(b.name)) + "</span></div>";
  }
  var ART_TTL = 30 * 864e5, artMem = {}, artWaiting = {}, artQueue = [], artActive = 0, jsonpN = 0;
  function norm(s) { return String(s).normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase().replace(/[^a-z0-9]/g, ""); }
  function cacheGet(slug) {
    if (slug in artMem) return artMem[slug];
    try { var c = JSON.parse(localStorage.getItem("rer-art:" + slug)); if (c && Date.now() - c.t < ART_TTL) return (artMem[slug] = c.u); } catch (e) {}
    return undefined;
  }
  function cacheSet(slug, url) {
    artMem[slug] = url;
    try { localStorage.setItem("rer-art:" + slug, JSON.stringify({ u: url, t: Date.now() })); } catch (e) {}
  }
  function jsonp(url, done) {
    var name = "rerJsonp" + (++jsonpN), el = document.createElement("script"), fin = false;
    function end(data) { if (fin) return; fin = true; delete window[name]; el.remove(); done(data); }
    window[name] = end;
    el.onerror = function () { end(null); };
    setTimeout(function () { end(null); }, 8000);
    el.src = url + (url.indexOf("?") > -1 ? "&" : "?") + "callback=" + name;
    document.head.appendChild(el);
  }
  function lookupCover(b, done) {
    var want = norm(b.name);
    jsonp("https://api.deezer.com/search/album?output=jsonp&q=" + encodeURIComponent('artist:"' + b.name + '"'), function (r) {
      var hit = r && r.data && r.data.filter(function (a) { return a.artist && norm(a.artist.name) === want && a.cover_xl; })[0];
      if (hit) return done(hit.cover_xl);
      jsonp("https://itunes.apple.com/search?media=music&entity=album&limit=15&term=" + encodeURIComponent(b.name), function (r2) {
        var hit2 = r2 && r2.results && r2.results.filter(function (a) { return norm(a.artistName) === want && a.artworkUrl100; })[0];
        done(hit2 ? hit2.artworkUrl100.replace("100x100bb", "600x600bb") : "");
      });
    });
  }
  function pumpArt() {
    while (artActive < 2 && artQueue.length) {
      (function (b) {
        artActive++;
        lookupCover(b, function (url) {
          artActive--;
          cacheSet(b.slug, url);
          (artWaiting[b.slug] || []).forEach(function (el) { showCover(el, url); });
          delete artWaiting[b.slug];
          pumpArt();
        });
      })(artQueue.shift());
    }
  }
  function showCover(el, url) {
    if (!url || el.querySelector(".cover")) return;
    var img = new Image();
    img.className = "cover"; img.alt = ""; img.referrerPolicy = "no-referrer";
    img.onload = function () { img.classList.add("on"); el.classList.add("has-cover"); };
    img.src = url;
    el.insertBefore(img, el.firstChild);
  }
  function loadArt(el) {
    var b = findBand(el.getAttribute("data-band"));
    if (!b) return;
    if (b.image) return showCover(el, b.image);
    if (b.provisional) return;
    var c = cacheGet(b.slug);
    if (c !== undefined) return showCover(el, c);
    if (artWaiting[b.slug]) return artWaiting[b.slug].push(el);
    artWaiting[b.slug] = [el];
    artQueue.push(b);
    pumpArt();
  }
  var artObserver = "IntersectionObserver" in window ? new IntersectionObserver(function (entries) {
    entries.forEach(function (e) { if (e.isIntersecting) { artObserver.unobserve(e.target); loadArt(e.target); } });
  }, { rootMargin: "200px" }) : null;
  function hydrateArt() {
    document.querySelectorAll(".art[data-band]:not([data-art])").forEach(function (el) {
      el.setAttribute("data-art", "1");
      if (artObserver) artObserver.observe(el); else loadArt(el);
    });
  }

  function bandCard(b) {
    return '<a class="band-card" href="' + bandUrl(b) + '">' +
      (b.country ? '<span class="flag">' + esc(b.country) + "</span>" : "") +
      artBox(b) +
      '<div class="body"><h3>' + esc(b.name) + '</h3><div class="meta">' +
      (b.genre ? esc(b.genre) : '<span class="pending">Genre being researched</span>') + "</div></div></a>";
  }

  /* ---------- layout ---------- */
  function layout() {
    var here = location.pathname.split("/").pop() || "index.html";
    var top = document.createElement("div");
    top.className = "topbar";
    var cur = function (f) { return f === here ? ' aria-current="page"' : ""; };
    top.innerHTML = '<div class="wrap"><span>Established 2026</span>' +
      '<span><a href="index.html"' + cur("index.html") + '>Home</a> &nbsp;/&nbsp; <a href="about.html"' + cur("about.html") + ">About</a></span></div>";

    var header = document.createElement("header");
    header.className = "site";
    header.innerHTML = '<div class="wrap">' +
      '<a class="brand" href="index.html"><span class="name">Raven Eye Records</span></a>' +
      '<button class="menu-btn" aria-expanded="false" aria-controls="mainnav">Menu</button>' +
      '<nav class="main" id="mainnav" aria-label="Main"><ul>' +
      NAV.map(function (n) {
        return '<li><a href="' + n[0] + '"' + (n[0] === here ? ' aria-current="page"' : "") + ">" + n[1] + "</a></li>";
      }).join("") + "</ul></nav></div>";

    var footer = document.createElement("footer");
    footer.className = "site";
    footer.innerHTML = '<div class="wrap"><div class="cols">' +
      '<div><a class="brand" href="index.html"><span class="name">Raven Eye Records</span></a>' +
      '<p style="margin-top:1rem">An independent label and lyrics codex for black, pagan, folk and melodic extreme metal. The words matter here.</p>' +
      '<form class="newsletter" onsubmit="event.preventDefault();this.innerHTML=\'<span>Thank you. The ravens will find you.</span>\'">' +
      '<label class="sr-only" for="nl">Email</label><input id="nl" type="email" placeholder="Your email" required><button class="btn blood" type="submit">Join</button></form></div>' +
      '<div><h4>Label</h4><ul><li><a href="about.html">About</a></li><li><a href="news.html">News</a></li><li><a href="submit.html">Demo submissions</a></li></ul></div>' +
      '<div><h4>Explore</h4><ul><li><a href="roster.html">Artists</a></li><li><a href="lyrics.html">The Codex</a></li><li><a href="lyrics.html#themes">Lyrical themes</a></li></ul></div>' +
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

  /* ---------- the logo ----------
     Inline copies of the raven's eye (ids namespaced per copy). It blinks when hovered or
     focused; the lids move through CSS in style.css. */
  var logoN = 0;
  function mountLogos() {
    document.querySelectorAll("[data-logo]:not([data-mounted])").forEach(function (slot) {
      if (!window.RER_LOGO) return;
      var n = ++logoN;
      slot.innerHTML = window.RER_LOGO.replace(/id="rer-/g, 'id="rer' + n + "-").replace(/url\(#rer-/g, "url(#rer" + n + "-");
      slot.setAttribute("data-mounted", "1");
      var eye = slot.querySelector(".rer-eye");
      var host = slot.closest("a") || slot;
      host.addEventListener("mouseenter", function () { blink(eye); });
      host.addEventListener("focus", function () { blink(eye); });
      host.addEventListener("touchstart", function () { blink(eye); }, { passive: true });
    });
  }
  function blink(eye) {
    if (eye.classList.contains("closed")) return;
    eye.classList.add("closed");
    setTimeout(function () { eye.classList.remove("closed"); }, 260);
  }

  /* ---------- pages ---------- */
  // Featured on the homepage, in this order. Searching swaps in matches from the whole roster, A to Z.
  var FEATURED = ["insomnium", "amorphis", "amon-amarth", "darconigan", "varmia", "walg", "soilwork", "wormlight", "kalmah", "flamen"];
  function renderHome() {
    var el = document.getElementById("featured");
    if (el) {
      var featured = FEATURED.map(findBand).filter(Boolean);
      var q = document.getElementById("fq"), empty = document.getElementById("featured-empty");
      var draw = function () {
        var term = q ? q.value.trim().toLowerCase() : "";
        var list = !term ? featured : bands().slice()
          .filter(function (b) { return [b.name, b.genre, b.country, b.label, (b.themes || []).join(" ")].join(" ").toLowerCase().indexOf(term) > -1; })
          .sort(function (x, y) { return x.name.localeCompare(y.name); });
        el.innerHTML = list.map(bandCard).join("");
        if (empty) empty.hidden = list.length > 0;
      };
      if (q) q.addEventListener("input", draw);
      draw();
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
    var codex = (window.RER_CODEX || []).filter(function (e) { return e.band === b.slug; });
    var related = bands().filter(function (x) {
      return x !== b && ((b.country && x.country === b.country) || themes.some(function (t) { return (x.themes || []).indexOf(t) > -1; }));
    }).slice(0, 4);

    root.innerHTML =
      '<section class="band-hero"><div class="wrap">' +
      artBox(b) +
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

      armorySection(b) +

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
  function armorySection(b) {
    var gear = gearFor(b);
    var byMember = {};
    gear.forEach(function (g) {
      var k = (g.member || "Band") + (g.role ? " \u00b7 " + g.role : "");
      (byMember[k] = byMember[k] || []).push(g);
    });
    return '<section class="block" id="gear"><div class="wrap"><div class="section-head"><div><span class="eyebrow">A musician\'s armor</span><h2>The Armory</h2></div>' +
      '<a class="more" href="' + submitGearUrl(b) + '" target="_blank" rel="noopener">Submit gear</a></div>' +
      (gear.length
        ? '<div class="grid three">' + Object.keys(byMember).map(function (m) {
            return '<div class="panel"><h3>' + esc(m) + '</h3><ul class="gear-list">' + byMember[m].map(gearItem).join("") + "</ul></div>";
          }).join("") + "</div>"
        : '<p class="muted">No rig information catalogued yet. Seen them live or in a playthrough? <a href="' + submitGearUrl(b) + '" target="_blank" rel="noopener">Tell us what they play</a>.</p>') +
      "</div></section>";
  }
  function renderArmory() {
    var el = document.getElementById("armory");
    if (!el) return;
    var withGear = bands().filter(function (b) { return gearFor(b).length; });
    var brands = {};
    withGear.forEach(function (b) { gearFor(b).forEach(function (g) { if (g.brand && !/^unknown$/i.test(g.brand)) (brands[g.brand] = brands[g.brand] || {})[b.slug] = b; }); });
    var top = Object.keys(brands).sort(function (a, b) { return Object.keys(brands[b]).length - Object.keys(brands[a]).length || a.localeCompare(b); });
    el.innerHTML =
      '<div class="section-head"><h2>Armories by band</h2><span class="count">' + withGear.length + " bands catalogued</span></div>" +
      '<div class="grid bands">' + withGear.map(function (b) {
        var g = gearFor(b), endorsed = g.filter(function (x) { return x.relationship === "endorsement" || x.relationship === "signature_model"; });
        return '<a class="band-card" href="' + bandUrl(b) + '#gear">' + artBox(b) +
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

  /* ---------- Codex translator ----------
     Languages spoken in our bands' countries. Uses the free MyMemory API, which takes
     about 500 bytes per request, so longer text is sent sentence by sentence. */
  var TR_LANGS = [
    ["hy", "Armenian", "Armenia"], ["be", "Belarusian", "Belarus"], ["da", "Danish", "Denmark"],
    ["nl", "Dutch", "Netherlands, Belgium"], ["en", "English", "USA, UK, Canada, Australia, New Zealand"],
    ["fo", "Faroese", "Faroe Islands"], ["fi", "Finnish", "Finland"], ["fr", "French", "France, Canada, Belgium, Switzerland"],
    ["de", "German", "Germany, Austria, Switzerland"], ["el", "Greek", "Greece"], ["is", "Icelandic", "Iceland"],
    ["it", "Italian", "Italy, Switzerland"], ["nb", "Norwegian", "Norway"], ["pl", "Polish", "Poland"],
    ["pt", "Portuguese", "Portugal"], ["ro", "Romanian", "Romania"], ["sk", "Slovak", "Slovakia"],
    ["es", "Spanish", "Spain, Ecuador"], ["sv", "Swedish", "Sweden"], ["tr", "Turkish", "Turkey"],
    ["uk", "Ukrainian", "Ukraine"]
  ];
  var TR_MAX_WORDS = 250;
  function wordCount(s) { var m = s.trim().match(/\S+/g); return m ? m.length : 0; }
  function utf8Len(s) { return unescape(encodeURIComponent(s)).length; }
  function trChunks(text) {
    // Split into pieces under ~450 bytes, keeping sentences and lines together where possible.
    var parts = text.match(/[^.!?\n]+[.!?]*\s*|\n+/g) || [text], out = [], cur = "";
    parts.forEach(function (p) {
      while (utf8Len(p) > 450) {          // a very long sentence: cut on a space
        var cut = p.lastIndexOf(" ", 300); if (cut < 1) cut = 300;
        if (cur) { out.push(cur); cur = ""; }
        out.push(p.slice(0, cut)); p = p.slice(cut);
      }
      if (utf8Len(cur + p) > 450) { out.push(cur); cur = p; } else cur += p;
    });
    if (cur) out.push(cur);
    return out;
  }
  function decodeEntities(s) { var t = document.createElement("textarea"); t.innerHTML = s; return t.value; }
  function translatePiece(piece, from, to) {
    if (!piece.trim()) return Promise.resolve(piece);
    var lead = piece.match(/^\s*/)[0], trail = piece.match(/\s*$/)[0];
    var url = "https://api.mymemory.translated.net/get?q=" + encodeURIComponent(piece.trim()) + "&langpair=" + from + "|" + to;
    return fetch(url).then(function (r) { return r.json(); }).then(function (d) {
      if (!d || String(d.responseStatus) !== "200" || !d.responseData) {
        var why = d && d.responseDetails ? String(d.responseDetails) : "";
        throw new Error(/QUOTA|LIMIT/i.test(why) || String(d && d.responseStatus) === "429"
          ? "The free translation limit for today has been reached. Please try again tomorrow."
          : "That language pair couldn't be translated. Try another pair.");
      }
      return lead + decodeEntities(d.responseData.translatedText) + trail;
    });
  }
  function renderTranslator() {
    var form = document.getElementById("tr-form");
    if (!form) return;
    var from = document.getElementById("tr-from"), to = document.getElementById("tr-to"),
        input = document.getElementById("tr-in"), count = document.getElementById("tr-count"),
        out = document.getElementById("tr-out"), status = document.getElementById("tr-status"),
        go = document.getElementById("tr-go"), copy = document.getElementById("tr-copy");
    var opts = TR_LANGS.map(function (l) { return '<option value="' + l[0] + '" title="' + esc(l[2]) + '">' + esc(l[1]) + "</option>"; }).join("");
    from.innerHTML = opts; to.innerHTML = opts;
    from.value = "en"; to.value = "fi";
    var last = "";
    function update() {
      var n = wordCount(input.value);
      if (n > TR_MAX_WORDS) {            // trim back to the limit, keeping the original spacing
        var re = /\S+/g, m, i = 0, end = 0;
        while ((m = re.exec(input.value)) && i < TR_MAX_WORDS) { end = m.index + m[0].length; i++; }
        input.value = input.value.slice(0, end); n = TR_MAX_WORDS;
      }
      count.textContent = n + " / " + TR_MAX_WORDS + " words";
      count.classList.toggle("full", n >= TR_MAX_WORDS);
      go.disabled = !n;
    }
    function show(text, isError) {
      out.innerHTML = "";
      var p = document.createElement(isError ? "p" : "div");
      p.className = isError ? "tr-error" : "";
      p.textContent = text;
      out.appendChild(p);
      last = isError ? "" : text;
      copy.disabled = !last;
    }
    input.addEventListener("input", update);
    input.addEventListener("keydown", function (e) { if ((e.ctrlKey || e.metaKey) && e.key === "Enter") { e.preventDefault(); form.requestSubmit ? form.requestSubmit() : form.dispatchEvent(new Event("submit")); } });
    document.getElementById("tr-swap").addEventListener("click", function () {
      var f = from.value; from.value = to.value; to.value = f;
      if (last) { input.value = last; update(); show("", false); out.innerHTML = '<span class="muted">Press Translate to translate it back.</span>'; }
    });
    copy.addEventListener("click", function () {
      if (!last) return;
      var done = function () { status.textContent = "Copied"; setTimeout(function () { status.textContent = ""; }, 1600); };
      if (navigator.clipboard) navigator.clipboard.writeText(last).then(done, function () {});
    });
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      var text = input.value.trim();
      if (!text) return;
      if (from.value === to.value) return show("Choose two different languages.", true);
      go.disabled = true; status.textContent = "Translating...";
      var pieces = trChunks(input.value.replace(/^\s+|\s+$/g, ""));
      Promise.all(pieces.map(function (p) { return translatePiece(p, from.value, to.value); }))
        .then(function (res) { show(res.join(""), false); status.textContent = ""; })
        .catch(function (err) {
          show(err && err.message && !/fetch|network|json/i.test(err.message) ? err.message : "The translator couldn't be reached. Check your connection and try again.", true);
          status.textContent = "";
        })
        .then(function () { go.disabled = !wordCount(input.value); });
    });
    update();
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
    mountLogos();
    renderHome();
    renderRoster();
    renderBand();
    renderLyrics();
    renderTranslator();
    renderNews("news-list");
    renderArmory();
    hydrateArt();
    new MutationObserver(hydrateArt).observe(document.body, { childList: true, subtree: true });
  });

  window.RER = { slugify: slugify, esc: esc };
})();
