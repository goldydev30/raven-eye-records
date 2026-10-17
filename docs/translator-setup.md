# Setting up Google translation for the Codex

The Codex translator currently uses MyMemory, a free service with a small daily limit. These steps switch it to Google Cloud Translation, everything inside your own Google Cloud project.

A small **Cloud Run function** sits between the website and Google. It signs in as its own Google identity (a "service account"), so there is no API key to store or leak. You'll end up with one web address to send me.

## Part 1: Google Cloud project (done)

1. Create a project at [console.cloud.google.com](https://console.cloud.google.com) and link billing.
2. Add a budget alert: **Billing**, then **Budgets & alerts**, then **Create budget**, $5, alerts on.
3. Enable the **Cloud Translation API**: **APIs & Services**, then **Library**.

The first 500,000 translated characters each month are free, which is about 1,000 full 250-word translations. Cloud Run's free tier covers the relay itself at this scale.

You don't need an API key for this setup. If you made one, you can delete it under **APIs & Services**, then **Credentials**.

## Part 2: Create the Cloud Run function

1. In the console's search bar, type **Cloud Run** and open it. If asked, click **Enable** for the Cloud Run Admin API.
2. Click **Write a function**. If you see **Create service** instead, click it and choose **Use an inline editor to create a function**.
3. Fill in the form:
   - **Service name:** `rer-translate`
   - **Region:** `us-central1` (or one near you)
   - **Runtime:** the newest **Node.js** listed
   - **Authentication:** **Allow public access** (it may be called *Allow unauthenticated invocations*). The website calls it without signing in, and the code itself only answers your site.
   - Under **Containers, Volumes, Networking, Security**, then **Revision scaling**, set **Maximum number of instances** to `2`. This caps cost if anything ever goes wrong.
4. Click **Create**. If Google asks to enable extra APIs (Cloud Build, Artifact Registry), click **Enable**.
5. The source editor opens with two files:
   - In **index.js**, delete everything and paste the contents of [`gcp/translate-function/index.js`](../gcp/translate-function/index.js).
   - In **package.json**, delete everything and paste the contents of [`gcp/translate-function/package.json`](../gcp/translate-function/package.json).
   - Set **Function entry point** to `translate`.
6. Click **Save and redeploy**. It takes a minute or two and shows a green check when it's done.

## Part 3: Let the function use the Translation API

1. On the `rer-translate` page, open the **Security** tab (or **Revisions**, then the latest revision) and note the **Service account**. It usually looks like `123456789-compute@developer.gserviceaccount.com`.
2. Open **IAM & Admin**, then **IAM**, and click **Grant access**.
3. In **New principals**, paste that service account. In **Role**, choose **Cloud Translation API User**. Click **Save**.

## Part 4: Send me the address

Copy the URL at the top of the `rer-translate` page. It looks like `https://rer-translate-abc123-uc.a.run.app`. Post it in the thread and I'll switch the site over and test it. Until then the translator keeps working on MyMemory.

To shut it off later, delete the `rer-translate` service in Cloud Run.

## If something goes wrong

- **"Allow public access" is greyed out, or saving fails with a policy error** (it mentions `allUsers` or `iam.allowedPolicyMemberDomains`): your Google organization blocks public services. An organization admin can add an exception for this project under **IAM & Admin**, then **Organization Policies**, then **Domain restricted sharing**. Tell me if you hit this and I'll walk you through it.
- **"The translation failed" on the site:** the service account is probably missing the **Cloud Translation API User** role (Part 3), or the Translation API isn't enabled. The function's **Logs** tab shows the exact reason.
- **Nothing happens, or "Forbidden":** the site's address isn't on the allowed list. The function allows `https://goldydev30.github.io`. If you move the site to its own domain, add it to `ALLOWED_ORIGINS` at the top of `index.js` and redeploy.
