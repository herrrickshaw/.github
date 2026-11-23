# .github — shared CI + repo standards

<!-- how-to-use-with-ai -->
> **New here?** See [How to use this repo with AI (Claude, Gemini, ChatGPT)](HOW_TO_USE_WITH_AI.md) — clone it, paste it into an AI tool, and ask in plain English.


Account-wide defaults for `herrrickshaw` repos.

| File | What it does |
|---|---|
| [`.github/workflows/quality.yml`](.github/workflows/quality.yml) | Reusable quality gate: gitleaks full-history secret scan + ruff/black for Python repos. Call it with 4 lines of YAML (see checklist). |
| [`.github/workflows/daily-stock-scanner.yml`](.github/workflows/daily-stock-scanner.yml) | Reusable daily-scan runner for the stock-screening repos: restores cached data from Dropbox/Google Drive (rclone), runs the calling repo's own scan command, uploads the generated reports. The screener logic itself stays in the calling repo — see the workflow's header comment for the call snippet. |
| [`NEW_REPO_CHECKLIST.md`](NEW_REPO_CHECKLIST.md) | Six-point stage gate to run before the first push of any new repo. |

The portfolio catalog (tiers, purpose, data canon, backups, crons for all live
repos) lives in [`repo-traffic-analytics/repos.yaml`](https://github.com/herrrickshaw/repo-traffic-analytics/blob/main/repos.yaml).
