# Independent official Oxford measured-data recheck (2026-11-21)

The [22 November verification update](FOLLOWUP_VERIFICATION.md) records the six source rechecks, browser results and current release decision. The observations below describe the earlier 21 November candidate.

The source is the University of Oxford Research Archive, record [Oxford energy trading battery degradation dataset](https://ora.ox.ac.uk/objects/uuid:9aae61af-2949-49f1-8ad5-6aea448979e5) (DOI 10.5287/bodleian:gJPdDzvP4), published under ODbL/DbCL terms. No official raw profiles or capacity CSVs were committed or redistributed. The independent recomputation read the *official archive files* and used stable ascending time sorting, duplicate-time mean current, clipped positive discharge current, trapezoidal ampere-second/3600 integration, a nominal 16 Ah denominator, and the documented limited near-zero-current final capacity-check tail correction. No calendar-cycle or physics-model extrapolation is involved.

| Official cell | Source profile ID | Capacity ID | Finite profile rows | Unique times | Nonincreasing raw transitions | Duplicate times | Capacity checks | Final unobserved tail (s) | Recomputed discharge EFC | Final retention | Historical target EFC | Recheck |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| BMP_cell1 | `dcc08hf70v` | `d7h149q034` | 69,712 | 69,698 | 17 | 14 | 13 | 154.706 | 412.367955 | 0.9752582351 | 412.37 | PASS |
| BMP_cell2 | `dvx021f16r` | `dth83kz455` | 73,020 | 73,009 | 14 | 11 | 13 | 213.288 | 410.121400 | 0.9755847020 | 410.12 | PASS |
| SPM_cell1 | `d9880vr050` | `d2801pg45q` | 77,949 | 77,936 | 18 | 13 | 13 | 433.410 | 689.231401 | 0.9835216037 | 689.23 | PASS |
| SPM_cell2 | `dhx11xf35n` | `dg732d903f` | 76,623 | 76,612 | 16 | 11 | 13 | 964.327 | 689.929320 | 0.9823329549 | 689.93 | PASS |
| BMR_cell1 | `d7d278t10b` | `dkw52j8142` | — | — | — | — | — | — | — | — | 1558.15 | BLOCKED: archive automated-access rejection |
| BMR_cell2 | `d4b29b6049` | `dxp68kg34h` | — | — | — | — | — | — | — | — | 1557.65 | BLOCKED: official profile target unreachable |

For each successful row, both EFC is within 0.01 of the historical test value and final normalized capacity is within 1e-6 of its test reference. These are deterministic *source arithmetic* checks; they do not establish predictive EOL accuracy and are not a substitute for an independent scientist’s signoff. The externally sourced `tests/test_oxford_live.py` remain skipped in GitHub Actions; do not transform those skips into passes or bundle the licensed dataset as a workaround. Official archive documentation cautions that bulk automated access may be blocked; respect rate/access limits and obtain permission for larger automated runs. Avoid invented BMR measurements.

Source files can be accessed from the official record's listed attachments with the IDs above. For example, the BMP_cell1 profile is `https://ora.ox.ac.uk/objects/uuid:9aae61af-2949-49f1-8ad5-6aea448979e5/files/dcc08hf70v` and its capacity checks are under `.../files/d7h149q034`.
