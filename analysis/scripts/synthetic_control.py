"""
synthetic_control.py
=====================
Synthetic Control Method (SCM) for Mauritania energy shock analysis.

What this script does:
  1. Builds a "synthetic Mauritania" — a weighted combination of peer
     countries that best replicates Mauritania pre-shock (2015–2022)
  2. Post-shock (2023+), the gap between real and synthetic Mauritania
     = the causal effect of the Middle East energy crisis
  3. Placebo tests: run SCM on every peer country to validate significance
  4. Gap chart + placebo distribution + donor weights + predictor balance
  5. Exports results to Excel

Method reference: Abadie & Gardeazabal (2003), Abadie et al. (2010)
Implemented from scratch using scipy.optimize — no specialized package needed.

Run after: python analyze_mauritania.py
Dependencies: pip install pandas numpy matplotlib seaborn scipy statsmodels openpyxl
"""

import warnings
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
from pathlib import Path
from scipy.optimize import minimize, LinearConstraint
from scipy import stats

warnings.filterwarnings("ignore")

# ─── Config ──────────────────────────────────────────────────────────────────

OUTPUT_DIR = Path("output/synthetic_control")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

WB_FILE    = Path("output/wb_macro.csv")
PRICE_FILE = Path("output/prices.csv")

TREATED     = "MRT"           # Mauritania
SHOCK_YEAR  = 2023            # Oct 7 2023 → annual break
PRE_PERIOD  = list(range(2015, 2023))
POST_PERIOD = list(range(2023, 2025))
ALL_YEARS   = PRE_PERIOD + POST_PERIOD

# Donor pool — similar developing economies, not directly treated
DONOR_POOL  = ["SEN", "MLI", "CIV", "GHA", "MAR", "TUN", "CMR", "BFA"]

# Outcome variable to estimate treatment effect on
OUTCOME_VAR = "GDP_growth_pct"

# Predictor variables used to match pre-shock Mauritania
PREDICTORS  = [
    "GDP_growth_pct",
    "Inflation_CPI_pct",
    "Current_Account_pct_GDP",
    "Fuel_Imports_pct_merchandise",
    "External_Debt_pct_GNI",
]

PALETTE = {
    "treated":    "#C0392B",
    "synthetic":  "#2980B9",
    "placebo":    "#BDC3C7",
    "gap":        "#E67E22",
    "zero":       "#7F8C8D",
    "shock":      "#E74C3C",
    "bg":         "#FAFAFA",
}
DPI = 150


# ─── 1.  Data Loading & Synthetic Fallback ───────────────────────────────────

def load_panel() -> pd.DataFrame:
    if not WB_FILE.exists():
        print("⚠  wb_macro.csv not found — generating synthetic panel.")
        return _make_synthetic_panel()

    df = pd.read_csv(WB_FILE)
    df["year"] = df["year"].astype(int)
    df = df[df["year"].isin(ALL_YEARS)]

    # Add price data
    if PRICE_FILE.exists():
        prices = pd.read_csv(PRICE_FILE, index_col="date", parse_dates=True)
        ann    = prices.resample("YS").mean()
        ann["year"] = ann.index.year
        ann = ann.reset_index(drop=True)
        df = df.merge(ann[["year","WTI_Crude_Oil_USD"]].dropna(), on="year", how="left")

    return df


