# New-repo stage gate

Six checks before the **first push** of any new repo. Two minutes now beats an
incident later (misnamed repos, leaked creds, and orphaned data files have all
happened in this account).

- [ ] **Name matches content.** The repo name describes what is actually inside
      (check: would a stranger reading only the name predict the README?).
- [ ] **`.gitignore` present and a local `gitleaks detect` pass is clean.**
      Real credentials live only in gitignored machine-local files; tracked
      copies ship placeholders. Check `git diff --cached`, not plain `git diff`.
- [ ] **README** states purpose, how to run, and where the data comes from.
- [ ] **Catalog entry added** to `repo-traffic-analytics/repos.yaml`
      (tier, purpose, canonical data location, backup plan, cron jobs if any).
- [ ] **Canonical data file declared.** If the repo stores market/reference
      data, the README names the ONE authoritative file/table. No second copy
      elsewhere without a pointer back (prevents the two-file trap).
- [ ] **Backup plan.** Where does durable data live if this clone or repo is
      lost? (GitHub is primary; large artifacts go to `market-data-artifacts`
      releases, NOT LFS — the LFS budget is exhausted account-wide.)

## CI wiring (30 seconds)

Add `.github/workflows/ci.yml`:

```yaml
name: ci
on: [push, pull_request]
jobs:
  quality:
    uses: herrrickshaw/.github/.github/workflows/quality.yml@main
    with:
      python: "true"   # "false" for non-Python repos
```
