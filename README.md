# .github — shared CI + repo standards

Account-wide defaults for `herrrickshaw` repos.

| File | What it does |
|---|---|
| [`.github/workflows/quality.yml`](.github/workflows/quality.yml) | Reusable quality gate: gitleaks full-history secret scan + ruff/black for Python repos. Call it with 4 lines of YAML (see checklist). |
| [`NEW_REPO_CHECKLIST.md`](NEW_REPO_CHECKLIST.md) | Six-point stage gate to run before the first push of any new repo. |

The portfolio catalog (tiers, purpose, data canon, backups, crons for all live
repos) lives in [`repo-traffic-analytics/repos.yaml`](https://github.com/herrrickshaw/repo-traffic-analytics/blob/main/repos.yaml).