def _make_synthetic_panel() -> pd.DataFrame:
    """
    Plausible synthetic panel for MRT + donor pool.
    Mauritania shows a distinctive shock response post-2023.
    """
    np.random.seed(2024)
    years = ALL_YEARS

    country_profiles = {
        # code: (base_gdp, base_inf, base_ca, fuel_imp, ext_debt)
        "MRT": (4.5, 3.5,  -9.5, 20.0, 90.0),
        "SEN": (6.2, 2.8,  -8.0, 18.0, 65.0),
        "MLI": (5.0, 1.8,  -6.5, 15.0, 45.0),
        "CIV": (7.1, 2.2,  -3.0, 16.0, 48.0),
        "GHA": (5.5, 9.0, -10.0, 22.0, 72.0),
        "MAR": (3.8, 1.5,  -4.0, 19.0, 35.0),
        "TUN": (2.5, 6.0, -10.0, 17.0, 88.0),
        "CMR": (4.2, 2.3,  -4.5, 14.0, 40.0),
        "BFA": (5.0, 2.0,  -5.5, 12.0, 38.0),
    }

    country_names = {
        "MRT":"Mauritania","SEN":"Senegal","MLI":"Mali","CIV":"Côte d'Ivoire",
        "GHA":"Ghana","MAR":"Morocco","TUN":"Tunisia","CMR":"Cameroon","BFA":"Burkina Faso",
    }

    wti = {y: max(40, 55 + (y-2015)*3 + np.random.normal(0,5)) for y in years}
    wti[2020] = 40; wti[2021] = 68; wti[2022] = 95; wti[2023] = 78; wti[2024] = 82

    rows = []
    for code, (bg, bi, bc, bf, bd) in country_profiles.items():
        for year in years:
            shock     = -3.5 if (code == "MRT" and year >= SHOCK_YEAR) else 0
            covid     = -4.0 if year == 2020 else 0
            recovery  =  2.0 if year == 2021 else 0
            inf_shock =  3.0 if year >= 2022 else 0

            rows.append({
                "country_code":               code,
                "country_name":               country_names[code],
                "year":                       year,
                "GDP_growth_pct":             bg + shock + covid + recovery + np.random.normal(0, 0.6),
                "Inflation_CPI_pct":          bi + inf_shock + np.random.normal(0, 0.8),
                "Current_Account_pct_GDP":    bc + shock*0.4 + np.random.normal(0, 0.7),
                "Fuel_Imports_pct_merchandise": bf + (2 if year>=2022 else 0) + np.random.normal(0,0.8),
                "External_Debt_pct_GNI":      bd + (year-2015)*1.5 + np.random.normal(0, 1.5),
                "WTI_Crude_Oil_USD":          wti[year],
            })
    return pd.DataFrame(rows)


# ─── 2.  SCM Core ────────────────────────────────────────────────────────────

def pivot_outcome(df: pd.DataFrame, countries: list) -> pd.DataFrame:
    """Wide pivot: rows=year, cols=country_code for OUTCOME_VAR."""
    sub = df[df["country_code"].isin(countries)][
        ["year","country_code", OUTCOME_VAR]
    ].dropna()
    return sub.pivot(index="year", columns="country_code", values=OUTCOME_VAR)


def pivot_predictors(df: pd.DataFrame, countries: list,
                     pre_years: list) -> pd.DataFrame:
    """
    Predictor matrix: rows=country, cols=predictor × year averages.
    Only pre-shock data used for matching.
    """
    sub = df[df["country_code"].isin(countries) & df["year"].isin(pre_years)]
    avail_preds = [p for p in PREDICTORS if p in sub.columns]
    pred_means  = sub.groupby("country_code")[avail_preds].mean()
    return pred_means


