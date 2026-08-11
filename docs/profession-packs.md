# Career toolpacks

WutPack includes 30 CLI-selectable packs: ten from a general high-pay snapshot,
ten finance packs, and ten engineering packs. Each combines existing WutPack
specialists and deterministic tools with a safe, role-specific starter prompt.

## Selection basis

There is no single authoritative, globally comparable ranking of detailed
profession pay. Currency, purchasing power, employment form, specialty coding,
and whether self-employed income is included all change the result.

The [ILO Global Wage Report 2024–25](https://www.ilo.org/sites/default/files/2024-11/GWR-2024_Layout_E_RGB_Web.pdf)
uses harmonized evidence from 82 countries to analyze wage distributions. It
supports the need for cross-country caution, but it does not publish an exact
worldwide top-ten list of detailed professions. The BLS selections below are
therefore transparent U.S. proxies, not mislabeled global facts.

### General high-pay snapshot

The first collection follows the first ten entries in the
[U.S. Bureau of Labor Statistics highest-paying occupations table](https://www.bls.gov/ooh/highest-paying.htm).
That table uses 2024 U.S. median annual pay and was last modified August 28,
2025. All ten selected occupations are tied in its top-coded bracket of at least
USD 239,200; the displayed order is therefore a source-table order, not a claim
that rank 1 earns more than rank 10.

| Source order | Profession | Toolpack |
|---:|---|---|
| 1 | Psychiatrists | `psychiatry` |
| 2 | Surgeons, all other | `surgery` |
| 3 | Dermatologists | `dermatology` |
| 4 | Pediatric surgeons | `pediatric-surgery` |
| 5 | Prosthodontists | `prosthodontics` |
| 6 | Anesthesiologists | `anesthesiology` |
| 7 | Emergency medicine physicians | `emergency-medicine` |
| 8 | Radiologists | `radiology` |
| 9 | Ophthalmologists, except pediatric | `ophthalmology` |
| 10 | Physicians, pathologists | `pathology` |

### Finance snapshot

The finance collection uses annual mean wages in the
[May 2025 OEWS national table](https://www.bls.gov/news.release/ocwage.t01.htm),
released May 15, 2026. It selects financial managers plus the nine highest-paid
named, detailed finance-specialist roles, omitting aggregate “all other” rows.
These are U.S. wages for wage-and-salary workers, not total compensation and not
a claim about self-employed or worldwide earnings.

| Finance order | Profession | Annual mean wage | Toolpack |
|---:|---|---:|---|
| 1 | Financial managers | $186,910 | `finance-management` |
| 2 | Personal financial advisors | $156,670 | `finance-advisory` |
| 3 | Financial risk specialists | $124,420 | `finance-risk` |
| 4 | Financial and investment analysts | $116,800 | `finance-investment-analysis` |
| 5 | Financial examiners | $106,240 | `finance-examination` |
| 6 | Credit analysts | $100,850 | `finance-credit` |
| 7 | Budget analysts | $96,370 | `finance-budget` |
| 8 | Accountants and auditors | $94,750 | `finance-accounting` |
| 9 | Insurance underwriters | $93,700 | `finance-underwriting` |
| 10 | Loan officers | $87,790 | `finance-lending` |

### Engineering snapshot

The engineering collection sorts the detailed engineer roles in the
[BLS Architecture and Engineering occupations table](https://www.bls.gov/ooh/architecture-and-engineering/)
by 2024 median annual pay. It excludes managers, architects, surveyors, drafters,
and technician roles so the comparison remains within detailed engineering
occupations.

| Engineering order | Profession | Median annual pay | Toolpack |
|---:|---|---:|---|
| 1 | Computer hardware engineers | $155,020 | `engineering-hardware` |
| 2 | Petroleum engineers | $141,280 | `engineering-petroleum` |
| 3 | Aerospace engineers | $134,830 | `engineering-aerospace` |
| 4 | Nuclear engineers | $127,520 | `engineering-nuclear` |
| 5 | Chemical engineers | $121,860 | `engineering-chemical` |
| 6 | Electrical and electronics engineers | $118,780 | `engineering-electrical` |
| 7 | Health and safety engineers | $109,660 | `engineering-safety` |
| 8 | Materials engineers | $108,310 | `engineering-materials` |
| 9 | Bioengineers and biomedical engineers | $106,950 | `engineering-biomedical` |
| 10 | Marine engineers and naval architects | $105,670 | `engineering-marine` |

Research cutoff: August 11, 2026.

## CLI usage

List the available packs:

```bash
wut packs
wut packs profession
wut packs finance
wut packs engineering
```

Inspect a full pack or just its selected toolchain:

```bash
wut pack radiology
wut pack radiology tools
```

Create a copy-ready prompt with an optional request:

```bash
wut pack radiology prompt "Analyze de-identified turnaround data by modality."
```

Launch interactive Codex with the same pack and request:

```bash
wut pack radiology codex "Analyze de-identified turnaround data by modality."
```

The `codex` action deliberately uses the normal interactive Codex CLI, including
its existing authentication, sandbox, and permission controls. It does not call
Claude Code, copy credentials, or silently start an agent.

## Domain boundaries

### Clinical and privacy

These packs support professional work; they are not clinical decision systems.
They prohibit patient-specific diagnosis, treatment selection, medication or
dose recommendations, diagnostic image or specimen interpretation, and live
triage. Use fictional or properly de-identified inputs, follow organizational
privacy controls, and require licensed human review before any clinical use.

Each pack makes its narrower boundary explicit. The tools are best suited to
literature review, aggregate quality analysis, capacity and workflow modeling,
controlled-document drafting, and review-ready communication.

### Finance

Finance packs create analysis and drafts, not personalized financial, investment,
tax, legal, insurance, or credit advice. They do not execute trades, approve or
deny credit, bind coverage, certify accounts, or issue regulatory or audit
opinions. Jurisdiction, data cutoff, assumptions, and accountable review must be
explicit.

### Engineering

Engineering packs create requirements, analysis, diagrams, and review evidence;
they do not certify designs, issue construction or operating instructions, set
live controls, or authorize release or hazardous work. Governing standards,
configuration, units, uncertainty, safety classification, and independent
professional review remain mandatory.
