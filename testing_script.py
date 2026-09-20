"""
HealthConnect Clinic - Week 7 Analytics Testing & Refinement Script
AnalystLab Africa Experience Lab | Data Analytics Track
Author: Georgina Wawira

Purpose: Systematically re-test the Week 6 analytical outputs (KPIs and the
4-tier risk segmentation) directly against the underlying dataset, diagnose
and fix the Week 6 Power BI DAX error, and re-validate after refinement.
"""

import pandas as pd
from scipy import stats

DATA_PATH = "HealthConnect_Clean_ForPowerBI.csv"

def load_data():
    df = pd.read_csv(DATA_PATH)
    base = df[df["in_noshow_base"] == 1].copy()
    return df, base


# ---------------------------------------------------------------------------
# TEST 1 — Core KPI validation (no-show rate, cancellation rate)
# ---------------------------------------------------------------------------
def test_core_kpis(df, base):
    total = len(df)
    cancelled = (df["appointment_outcome"] == "Cancelled").sum()
    cancel_rate = cancelled / total
    noshow_rate = base["is_noshow"].mean()
    results = {
        "cancellation_rate": cancel_rate,
        "cancellation_n": cancelled,
        "total_n": total,
        "noshow_rate": noshow_rate,
        "noshow_base_n": len(base),
        "noshow_n": int(base["is_noshow"].sum()),
    }
    return results


# ---------------------------------------------------------------------------
# TEST 2 — Data integrity / derived-field consistency checks
# ---------------------------------------------------------------------------
def test_data_integrity(df):
    checks = {}
    checks["duplicate_appointment_ids"] = int(df["appointment_id"].duplicated().sum())
    checks["is_noshow_vs_outcome_mismatches"] = int(
        ((df["is_noshow"] == 1) != (df["appointment_outcome"] == "No-Show")).sum()
    )
    checks["in_noshow_base_vs_cancelled_mismatches"] = int(
        ((df["in_noshow_base"] == 0) != (df["appointment_outcome"] == "Cancelled")).sum()
    )
    checks["reminder_flag_mismatches"] = int(
        ((df["reminder_sent"] == "No") != (df["reminder_channel_clean"] == "No Reminder Sent")).sum()
    )
    checks["has_prior_noshow_vs_previous_no_shows_mismatches"] = int(
        ((df["has_prior_noshow"] == 1) != (df["previous_no_shows"] > 0)).sum()
    )
    return checks


# ---------------------------------------------------------------------------
# TEST 3 — Risk segmentation: rebuild in Python (source of truth) and check
# it against the Power BI DAX logic. This is the ground truth used to
# diagnose the Week 6 DAX error and validate the corrected DAX (see report).
# ---------------------------------------------------------------------------
def build_risk_segment(base):
    base = base.copy()
    base["f_long_lead"] = base["lead_bracket"].isin(["15-30 days", "31-60 days"]).astype(int)
    base["f_prior_noshow"] = base["has_prior_noshow"]
    base["f_no_reminder"] = (base["reminder_channel_clean"] == "No Reminder Sent").astype(int)
    base["risk_score"] = base["f_long_lead"] + base["f_prior_noshow"] + base["f_no_reminder"]
    tier_map = {0: "Low", 1: "Baseline", 2: "High", 3: "Triple-risk"}
    base["risk_segment"] = base["risk_score"].map(tier_map)
    return base


def test_risk_segment_predictive_validity(base_scored):
    summary = base_scored.groupby("risk_segment").agg(
        n=("is_noshow", "size"), noshow_rate=("is_noshow", "mean")
    ).reindex(["Low", "Baseline", "High", "Triple-risk"])
    summary["pct_of_base"] = summary["n"] / len(base_scored)
    rates = summary["noshow_rate"].tolist()
    monotonic = all(rates[i] <= rates[i + 1] for i in range(len(rates) - 1))
    return summary, monotonic


# ---------------------------------------------------------------------------
# TEST 4 — Significance of each risk factor used in the segmentation, plus
# distance (currently excluded) — checks whether the segmentation still
# uses the right drivers and flags a candidate improvement for Week 8.
# ---------------------------------------------------------------------------
def test_driver_significance(base):
    out = {}
    for col in ["reminder_sent", "has_prior_noshow", "lead_bracket"]:
        ct = pd.crosstab(base[col], base["is_noshow"])
        _, p, _, _ = stats.chi2_contingency(ct)
        out[col] = p
    ct_dist = pd.crosstab(base["distance_band"].fillna("Unknown"), base["is_noshow"])
    _, p_dist, _, _ = stats.chi2_contingency(ct_dist)
    out["distance_band"] = p_dist
    return out


# ---------------------------------------------------------------------------
# TEST 5 — Segment consistency check: does the overall no-show finding hold
# (is not an artefact of one subgroup) across gender, age, appointment type,
# day, time and distance?
# ---------------------------------------------------------------------------
def test_segment_consistency(base):
    overall = base["is_noshow"].mean()
    tables = {}
    for col in ["gender", "age_group", "appointment_type", "appointment_day", "appointment_time", "distance_band"]:
        g = base.groupby(col)["is_noshow"].agg(n="size", noshow_rate="mean").sort_values("noshow_rate")
        tables[col] = g
    return overall, tables


if __name__ == "__main__":
    df, base = load_data()

    print("=== TEST 1: Core KPI validation ===")
    print(test_core_kpis(df, base))

    print("\n=== TEST 2: Data integrity checks ===")
    print(test_data_integrity(df))

    print("\n=== TEST 3: Risk segmentation predictive validity ===")
    base_scored = build_risk_segment(base)
    summary, monotonic = test_risk_segment_predictive_validity(base_scored)
    print(summary)
    print("Monotonic (higher tier -> higher no-show rate):", monotonic)

    print("\n=== TEST 4: Driver significance (chi-square p-values) ===")
    print(test_driver_significance(base))

    print("\n=== TEST 5: Segment consistency ===")
    overall, tables = test_segment_consistency(base)
    print("Overall no-show rate:", overall)
    for k, v in tables.items():
        print(f"\n-- {k} --")
        print(v)

    base_scored.to_csv("HealthConnect_Week7_Tested_Data.csv", index=False)
    print("\nSaved HealthConnect_Week7_Tested_Data.csv with validated risk_score/risk_segment columns.")