def find_weights(treated: str, donors: list,
                 outcome_wide: pd.DataFrame,
                 pred_matrix: pd.DataFrame,
                 pre_years: list) -> np.ndarray:
    """
    Solve for donor weights W* that minimise:
        ||X_treated − X_donors @ W||²
    Subject to: W ≥ 0, sum(W) = 1
    where X contains both outcome pre-means and predictor means.
    """
    available_donors = [d for d in donors if d in outcome_wide.columns
                                           and d in pred_matrix.index]
    if len(available_donors) < 2:
        print("  ⚠  Not enough donors available — returning equal weights.")
        n = len(donors)
        return np.ones(n) / n, donors

    # Feature matrix: combine outcome (pre-period) + predictors
    out_pre = outcome_wide.loc[pre_years]
    treated_out  = out_pre[treated].values if treated in out_pre.columns else np.array([])
    donors_out   = out_pre[available_donors].values   # (T_pre × n_donors)

    treated_pred = pred_matrix.loc[treated].values if treated in pred_matrix.index else np.array([])
    donors_pred  = pred_matrix.loc[available_donors].values

    # X0 shape must be (n_donors × n_features) so X0.T @ w → (n_features,) == X1
    #   donors_out.T : (n_donors × T_pre)    donors as rows via transpose
    #   donors_pred  : (n_donors × n_preds)  donors already as rows
    #   hstack → (n_donors × (T_pre + n_preds))
    if len(treated_out) and len(treated_pred):
        X0 = np.hstack([donors_out.T, donors_pred])     # (n_donors × T_pre+n_preds)
        X1 = np.concatenate([treated_out, treated_pred])
    elif len(treated_out):
        X0 = donors_out.T                               # (n_donors × T_pre)
        X1 = treated_out
    else:
        X0 = donors_pred                                # (n_donors × n_preds)
        X1 = treated_pred

    # Normalise each feature COLUMN to [0,1] across donors to avoid scale dominance.
    # X0 is (n_donors x n_features) — axis=0 gives one min/max per feature column.
    col_min   = X0.min(axis=0, keepdims=True)                     # (1 x n_features)
    col_range = X0.max(axis=0, keepdims=True) - col_min           # (1 x n_features)
    col_range[col_range == 0] = 1                                  # avoid /0
    X0_n = (X0 - col_min) / col_range                             # (n_donors x n_features)
    X1_n = (X1 - col_min.flatten()) / col_range.flatten()         # (n_features,)

    n = len(available_donors)

    def objective(w):
        return np.sum((X1_n - X0_n.T @ w) ** 2)

    def gradient(w):
        return -2 * X0_n @ (X1_n - X0_n.T @ w)

    # Constraints: weights sum to 1, all ≥ 0
    constraints = {"type": "eq", "fun": lambda w: np.sum(w) - 1}
    bounds = [(0, 1)] * n
    w0     = np.ones(n) / n

    res = minimize(objective, w0, jac=gradient,
                   method="SLSQP", bounds=bounds, constraints=constraints,
                   options={"ftol":1e-10, "maxiter":1000})

    weights = res.x if res.success else w0
    weights = np.clip(weights, 0, 1)
    weights /= weights.sum()
    return weights, available_donors


def build_synthetic(outcome_wide: pd.DataFrame,
                    weights: np.ndarray,
                    donors: list) -> pd.Series:
    """Construct synthetic outcome as weighted sum of donor outcomes."""
    donor_df  = outcome_wide[donors]
    synthetic = donor_df.values @ weights
    return pd.Series(synthetic, index=outcome_wide.index, name="Synthetic")


# ─── 3.  Placebo Tests ───────────────────────────────────────────────────────

def run_placebo_tests(df: pd.DataFrame, outcome_wide: pd.DataFrame,
                      pred_matrix: pd.DataFrame) -> dict:
    """
    Run SCM on each donor country as if it were the treated unit.
    Returns dict of {country_code: gap_series}
    """
    all_countries = [TREATED] + DONOR_POOL
    placebo_gaps  = {}

    print("\n── Placebo Tests ──────────────────────────────────────────")
    for placebo_unit in all_countries:
        if placebo_unit not in outcome_wide.columns:
            continue
        placebo_donors = [c for c in all_countries
                          if c != placebo_unit and c in outcome_wide.columns]
        if len(placebo_donors) < 2:
            continue

        w, used_donors = find_weights(
            placebo_unit, placebo_donors,
            outcome_wide, pred_matrix, PRE_PERIOD
        )
        synth = build_synthetic(outcome_wide, w, used_donors)
        gap   = outcome_wide[placebo_unit] - synth
        placebo_gaps[placebo_unit] = gap

        pre_rmse  = np.sqrt(np.mean(gap.loc[PRE_PERIOD].dropna() ** 2))
        post_mean = gap.loc[[y for y in POST_PERIOD if y in gap.index]].mean()
        print(f"  {placebo_unit:<5}  pre-RMSE={pre_rmse:.3f}  "
              f"post-gap_mean={post_mean:+.3f}")

    return placebo_gaps


