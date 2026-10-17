/*
 * Raven Eye Records translation relay (Google Cloud Run function, Node.js).
 *
 * The Codex translator on the website sends text here, and this function asks the
 * Cloud Translation API for the translation. It signs in as the function's own service
 * account, so no API key is stored anywhere. Setup steps: docs/translator-setup.md.
 *
 * Entry point: translate
 * The service account needs the "Cloud Translation API User" role.
 */
const functions = require("@google-cloud/functions-framework");

// Sites allowed to use this relay. Add your own domain here if you get one.
const ALLOWED_ORIGINS = [
  "https://goldydev30.github.io",
  "http://localhost:8766",
];

// The languages the website offers. Google calls Norwegian "no".
const LANGS = new Set(["hy", "be", "da", "nl", "en", "fo", "fi", "fr", "de", "el", "is", "it", "no", "pl", "pt", "ro", "sk", "es", "sv", "tr", "uk"]);
const MAX_WORDS = 250;
const MAX_CHARS = 2500;

// A short-lived access token for the function's service account, from the metadata server.
let token = { value: "", expires: 0 };
async function accessToken() {
  if (token.value && Date.now() < token.expires - 60000) return token.value;
  const r = await fetch("http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/token", {
    headers: { "Metadata-Flavor": "Google" },
  });
  if (!r.ok) throw new Error("metadata " + r.status);
  const d = await r.json();
  token = { value: d.access_token, expires: Date.now() + d.expires_in * 1000 };
  return token.value;
}

functions.http("translate", async (req, res) => {
  const origin = req.get("Origin") || "";
  if (!ALLOWED_ORIGINS.includes(origin)) return res.status(403).send("Forbidden");
  res.set({
    "Access-Control-Allow-Origin": origin,
    "Access-Control-Allow-Methods": "POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type",
    "Access-Control-Max-Age": "86400",
    "Vary": "Origin",
  });
  if (req.method === "OPTIONS") return res.status(204).send("");
  if (req.method !== "POST") return res.status(405).json({ error: "Use POST." });

  const body = req.body && typeof req.body === "object" ? req.body : {};
  const text = String(body.q || "").trim();
  const source = String(body.source || "");
  const target = String(body.target || "");
  if (!text) return res.status(400).json({ error: "Nothing to translate." });
  if (!LANGS.has(source) || !LANGS.has(target) || source === target) return res.status(400).json({ error: "Choose two different languages." });
  if (text.length > MAX_CHARS || text.split(/\s+/).length > MAX_WORDS) return res.status(413).json({ error: "Please keep it under 250 words." });

  try {
    const google = await fetch("https://translation.googleapis.com/language/translate/v2", {
      method: "POST",
      headers: { "Content-Type": "application/json", "Authorization": "Bearer " + (await accessToken()) },
      body: JSON.stringify({ q: text, source, target, format: "text" }),
    });
    const data = await google.json().catch(() => ({}));
    if (!google.ok) {
      console.error("Translation API error", google.status, JSON.stringify(data));
      const busy = google.status === 429;
      return res.status(502).json({ error: busy ? "The translator is busy right now. Please try again later." : "The translation failed. Please try again." });
    }
    const out = data.data && data.data.translations && data.data.translations[0];
    return res.json({ translation: out ? out.translatedText : "" });
  } catch (err) {
    console.error("Relay error", err);
    return res.status(502).json({ error: "The translation failed. Please try again." });
  }
});
