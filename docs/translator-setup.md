# Setting up Google translation for the Codex

The Codex translator currently uses MyMemory, a free service with a small daily limit. These steps switch it to Google Cloud Translation. Your private Google key is kept in a Cloudflare Worker, a tiny free relay that sits between the website and Google, so the key never appears in the public site.

It takes about 20 minutes. You'll end up with one web address to send me, and **you never need to send me the key itself**.

## Part 1: Google Cloud (get a translation key)

1. Go to [console.cloud.google.com](https://console.cloud.google.com) and sign in with a Google account.
2. Create a project. Click the project picker at the top, choose **New project**, name it `raven-eye-records`, and click **Create**. Make sure it's selected afterwards.
3. Turn on billing. Open the menu, then **Billing**, and link a billing account. Google requires a card even for the free tier. The first 500,000 characters each month are free, which is about 1,000 full 250-word translations.
4. Add a budget alert so there are no surprises. Go to **Billing**, then **Budgets & alerts**, then **Create budget**. Set the amount to $5 and keep the email alerts on.
5. Turn on the translation service. Go to **APIs & Services**, then **Library**. Search for **Cloud Translation API**, open it, and click **Enable**.
6. Create the key. Go to **APIs & Services**, then **Credentials**, then **Create credentials**, then **API key**. Copy the key that appears and keep it somewhere private for Part 2.
7. Lock the key down. Click the key's name. Under **API restrictions**, choose **Restrict key**, tick **Cloud Translation API**, and click **Save**.

## Part 2: Cloudflare (create the relay)

1. Go to [dash.cloudflare.com](https://dash.cloudflare.com/sign-up) and create a free account. No domain or card is needed.
2. In the left menu, open **Workers & Pages** (it may be under **Compute**). Click **Create**, then **Create Worker**, and start from **Hello World**.
3. Name it `rer-translate` and click **Deploy**.
4. Click **Edit code**. Delete everything in the editor and paste in the whole contents of [`worker/translate-worker.js`](../worker/translate-worker.js) from the repository. Click **Deploy**.
5. Add the key. Go back to the Worker's page and open **Settings**, then **Variables and Secrets**, then **Add**. Set:
   - **Type:** Secret
   - **Variable name:** `GOOGLE_API_KEY`
   - **Value:** the key from Part 1

   Click **Deploy** (or **Save**).
6. Copy the Worker's address from its overview page. It looks like `https://rer-translate.your-name.workers.dev`.

## Part 3: Send me the address

Post the Worker address in the thread. I'll add it to the site, test it, and push. Until then the translator keeps working on MyMemory.

If you ever want to switch back, I can set the address back to empty. To shut the relay off completely, delete the Worker in Cloudflare or delete the key in Google Cloud.

## If something goes wrong

- **"The translator isn't set up yet":** the `GOOGLE_API_KEY` secret is missing or misspelled in Cloudflare.
- **"The translator is busy right now":** Google refused the key. Check that the Cloud Translation API is enabled, billing is linked, and the key is restricted to that API rather than to a different one.
- **Nothing happens, or a "Forbidden" error:** the site's address isn't on the Worker's allowed list. It allows `https://goldydev30.github.io`. If you move the site to its own domain, add that domain to `ALLOWED_ORIGINS` at the top of the Worker code.