# ─── 4.  Charts ──────────────────────────────────────────────────────────────

def chart_synthetic_vs_actual(outcome_wide: pd.DataFrame,
                               synthetic: pd.Series, weights: np.ndarray,
                               donors: list):
    """Main SCM result chart: actual vs. synthetic Mauritania."""
    treated_series = outcome_wide[TREATED]

    fig, axes = plt.subplots(2, 1, figsize=(13, 10), facecolor=PALETTE["bg"])
    fig.suptitle(
        f"Synthetic Control Method — Mauritania\n"
        f"Outcome: {OUTCOME_VAR.replace('_',' ')}  |  Shock: Oct 7, {SHOCK_YEAR}",
        fontsize=13, fontweight="bold"
    )

    # Panel 1: Actual vs. Synthetic
    ax = axes[0]
    ax.set_facecolor(PALETTE["bg"])
    ax.plot(treated_series.index, treated_series.values,
            color=PALETTE["treated"], lw=2.5, marker="o", ms=5,
            label="Mauritania (actual)")
    ax.plot(synthetic.index, synthetic.values,
            color=PALETTE["synthetic"], lw=2.5, ls="--", marker="s", ms=4,
            label="Synthetic Mauritania")
    ax.axvline(SHOCK_YEAR - 0.5, color=PALETTE["shock"], lw=1.5, ls=":",
               alpha=0.9, label=f"Shock ({SHOCK_YEAR})")
    ax.fill_between(
        [y for y in outcome_wide.index if y >= SHOCK_YEAR],
        [treated_series.get(y, np.nan) for y in outcome_wide.index if y >= SHOCK_YEAR],
        [synthetic.get(y, np.nan)      for y in outcome_wide.index if y >= SHOCK_YEAR],
        alpha=0.25, color=PALETTE["gap"], label="Treatment effect (gap)"
    )
    ax.axvspan(min(PRE_PERIOD), SHOCK_YEAR - 0.5, alpha=0.05,
               color="blue", label="Pre-shock (matching period)")
    ax.set_title("Actual vs. Synthetic Mauritania", fontsize=10, fontweight="bold")
    ax.set_ylabel(OUTCOME_VAR.replace("_"," "), fontsize=9)
    ax.legend(fontsize=8.5, loc="best")
    ax.grid(axis="y", alpha=0.3)
    ax.tick_params(labelsize=9)

    # Panel 2: Gap (treatment effect)
    ax = axes[1]
    ax.set_facecolor(PALETTE["bg"])
    gap = treated_series - synthetic
    colours = [PALETTE["treated"] if v < 0 else PALETTE["synthetic"] for v in gap]
    bars = ax.bar(gap.index, gap.values, color=colours, alpha=0.75, width=0.6)
    ax.axhline(0, color="black", lw=0.8, alpha=0.5)
    ax.axvline(SHOCK_YEAR - 0.5, color=PALETTE["shock"], lw=1.5, ls=":",
               alpha=0.9, label=f"Shock ({SHOCK_YEAR})")

    # Label bars
    for bar, val in zip(bars, gap.values):
        if not np.isnan(val):
            ax.text(bar.get_x() + bar.get_width()/2, val + (0.1 if val >= 0 else -0.25),
                    f"{val:+.1f}", ha="center", va="bottom" if val >= 0 else "top",
                    fontsize=8, fontweight="bold",
                    color=PALETTE["treated"] if val < 0 else PALETTE["synthetic"])

    ax.set_title("Treatment Effect Gap (Actual − Synthetic)", fontsize=10, fontweight="bold")
    ax.set_ylabel(f"Δ {OUTCOME_VAR.replace('_',' ')}", fontsize=9)
    ax.legend(fontsize=8.5)
    ax.grid(axis="y", alpha=0.3)
    ax.tick_params(labelsize=9)

    plt.tight_layout()
    out = OUTPUT_DIR / "M_synthetic_control_main.png"
    fig.savefig(out, dpi=DPI, bbox_inches="tight")
    plt.close()
    print(f"\n✓ Chart M saved → {out}")


