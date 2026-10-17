/*
 * Raven Eye Records translation relay (Cloudflare Worker).
 *
 * The Codex translator on the website sends text here; this Worker adds the private
 * Google Cloud Translation key and passes the request on, so the key never appears in
 * the public site. Setup steps: docs/translator-setup.md.
 *
 * Needs one secret, set in the Cloudflare dashboard (Settings > Variables and Secrets):
 *   GOOGLE_API_KEY  a Google Cloud API key restricted to the Cloud Translation API
 */

// Sites allowed to use this relay. Add your own domain here if you get one.
const ALLOWED_ORIGINS = [
  "https://goldydev30.github.io",
  "http://localhost:8766",
];

// The languages the website offers. Google calls Norwegian "no".
const LANGS = new Set(["hy", "be", "da", "nl", "en", "fo", "fi", "fr", "de", "el", "is", "it", "no", "pl", "pt", "ro", "sk", "es", "sv", "tr", "uk"]);
const MAX_WORDS = 250;
const MAX_CHARS = 2500;

function cors(origin) {
  return {
    "Access-Control-Allow-Origin": origin,
    "Access-Control-Allow-Methods": "POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type",
    "Access-Control-Max-Age": "86400",
    "Vary": "Origin",
  };
}

function reply(body, status, origin) {
  return new Response(JSON.stringify(body), {
    status,
    headers: { "Content-Type": "application/json", ...cors(origin) },
  });
}

export default {
  async fetch(request, env) {
    const origin = request.headers.get("Origin") || "";
    if (!ALLOWED_ORIGINS.includes(origin)) return new Response("Forbidden", { status: 403 });
    if (request.method === "OPTIONS") return new Response(null, { status: 204, headers: cors(origin) });
    if (request.method !== "POST") return reply({ error: "Use POST." }, 405, origin);
    if (!env.GOOGLE_API_KEY) return reply({ error: "The translator isn't set up yet." }, 500, origin);

    let input;
    try { input = await request.json(); } catch { return reply({ error: "Bad request." }, 400, origin); }
    const text = String(input.q || "").trim();
    const source = String(input.source || "");
    const target = String(input.target || "");
    if (!text) return reply({ error: "Nothing to translate." }, 400, origin);
    if (!LANGS.has(source) || !LANGS.has(target) || source === target) return reply({ error: "Choose two different languages." }, 400, origin);
    if (text.length > MAX_CHARS || text.split(/\s+/).length > MAX_WORDS) return reply({ error: "Please keep it under 250 words." }, 413, origin);

    const google = await fetch("https://translation.googleapis.com/language/translate/v2?key=" + encodeURIComponent(env.GOOGLE_API_KEY), {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ q: text, source, target, format: "text" }),
    });
    const data = await google.json().catch(() => ({}));
    if (!google.ok) {
      const quota = google.status === 429 || google.status === 403;
      return reply({ error: quota ? "The translator is busy right now. Please try again later." : "The translation failed. Please try again." }, 502, origin);
    }
    const out = data && data.data && data.data.translations && data.data.translations[0];
    return reply({ translation: out ? out.translatedText : "" }, 200, origin);
  },
};
