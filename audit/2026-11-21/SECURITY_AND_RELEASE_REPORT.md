# Security, packaging and release governance

## Security and CI

- Repository `AGENTS.md` requires preserving PR validations, matrices, security gates, workflow permissions, and immutable action SHA pins; no CI gate or timeout was weakened in this PR.
- Existing workflows include CodeQL and Hardened CI (SAST, secrets, dependencies, Trivy, Python/browser QA); tests.yml covers Python3.9–3.12, and package-validation checks wheels without publishing. Repository supplies `.gitleaks.toml`, `.semgrep.yml`, secure scanner configuration and documented CI runbooks.
- The first corrected candidate CodeQL completed successfully: https://github.com/mohammadrezwankhan/battery-cycle-life-analyzer/actions/runs/44944454689 . Broader hardened CI 44944454664 had not completed when this report was generated. Passing scanners do not demonstrate absence of undiscovered vulnerabilities.

## Distributions

- `pyproject.toml` declares version `0.3.0` and `requires-python >=3.9`; the v0.3.0 Git tag points to `65df747ccf1ff0d2427ab8ba321b4c6839d0ad3b`, not the current main head.
- Candidate sdist/wheel build, strict twine check, isolated installed-wheel import and CLI/PNG test all passed (run 44944454661). No publishing, package upload, or deployment performed.
- At baseline runtime `bcla.__version__` was 0.2.0, contradicting project metadata 0.3.0; it is corrected to 0.3.0 on the audit branch, with regression asserting installed distribution parity. No package version bump.
- Baseline CHANGELOG's 0.3.0 Pending release heading contradicted the preserved maintainer playbook documenting PyPI upload 2026-10-08 and the existing v0.3.0 tag. The audit updates that heading while preserving the distinction that GitHub Releases lacks a v0.3.0 Release record and the PyPI history was not independently re-fetched in this audit.

## Outstanding release controls

Require up-to-date CI on final commit, explicit independent scientific and system review, security results, browser QA, and review of release metadata/publication policy. Do not reuse a prior signed artifact's verification as proof of a new build. No credentials were added to repository source or reports.

**Decision: publishing and merging remain disallowed by audit readiness until review and blocking evidence are resolved.**

## Subsequent verified hardening status

Run 44945020410 (commit 0c79e9a8…) passed all five security modes (workflow, secrets, SAST, dependencies, Trivy), all four browser quality modes, Python typing, and Python tests/coverage; Python lint was the sole failed job. Its saved Ruff report identified exactly PTH105 (prefer Path.replace) and four ARG001 unused mock arguments. Source/test lint has been corrected without changing rules; final-head validation is still required. CodeQL, package-distribution smoke and documentation checks passed on the same 0c79e9a8… commit.

## Publication gating clarified after second-pass review

The existing 0.3.0 version was published to PyPI on 2026-10-08 and cannot be overwritten. A new release must be deliberately versioned (for example v0.3.1), with the matching `pyproject.toml`, runtime version, changelog and release tag, and must pass the existing tag-triggered Python matrix, build, trusted-publishing OIDC/environment gate, and post-release installed-wheel smoke. No tag, PyPI publication or GitHub Pages deployment has been created for this unmerged audit branch.

The broader hardened security/quality workflow remains mandatory. Its second-pass run 44958616487 passed all five security categories but failed one Ruff test-function naming rule (N802); final-HEAD confirmation is required before any merge. This report is not a substitute for GitHub reviewer approvals or the actual PyPI/publishing run.

## Third-pass mandatory quality results

On source revision `1365fb7f2c55b6d0a02c5c217c849892147c8371`, GitHub Hardened CI run 44959498963 returned **success** (12 of 12 jobs). The Python supported-version matrix, package build/installed-wheel smoke, CodeQL, documentation, and human-authorship pattern checks also returned successful conclusions. The earlier second-pass Ruff N802 failure was corrected by renaming one test without relaxing lint configuration. **This is successful software verification, not independent scientific certification**. The current documentation commit requires its own CI run; release and protected branch rules are unchanged.