def chart_placebo_distribution(placebo_gaps: dict):
    """
    Placebo inference chart: Mauritania gap vs. distribution of all placebo gaps.
    The further Mauritania's post-shock gap lies from the placebo cloud, the more
    significant the treatment effect.
    """
    if not placebo_gaps:
        return

    fig, axes = plt.subplots(1, 2, figsize=(14, 6), facecolor=PALETTE["bg"])
    fig.suptitle("Placebo / Permutation Inference Tests",
                 fontsize=13, fontweight="bold")

    # ── Panel 1: Spaghetti plot ──
    ax = axes[0]
    ax.set_facecolor(PALETTE["bg"])

    for code, gap in placebo_gaps.items():
        if code == TREATED:
            continue
        pre_rmse = np.sqrt(np.mean(gap.loc[PRE_PERIOD].dropna() ** 2))
        # Only show placebos with reasonable pre-period fit (< 2× treated RMSE)
        mrt_pre_rmse = np.sqrt(np.mean(
            placebo_gaps[TREATED].loc[PRE_PERIOD].dropna() ** 2
        )) if TREATED in placebo_gaps else 1.0
        if pre_rmse > 2 * mrt_pre_rmse + 0.01:
            continue
        ax.plot(gap.index, gap.values,
                color=PALETTE["placebo"], lw=1.2, alpha=0.55)

    # Mauritania on top
    if TREATED in placebo_gaps:
        mrt_gap = placebo_gaps[TREATED]
        ax.plot(mrt_gap.index, mrt_gap.values,
                color=PALETTE["treated"], lw=2.8, label="Mauritania (treated)")

    ax.axhline(0, color="black", lw=0.8, alpha=0.5)
    ax.axvline(SHOCK_YEAR - 0.5, color=PALETTE["shock"], lw=1.5, ls=":",
               alpha=0.9, label=f"Shock ({SHOCK_YEAR})")
    ax.set_title("Gap Paths: Mauritania vs. Donor Placebos", fontsize=10, fontweight="bold")
    ax.set_ylabel(f"Actual − Synthetic ({OUTCOME_VAR.replace('_',' ')})", fontsize=9)
    ax.legend(fontsize=8.5)
    ax.grid(axis="y", alpha=0.3)

    grey_patch = mpatches.Patch(color=PALETTE["placebo"], alpha=0.6, label="Donor placebos")
    ax.legend(handles=[
        plt.Line2D([0],[0], color=PALETTE["treated"], lw=2.5, label="Mauritania"),
        grey_patch,
    ], fontsize=8.5)

    # ── Panel 2: Post-shock gap distribution ──
    ax = axes[1]
    ax.set_facecolor(PALETTE["bg"])

    post_gaps = {}
    for code, gap in placebo_gaps.items():
        post_vals = gap.loc[[y for y in POST_PERIOD if y in gap.index]]
        if not post_vals.empty:
            post_gaps[code] = post_vals.mean()

    if post_gaps:
        placebo_vals = [v for c, v in post_gaps.items() if c != TREATED]
        mrt_val      = post_gaps.get(TREATED, None)

        ax.hist(placebo_vals, bins=min(10, len(placebo_vals)),
                color=PALETTE["placebo"], alpha=0.75, edgecolor="white",
                label=f"Donor placebos (n={len(placebo_vals)})")

        if mrt_val is not None:
            ax.axvline(mrt_val, color=PALETTE["treated"], lw=2.5, ls="--",
                       label=f"Mauritania ({mrt_val:+.2f})")

            # One-sided p-value: rank of MRT in distribution
            all_vals = placebo_vals + [mrt_val]
            rank     = sorted(all_vals).index(mrt_val) + 1
            p_val    = rank / len(all_vals) if mrt_val < 0 else (len(all_vals) - rank + 1) / len(all_vals)
            ax.text(0.05, 0.92,
                    f"Mauritania post-shock gap: {mrt_val:+.2f}\n"
                    f"Permutation p-value: {p_val:.3f}\n"
                    f"Rank: {rank}/{len(all_vals)}",
                    transform=ax.transAxes, fontsize=9,
                    bbox=dict(boxstyle="round", fc="white", alpha=0.85, ec="grey"))

        ax.set_title(f"Post-Shock Gap Distribution\n({min(POST_PERIOD)}–{max(POST_PERIOD)})",
                     fontsize=10, fontweight="bold")
        ax.set_xlabel(f"Mean Post-Shock Gap ({OUTCOME_VAR.replace('_',' ')})", fontsize=9)
        ax.set_ylabel("Count", fontsize=9)
        ax.legend(fontsize=8.5)
        ax.grid(axis="y", alpha=0.3)
        ax.axvline(0, color="black", lw=0.7, alpha=0.4)

    plt.tight_layout()
    out = OUTPUT_DIR / "N_placebo_tests.png"
    fig.savefig(out, dpi=DPI, bbox_inches="tight")
    plt.close()
    print(f"✓ Chart N saved → {out}")


