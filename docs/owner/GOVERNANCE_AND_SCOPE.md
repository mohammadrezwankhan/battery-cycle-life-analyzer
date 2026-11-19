# Governance and scope

The repository is owned by `mohammadrezwankhan`; the existing citation and package metadata attribute the software to **Mohammad Rezwan Khan**. The tracked license is MIT. No backup maintainer, service-level agreement or formal governance committee is declared in the reviewed source. Roles below are a proposed operating arrangement, not invented appointments. [CITATION.cff:1–16](https://github.com/mohammadrezwankhan/battery-cycle-life-analyzer/blob/02ed161bded286dad4b3624961430a564715c782/CITATION.cff#L1-L16) [pyproject.toml:18–20](https://github.com/mohammadrezwankhan/battery-cycle-life-analyzer/blob/02ed161bded286dad4b3624961430a564715c782/pyproject.toml#L18-L20) [LICENSE:1–21](https://github.com/mohammadrezwankhan/battery-cycle-life-analyzer/blob/02ed161bded286dad4b3624961430a564715c782/LICENSE#L1-L21)

| Role | Accountability |
| --- | --- |
| Repository owner / release maintainer | Scope, access recovery, applicable protection settings, release approval and provenance |
| Scientific reviewer | Model assumptions, units, preprocessing conventions, validation design and uncertainty claims |
| Contributor / documentation author | Source-grounded change, exact evidence, reproducible examples and narrow diff |
| Independent reviewer | Candidate-specific factual, interface, scientific and operational review |
| Integration owner | Exact tree/commit mapping, current gates, expected-head merge and deployment verification |

## Scope of the software and this package

The native package implements empirical curve fitting, temporal family selection, bounded EOL/RUL estimates, residual bootstrap, loaders and plotting. The browser is a separate educational model. External measured-data validation, production BMS use, calibrated chemistry inference and safety certification are outside the evidence established here. The [assumptions page](../math-and-physics/ASSUMPTIONS_AND_LIMITS.md) is the claim boundary. [bcla/core.py:18–42](https://github.com/mohammadrezwankhan/battery-cycle-life-analyzer/blob/02ed161bded286dad4b3624961430a564715c782/bcla/core.py#L18-L42) [bcla/core.py:299–435](https://github.com/mohammadrezwankhan/battery-cycle-life-analyzer/blob/02ed161bded286dad4b3624961430a564715c782/bcla/core.py#L299-L435) [docs/index.html:155–189](https://github.com/mohammadrezwankhan/battery-cycle-life-analyzer/blob/02ed161bded286dad4b3624961430a564715c782/docs/index.html#L155-L189)

This change adds canonical documentation, a derived static reading view and small navigation links. It preserves native algorithms, tests, workflows, dependencies, notebook/data/results, license and existing citation metadata. Scientific/model/dependency/security-policy changes proposed by the [roadmap](../../ROADMAP.md) require separate review and evidence.

The software's MIT license does not establish a license for external Oxford data. The adapter/walkthrough records that dataset's separate ODbL/DbCL attribution; preserve source provenance and verify applicable permissions before redistributing external data or derived material. No dataset was mirrored or newly licensed by this documentation work. [docs/oxford-energy-trading.md:9–25](https://github.com/mohammadrezwankhan/battery-cycle-life-analyzer/blob/02ed161bded286dad4b3624961430a564715c782/docs/oxford-energy-trading.md#L9-L25)

## Change decisions and ownership evidence

Use ordinary PR review with an independently reviewable diff. Record the source SHA, what behavior or claim changes, validation evidence and any unresolved constraints. Operational policy comes from actual authorized GitHub settings, not assumptions from a sibling repository. Keep declared conventions, executed observations, historical records and proposed design decisions distinct. [Decision index](ADR/ADR-0000-INDEX.md) · [CI/release procedure](../maintainer/CI_CD_AND_RELEASE_PLAYBOOK.md).

Assign a second maintainer and record authorized access/recovery ownership outside public docs before claiming reduced bus factor. Publish only information appropriate for this public repository; never place credentials, private measurements or private portfolio details in a public README, issue or roadmap.
