@echo off
rem Redeploys the Codex translation relay (Cloud Run service rer-translate).
rem Pull the latest code in GitHub Desktop first, then double-click this file
rem or run it from any terminal. Needs the Google Cloud CLI, signed in.

cd /d "%~dp0..\gcp\translate-function"

call gcloud.cmd config set project raven-eye-511902
call gcloud.cmd run deploy rer-translate --source . --function translate --base-image nodejs22 --region us-central1 --max-instances 2
call gcloud.cmd run services update rer-translate --region=us-central1 --no-invoker-iam-check

echo.
echo Done. Service URL: https://rer-translate-387319036805.us-central1.run.app
pause