def chart_donor_weights(weights: np.ndarray, donors: list):
    """Bar chart of optimal donor weights."""
    weight_df = pd.DataFrame({"Donor": donors, "Weight": weights})
    weight_df = weight_df[weight_df["Weight"] > 0.005].sort_values("Weight", ascending=True)

    country_names = {
        "SEN":"Senegal","MLI":"Mali","CIV":"Côte d'Ivoire","GHA":"Ghana",
        "MAR":"Morocco","TUN":"Tunisia","CMR":"Cameroon","BFA":"Burkina Faso",
    }
    weight_df["Donor"] = weight_df["Donor"].map(lambda x: country_names.get(x, x))

    fig, ax = plt.subplots(figsize=(9, max(4, len(weight_df) * 0.55)),
                           facecolor=PALETTE["bg"])
    ax.set_facecolor(PALETTE["bg"])

    bars = ax.barh(weight_df["Donor"], weight_df["Weight"],
                   color=PALETTE["synthetic"], alpha=0.8, height=0.55)
    for bar, val in zip(bars, weight_df["Weight"]):
        ax.text(val + 0.005, bar.get_y() + bar.get_height()/2,
                f"{val:.3f}", va="center", fontsize=9, fontweight="bold")

    ax.set_xlim(0, weight_df["Weight"].max() * 1.25)
    ax.set_title("Synthetic Mauritania — Optimal Donor Weights\n"
                 "(Countries with weight > 0.5% shown)",
                 fontsize=11, fontweight="bold")
    ax.set_xlabel("Weight", fontsize=9)
    ax.grid(axis="x", alpha=0.3)
    ax.tick_params(labelsize=9)

    plt.tight_layout()
    out = OUTPUT_DIR / "O_donor_weights.png"
    fig.savefig(out, dpi=DPI, bbox_inches="tight")
    plt.close()
    print(f"✓ Chart O saved → {out}")


