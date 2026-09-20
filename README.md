# HealthConnect Clinic — No-Show Analytics

**AnalystLab Africa Experience Lab · Data Analytics Track**
**Author:** Georgina Wawira · [LinkedIn](https://linkedin.com/in/georgina-wawira-0a2782340) · [GitHub](https://github.com/Wawidata)

A multi-week analytics project for **HealthConnect Clinic**, a fictional healthcare
provider trying to answer one question:

> **How can HealthConnect Clinic use data and AI to reduce missed appointments and
> improve the patient support experience?**

This repo tracks the Data Analytics track's work from initial EDA through
integration, testing and refinement, across a 5,000-record appointment dataset.

---

## Project Timeline

| Week | Focus | Status |
|---|---|---|
| 4 | Problem understanding, resource review, solution planning | ✅ |
| 5 | EDA, core KPIs, first Power BI dashboard, business insights | ✅ |
| 6 | Deeper analysis, 4-tier risk segmentation, dashboard v2, simulated Data Science hand-off | ✅ |
| **7** | **Testing, refinement, end-to-end validation of Weeks 5–6 outputs** | ✅ *(this update)* |
| 8 | Final integration & presentation | ⏳ upcoming |

---

## Week 7 — Testing, Refinement & Validation

Week 7 shifted from *building* to *proving the build works*. Every KPI and
derived field from Weeks 5–6 was re-tested directly against the raw dataset
rather than assumed correct.

### What testing found

| Test | Result |
|---|---|
| No-show rate, cancellation rate, repeat-risk share vs. raw data | ✅ All reconcile exactly |
| 5 derived-field consistency checks (`is_noshow`, `in_noshow_base`, reminder flags, `lead_bracket`, `has_prior_noshow`) | ✅ 0 mismatches |
| `distance_band` vs. raw distance | ⚠️ 102 boundary cases — investigated, confirmed to be a consistent inclusive-upper-bound convention, not an error |
| **`risk_segment` DAX calculated column (Power BI)** | ❌ **Failed** — nested `IF()`/`IN{}` syntax error, column never computed |
| Corrected `risk_segment` DAX vs. independent Python calculation | ✅ 100% match across 4,737 rows |
| Risk tier predictive validity (no-show rate by tier) | ✅ Monotonic: 27.9% → 46.8% → 59.1% → 67.1% |
| Chi-square significance of all 3 segmentation drivers + distance | ✅ All p < 0.05 (distance significant but not yet included — Week 8 candidate) |
| Cross-segment consistency (gender, age, appointment type, day, time, distance) | ✅ No subgroup reverses the overall trend |

**The one real defect found and fixed:** the Week 6 `risk_segment` DAX column
used deeply nested `IF()` logic that Power BI rejected. It was rebuilt using
the `SWITCH(TRUE(), …)` pattern, validated independently in Python first, and
confirmed to match exactly on retest. See [`/dax`](./dax) for the corrected
formulas and [`/docs/week7_testing_output_log.txt`](./docs/week7_testing_output_log.txt)
for the full test run.

### Risk Tier — validated

| Tier | Patients | % of Base | No-Show Rate |
|---|---|---|---|
| Low (0 risk factors) | 524 | 11.1% | 27.9% |
| Baseline (1 factor) | 2,024 | 42.7% | 46.8% |
| High (2 factors) | 1,755 | 37.0% | 59.1% |
| Triple-risk (3 factors) | 434 | 9.2% | 67.1% |

Risk factors: long booking lead time (15+ days), a prior no-show on record,
no reminder sent.

### Dashboard change

Week 7 deliberately shows only the **delta**, not a full dashboard rebuild —
the reminder-channel, booking-lead-time, appointment-type and distance-band
charts were re-tested (found valid) and left untouched. What changed:
- The risk tier card — went from a broken/error state to a working, validated bar chart
- The repeat-risk KPI — split into two explicit cards (of no-shows / of all appointments) to remove a base ambiguity flagged in Week 6



### Cross-track testing — Data Science

The risk-segmented output is a direct input to the Data Science track's
no-show prediction model. This week's cross-track testing confirmed the
corrected `risk_segment`/`risk_score` fields are reproducible and safe to use
as a model feature (full Test → Finding → Action → Retest record in the
Week 7 report, Section 6).

---

## Repository Structure
healthconnect-analytics/
├── README.md
├── python/
│ └── week7_testing_script.py # re-runs all Week 7 test groups against the raw data
├── dax/
│ ├── risk_segmentation_columns.dax # corrected Risk_Score / Risk_Segment / sort column
│ └── week7_measures.dax # tier + repeat-risk measures, validation check
├── data/
│ └── HealthConnect_Week7_Tested_Data.csv # validated risk_score/risk_segment added
├── dashboard/
│ ├── HealthConnect_Week7_Dashboard_Change.html # interactive before/after
│ └── HealthConnect_Week7_Dashboard_Visual.png # target layout for the Power BI build
├── docs/
│ └── week7_testing_output_log.txt # raw console evidence for every test result
└── reports/
└── HealthConnect_Week7_Testing_Refinement_Report.docx

> Earlier weeks' `sql/`, `python/`, `data/`, `reports/` and `dashboard/` files
> (Week 5 EDA + SQL cleaning, Week 6 advanced analytics + risk segmentation
> design) live alongside these in the full project history — this update
> adds the Week 7 testing artefacts without overwriting them.

---

## How to Reproduce the Week 7 Tests

```bash
cd python
pip install pandas scipy
python week7_testing_script.py
```

Runs all 5 test groups (KPI validation, data integrity, risk segmentation
predictive validity, driver significance, cross-segment consistency) against
`HealthConnect_Clean_ForPowerBI.csv` and writes
`HealthConnect_Week7_Tested_Data.csv` with the validated `risk_score` /
`risk_segment` columns populated.

## Tech Stack

Python (pandas, scipy) · SQL · Power BI (DAX) · Excel

---

*Part of the AnalystLab Africa Experience Lab — HealthConnect Clinic Experience Lab.*
*#AnalystLabAfrica*
