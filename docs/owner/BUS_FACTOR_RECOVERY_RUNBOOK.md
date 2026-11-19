# Recovery and continuity runbook

This is a proposed recovery procedure grounded in the existing package, workflows and publication route. A recovery exercise, named backup maintainer and recovery-time objective have not been established by this documentation review. [pyproject.toml:5–58](https://github.com/mohammadrezwankhan/battery-cycle-life-analyzer/blob/02ed161bded286dad4b3624961430a564715c782/pyproject.toml#L5-L58) [.github/workflows/publish-pypi.yml:1–109](https://github.com/mohammadrezwankhan/battery-cycle-life-analyzer/blob/02ed161bded286dad4b3624961430a564715c782/.github/workflows/publish-pypi.yml#L1-L109) [.github/workflows/deploy-dashboard.yml:61–90](https://github.com/mohammadrezwankhan/battery-cycle-life-analyzer/blob/02ed161bded286dad4b3624961430a564715c782/.github/workflows/deploy-dashboard.yml#L61-L90)

## Preserve the recoverable unit

Keep an authorized repository backup including Git refs/history, code, docs, tests, dependency manifests/locks, workflows, notebook and citation/license. Preserve release distributions with digests and their publishing source/run identities. Separately retain the actual applicable GitHub branch/environment settings and access ownership in a restricted operational record; do not put credentials or recovery codes in Git. External Oxford data needs its own source identity, retrieval date, digest, licensing record and preprocessing receipts if a study relies on it. [examples/oxford_energy_trading.py:25–54](https://github.com/mohammadrezwankhan/battery-cycle-life-analyzer/blob/02ed161bded286dad4b3624961430a564715c782/examples/oxford_energy_trading.py#L25-L54) [docs/oxford-energy-trading.md:9–25](https://github.com/mohammadrezwankhan/battery-cycle-life-analyzer/blob/02ed161bded286dad4b3624961430a564715c782/docs/oxford-energy-trading.md#L9-L25)

## Restore in evidence order

1. **Establish authorized access.** The account/service owner restores access through existing recovery procedures. Preserve protection settings and environment requirements; do not bypass them to make a restoration appear successful.
2. **Choose the exact target.** Record the desired source commit, release tag/distribution and documentation deployment independently. Resolve the version drift described in the release playbook before promising a particular installed version.
3. **Reconstruct locally.** Clone the recorded source, provision an isolated environment, record resolved packages, and run native tests with live Oxford access off. Execute the synthetic quickstart and inspect actual outputs.
4. **Restore documentation.** Verify canonical Markdown/CFF, regenerate the static reference, run local links/CSP/guide checks, and review the entire diff. The notebook and preview are separate generators; do not overwrite them incidentally.
5. **Revalidate hosted gates.** Create a normal restoration/revert PR. Observe checks/reviews on its exact head and the current branch policy. Keep any unavailable required gate explicitly blocked.
6. **Restore public delivery.** Merge with an expected-head guard; map the Pages deployment to that merge and inspect the visible handbook content and navigation. A PyPI recovery is a separate tagged release process with owner authorization and package provenance.

[Setup](../developer/SETUP_AND_REPRODUCIBILITY.md), [verification](../maintainer/VERIFICATION_EVIDENCE_LEDGER.md) and [publication](../maintainer/CI_CD_AND_RELEASE_PLAYBOOK.md) supply commands and evidence boundaries.

## When a result cannot be reproduced

Compare input bytes and preprocessing counts first, then source SHA, dependency versions, seed, model family, split, bootstrap settings and EOL horizon. A historical Oxford audit without its original input receipts cannot be relabeled as a new reproduction. Preserve failed/censored outcomes and record the missing material. Roll back erroneous docs by a scoped reviewed revert and verify its deployment; preserve the old evidence for diagnosis.

Roadmap BCLA-08 proposes a second-person clean-environment recovery exercise with explicit success/failure records and an owner-approved recovery-time target. No staffing or timing commitment is implied.
