# 10: Remove Jekyll and finish

**What to build:** The branch is ready to merge.
- Remove the Gemfile, Gemfile.lock, `_config.yml`, `_plugins/`, the old `_layouts`/`_includes`/`_data` locations and any other Jekyll-only leftovers.
- Update the README and `AGENTS.md` for Zola: `zola serve`, the content layout, shortcodes, explicit `path`, self-contained Translations, build-time checks.
- Rebase onto the latest `master`, port any content that landed there since the Baseline, rebuild the Baseline at the new `master`, and run the Parity check over the whole site.
- Save the Parity check report for the PR body, then delete the Parity check script, the one-time migration scripts and `.scratch/`.
- Open the PR (one PR), with the report and the Cloudflare preview link, and click through the preview: search, theme toggle, language switch, pagination.

**Blocked by:** 05, 06, 07, 08, 09

**Status:** ready-for-agent

- [x] No Ruby or Jekyll file or reference remains in the repo (`AGENTS.md`, README, Dockerfile, workflows, Dependabot)
- [x] Full-site Parity check against the rebuilt Baseline is clean apart from the documented exceptions
- [ ] PR opened with the report and preview evidence (left to the user: push, PR, Cloudflare preview click-through; report in zola-notes/parity-report.md. `_parity/`, `_migrate/`, `.scratch/` kept for the code review, delete before merge)