def chart_predictor_balance(df: pd.DataFrame, weights: np.ndarray, donors: list):
    """
    Table plot: how well does the synthetic Mauritania match
    the actual Mauritania on each predictor pre-shock?
    """
    pre_df = df[df["year"].isin(PRE_PERIOD)]
    avail_preds = [p for p in PREDICTORS if p in pre_df.columns]

    treated_means = (
        pre_df[pre_df["country_code"] == TREATED]
        .groupby("country_code")[avail_preds].mean()
    )
    donor_means = (
        pre_df[pre_df["country_code"].isin(donors)]
        .groupby("country_code")[avail_preds].mean()
    )

    if treated_means.empty or donor_means.empty:
        return

    treated_vec = treated_means.values.flatten()

    # Donors in same order as weights
    avail_donors = [d for d in donors if d in donor_means.index]
    w_aligned    = np.array([weights[donors.index(d)] for d in avail_donors])
    w_aligned   /= w_aligned.sum() if w_aligned.sum() > 0 else 1
    donor_matrix = donor_means.loc[avail_donors].values   # (n_donors × n_preds)
    synthetic_vec = w_aligned @ donor_matrix               # (n_preds,)

    balance_df = pd.DataFrame({
        "Predictor":        [p.replace("_"," ") for p in avail_preds],
        "Mauritania":       treated_vec,
        "Synthetic":        synthetic_vec,
        "Sample Avg (Donors)": donor_means.mean().values,
    })
    balance_df["Match Δ"] = (balance_df["Synthetic"] - balance_df["Mauritania"]).round(3)

    fig, ax = plt.subplots(figsize=(10, 5), facecolor=PALETTE["bg"])
    ax.set_facecolor(PALETTE["bg"])

    x       = np.arange(len(balance_df))
    width   = 0.28
    ax.bar(x - width,   balance_df["Mauritania"],          width, label="Mauritania (actual)",
           color=PALETTE["treated"],   alpha=0.85)
    ax.bar(x,           balance_df["Synthetic"],           width, label="Synthetic Mauritania",
           color=PALETTE["synthetic"], alpha=0.85)
    ax.bar(x + width,   balance_df["Sample Avg (Donors)"], width, label="Donor sample avg",
           color=PALETTE["placebo"],   alpha=0.85)

    ax.set_xticks(x)
    ax.set_xticklabels(balance_df["Predictor"], rotation=25, ha="right", fontsize=8.5)
    ax.set_title("Predictor Balance — Pre-Shock Period (2015–2022)\n"
                 "Synthetic should closely match Mauritania (red ≈ blue)",
                 fontsize=11, fontweight="bold")
    ax.set_ylabel("Mean Value (pre-shock period)", fontsize=9)
    ax.legend(fontsize=8.5)
    ax.grid(axis="y", alpha=0.3)

    # Print MSPE (mean squared predictor error)
    mspe = np.mean((balance_df["Mauritania"].values - balance_df["Synthetic"].values)**2)
    ax.text(0.99, 0.97, f"MSPE: {mspe:.4f}", transform=ax.transAxes,
            fontsize=8.5, ha="right", va="top",
            bbox=dict(boxstyle="round", fc="white", alpha=0.85, ec="grey"))

    plt.tight_layout()
    out = OUTPUT_DIR / "P_predictor_balance.png"
    fig.savefig(out, dpi=DPI, bbox_inches="tight")
    plt.close()
    print(f"✓ Chart P saved → {out}")


# ─── 5.  Export Excel ────────────────────────────────────────────────────────

def export_excel(treated_series, synthetic, placebo_gaps, weights, donors,
                 df: pd.DataFrame):
    out = OUTPUT_DIR / "synthetic_control_results.xlsx"

    gap = treated_series - synthetic
    mspe_pre  = np.mean(gap.loc[PRE_PERIOD].dropna() ** 2)
    mspe_post = np.mean(gap.loc[[y for y in POST_PERIOD if y in gap.index]].dropna() ** 2)

    with pd.ExcelWriter(out, engine="openpyxl") as writer:

        # Main results
        result_df = pd.DataFrame({
            "Year":              treated_series.index,
            "Mauritania_Actual": treated_series.values,
            "Synthetic":         [synthetic.get(y, np.nan) for y in treated_series.index],
            "Gap (Treatment Effect)": gap.values,
            "Period":            ["Pre-Shock" if y < SHOCK_YEAR else "Post-Shock"
                                  for y in treated_series.index],
        })
        result_df.to_excel(writer, sheet_name="SCM Results", index=False)

        # Donor weights
        pd.DataFrame({
            "Donor":  donors,
            "Weight": weights.round(4),
        }).to_excel(writer, sheet_name="Donor Weights", index=False)

        # Placebo gaps
        if placebo_gaps:
            placebo_df = pd.DataFrame(placebo_gaps)
            placebo_df.index.name = "year"
            placebo_df.reset_index().to_excel(writer, sheet_name="Placebo Gaps", index=False)

        # Summary stats
        pd.DataFrame([{
            "Outcome Variable":        OUTCOME_VAR,
            "Treated Unit":            TREATED,
            "Shock Year":              SHOCK_YEAR,
            "Pre-Period MSPE":         round(mspe_pre, 4),
            "Post-Period MSPE":        round(mspe_post, 4),
            "MSPE Ratio (Post/Pre)":   round(mspe_post / mspe_pre, 2) if mspe_pre > 0 else None,
            "Post-Shock Gap Mean":     round(gap.loc[[y for y in POST_PERIOD if y in gap.index]].mean(), 4),
            "Donors Used":             ", ".join(donors),
            "N Donors":                len(donors),
        }]).to_excel(writer, sheet_name="Summary", index=False)

    print(f"✓ Excel saved → {out}")


