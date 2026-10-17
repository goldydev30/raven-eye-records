# Deploy

## Codex translator (Google Cloud Run)

To push a new version of `gcp/translate-function` to Google Cloud:

1. Pull the latest code in GitHub Desktop.
2. Double-click `redeploy-translator.cmd` (Windows), or run it from a terminal.

It sets the project (`raven-eye-511902`), deploys the `rer-translate` service to `us-central1`, and keeps it open to the website. The build takes a few minutes.

The same commands, if you'd rather type them (from `gcp/translate-function`):

```
gcloud.cmd config set project raven-eye-511902
gcloud.cmd run deploy rer-translate --source . --function translate --base-image nodejs22 --region us-central1 --max-instances 2
gcloud.cmd run services update rer-translate --region=us-central1 --no-invoker-iam-check
```

The website itself needs no deploy: GitHub Pages publishes every push to `main`.