# ─── Main ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 62)
    print("  SYNTHETIC CONTROL METHOD — MAURITANIA ENERGY SHOCK")
    print("=" * 62)

    # 1. Load data
    df = load_panel()
    print(f"\n✓ Panel loaded: {df['country_code'].nunique()} countries "
          f"| {df['year'].min()}–{df['year'].max()}")

    # 2. Build outcome and predictor matrices
    all_units    = [TREATED] + [d for d in DONOR_POOL if d in df["country_code"].values]
    outcome_wide = pivot_outcome(df, all_units)
    pred_matrix  = pivot_predictors(df, all_units, PRE_PERIOD)

    print(f"✓ Outcome matrix: {outcome_wide.shape}  "
          f"| Predictors: {pred_matrix.shape}")

    # 3. Find optimal weights
    print("\n── Optimising donor weights ─────────────────────────────────")
    weights, used_donors = find_weights(
        TREATED, DONOR_POOL, outcome_wide, pred_matrix, PRE_PERIOD
    )
    print("\n  Donor weights:")
    for d, w in sorted(zip(used_donors, weights), key=lambda x: -x[1]):
        bar = "█" * int(w * 40)
        print(f"  {d:<5}  {w:.4f}  {bar}")

    # 4. Build synthetic series
    synthetic       = build_synthetic(outcome_wide, weights, used_donors)
    treated_series  = outcome_wide[TREATED]
    gap             = treated_series - synthetic
    pre_rmse        = np.sqrt(np.mean(gap.loc[PRE_PERIOD].dropna() ** 2))
    post_gap_mean   = gap.loc[[y for y in POST_PERIOD if y in gap.index]].mean()

    print(f"\n  Pre-shock RMSE:     {pre_rmse:.4f}  (lower = better match)")
    print(f"  Post-shock gap:     {post_gap_mean:+.4f} pp GDP growth")
    print(f"  MSPE ratio:         {(post_gap_mean**2 / max(pre_rmse**2, 1e-9)):.2f}x")

    # 5. Placebo tests
    placebo_gaps = run_placebo_tests(df, outcome_wide, pred_matrix)

    # 6. Charts
    print("\n── Generating charts ────────────────────────────────────────")
    chart_synthetic_vs_actual(outcome_wide, synthetic, weights, used_donors)
    chart_placebo_distribution(placebo_gaps)
    chart_donor_weights(weights, used_donors)
    chart_predictor_balance(df, weights, used_donors)

    # 7. Excel
    export_excel(treated_series, synthetic, placebo_gaps, weights, used_donors, df)

    print("\n" + "=" * 62)
    print("  DONE — all outputs in output/synthetic_control/")
    print("=" * 62)
    print("\nFiles generated:")
    for f in sorted(OUTPUT_DIR.iterdir()):
        print(f"  {f.name}")

    print(f"""
── How to read the results ──────────────────────────────────
  Chart M:  Main result — actual vs. synthetic Mauritania.
            The orange gap post-{SHOCK_YEAR} = estimated causal effect.

  Chart N:  Placebo test — Mauritania's gap (red) vs. all
            donor gaps (grey). If red is an outlier, the
            effect is statistically unusual / significant.

  Chart O:  Which countries make up synthetic Mauritania and
            at what weight. High weight = most similar.

  Chart P:  Predictor balance table. Blue ≈ Red = good match.
            MSPE printed on chart.

  Excel:    Full numerical results + placebo gap matrix for
            your own further analysis.
""")