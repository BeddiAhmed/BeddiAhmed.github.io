"""
analyze_mauritania.py
======================
Empirical analysis of the Middle East energy crisis impact on Mauritania.

Modules:
  1.  Load & merge prices + World Bank macro + COMTRADE trade data
  2.  Descriptive: Mauritania macro trends vs. peers
  3.  OLS Regression: oil/gas price shocks → GDP, trade balance, inflation
  4.  Before / After shock comparison (Oct 7 2023 as structural break)
  5.  Chow Test for structural break significance
  6.  Trade exposure: fuel imports as % of total, partner concentration
  7.  COMTRADE: top trading partners & commodity breakdown
  8.  Energy import cost shock estimation (price × volume)
  9.  Export charts as PNG + Excel summary

Run after: python collect_data.py  AND  python analyze_prices.py
Dependencies: pip install pandas numpy matplotlib seaborn scipy statsmodels openpyxl
"""

import warnings
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.dates as mdates
import seaborn as sns
from pathlib import Path
from scipy import stats
import statsmodels.api as sm
from statsmodels.stats.diagnostic import het_breuschpagan
from statsmodels.stats.stattools import durbin_watson

warnings.filterwarnings("ignore")

# ─── Config ──────────────────────────────────────────────────────────────────

OUTPUT_DIR   = Path("output/mauritania_analysis")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

PRICE_FILE   = Path("output/prices.csv")
WB_FILE      = Path("output/wb_macro.csv")
CT_IMP_FILE  = Path("output/comtrade_imports.csv")
CT_EXP_FILE  = Path("output/comtrade_exports.csv")
IMF_FILE     = Path("output/imf_weo.csv")

SHOCK_DATE   = 2023          # Oct 7 2023 → annual break year
PEER_CODES   = ["MRT", "SEN", "MLI", "CIV", "GHA", "NGA", "DZA", "MAR"]
MRT_CODE     = "MRT"

PALETTE = {
    "mrt":     "#C0392B",
    "peer":    "#95A5A6",
    "oil":     "#E67E22",
    "gas":     "#2980B9",
    "pos":     "#27AE60",
    "neg":     "#E74C3C",
    "neutral": "#7F8C8D",
    "bg":      "#FAFAFA",
}

DPI      = 150
FIGSIZE  = (13, 5)

# ─── 1.  Data Loaders ────────────────────────────────────────────────────────

def load_wb() -> pd.DataFrame:
    if not WB_FILE.exists():
        print("⚠  wb_macro.csv not found — generating synthetic World Bank data.")
        return _synthetic_wb()
    df = pd.read_csv(WB_FILE)
    df["year"] = df["year"].astype(int)
    return df

def load_prices_annual() -> pd.DataFrame:
    """Convert monthly prices to annual averages for merging with WB data."""
    if not PRICE_FILE.exists():
        print("⚠  prices.csv not found — generating synthetic prices.")
        return _synthetic_prices_annual()
    df = pd.read_csv(PRICE_FILE, index_col="date", parse_dates=True)
    ann = df.resample("YS").mean()
    ann["year"] = ann.index.year
    return ann.reset_index(drop=True)

def load_comtrade(flow: str = "imports") -> pd.DataFrame:
    fpath = CT_IMP_FILE if flow == "imports" else CT_EXP_FILE
    if not fpath.exists():
        print(f"⚠  comtrade_{flow}.csv not found — generating synthetic trade data.")
        return _synthetic_comtrade(flow)
    df = pd.read_csv(fpath)
    df["year"] = df["year"].astype(int)
    return df

def load_imf() -> pd.DataFrame:
    if not IMF_FILE.exists():
        return pd.DataFrame()
    df = pd.read_csv(IMF_FILE)
    df["year"] = df["year"].astype(int)
    return df


# ─── 2.  Synthetic Data Fallbacks ────────────────────────────────────────────

def _synthetic_wb() -> pd.DataFrame:
    """Synthetic but plausible Mauritania + peers macro panel 2015–2024."""
    np.random.seed(7)
    years    = list(range(2015, 2025))
    countries = {
        "MRT": "Mauritania",  "SEN": "Senegal",   "MLI": "Mali",
        "CIV": "Côte d'Ivoire", "GHA": "Ghana",  "NGA": "Nigeria",
        "DZA": "Algeria",     "MAR": "Morocco",
    }
    rows = []
    # Mauritania: iron ore + fish + nascent gas exporter; runs trade deficits
    mrt_gdp   = [3.5, 3.8, 4.1, 5.3, 5.6, -1.8, 2.4, 5.2, 4.8, 3.9]
    mrt_inf   = [0.5, 1.5, 2.3, 2.4, 2.3,  2.4, 3.5, 9.5,10.2, 7.1]
    mrt_cab   = [-9, -10, -12,-11, -9,  -7, -8, -14, -12, -10]
    mrt_fuel_imp = [18, 19, 21, 22, 20, 16, 18, 26, 24, 22]  # fuel % merch imports
    mrt_fuel_exp = [2,  2,  3,  4,  4,  3,  4,  6,  8,  9]   # gas exports ramping up

    for i, year in enumerate(years):
        for code, name in countries.items():
            noise = np.random.normal
            if code == "MRT":
                rows.append({"country_code": code, "country_name": name, "year": year,
                    "GDP_growth_pct":            mrt_gdp[i]   + noise(0, 0.3),
                    "Inflation_CPI_pct":         mrt_inf[i]   + noise(0, 0.5),
                    "Current_Account_pct_GDP":   mrt_cab[i]   + noise(0, 0.8),
                    "Imports_pct_GDP":           54 + noise(0, 3),
                    "Exports_pct_GDP":           44 + noise(0, 3),
                    "Fuel_Imports_pct_merchandise": mrt_fuel_imp[i] + noise(0, 1),
                    "Fuel_Exports_pct_merchandise": mrt_fuel_exp[i] + noise(0, 0.5),
                    "External_Debt_pct_GNI":    93 + i*2 + noise(0, 2),
                    "Official_Exchange_Rate_per_USD": 355 + i*8 + noise(0, 5),
                })
            else:
                # Simplified peer data
                base_gdp = {"SEN":6,"MLI":5,"CIV":7,"GHA":5,"NGA":3,"DZA":3,"MAR":4}
                rows.append({"country_code": code, "country_name": name, "year": year,
                    "GDP_growth_pct":            base_gdp.get(code,4) + noise(0,1.5)
                                                 + (-3 if year==2020 else 0),
                    "Inflation_CPI_pct":         5 + noise(0,2) + (3 if year>=2022 else 0),
                    "Current_Account_pct_GDP":   -5 + noise(0,2),
                    "Fuel_Imports_pct_merchandise": 20 + noise(0,3),
                    "Fuel_Exports_pct_merchandise": 5 + noise(0,2),
                    "External_Debt_pct_GNI":    70 + noise(0,5),
                    "Official_Exchange_Rate_per_USD": noise(500,50),
                })
    return pd.DataFrame(rows)

def _synthetic_prices_annual() -> pd.DataFrame:
    wti = [52, 54, 58, 65, 57, 40, 68, 95, 78, 82]
    return pd.DataFrame({
        "year": list(range(2015, 2025)),
        "WTI_Crude_Oil_USD": wti,
        "Brent_Crude_Oil_USD": [w+3 for w in wti],
        "EU_NatGas_USD": [6,5,5,8,5,3,16,35,14,12],
    })

def _synthetic_comtrade(flow: str) -> pd.DataFrame:
    np.random.seed(42)
    years = list(range(2018, 2025))
    partners = ["World","France","China","Spain","Japan","UAE","Senegal","EU"]
    rows = []
    for year in years:
        for partner in partners:
            rows.append({
                "year": year,
                "partnerDesc": partner,
                "cmdCode": "27",
                "cmdDesc": "Mineral fuels, oils",
                "trade_value_USD": np.random.randint(50_000_000, 400_000_000)
                                   * (1.4 if year >= 2022 else 1.0),
                "flowDesc": flow,
            })
    return pd.DataFrame(rows)


# ─── 3.  Merge Master Panel ───────────────────────────────────────────────────

def build_panel(wb: pd.DataFrame, prices: pd.DataFrame) -> pd.DataFrame:
    """Merge World Bank macro + annual commodity prices into one panel."""
    merged = wb.merge(prices, on="year", how="left")
    # Trade balance (exports - imports as % GDP)
    if "Exports_pct_GDP" in merged and "Imports_pct_GDP" in merged:
        merged["Trade_Balance_pct_GDP"] = (
            merged["Exports_pct_GDP"] - merged["Imports_pct_GDP"]
        )
    # Real exchange rate proxy: nominal FX adjusted by inflation differential
    if "Official_Exchange_Rate_per_USD" in merged and "Inflation_CPI_pct" in merged:
        merged["REER_proxy"] = (
            merged["Official_Exchange_Rate_per_USD"]
            / (1 + merged["Inflation_CPI_pct"] / 100)
        )
    return merged


# ─── 4.  OLS Regression ──────────────────────────────────────────────────────

def run_ols(panel: pd.DataFrame, dep_var: str, ind_vars: list,
            label: str, country: str = "MRT") -> dict:
    """
    Run OLS on Mauritania data.
    Returns dict with model, results, diagnostics.
    """
    df = panel[panel["country_code"] == country].copy()
    df = df.dropna(subset=[dep_var] + ind_vars)
    df = df.sort_values("year")

    if len(df) < 6:
        print(f"  ⚠  {label}: only {len(df)} observations — skipping.")
        return {}

    X = sm.add_constant(df[ind_vars])
    y = df[dep_var]
    model = sm.OLS(y, X).fit(cov_type="HC3")   # heteroskedasticity-robust SEs

    # Diagnostics
    dw   = durbin_watson(model.resid)
    _, bp_p, _, _ = het_breuschpagan(model.resid, model.model.exog)
    jb_stat, jb_p = stats.jarque_bera(model.resid)

    return {
        "label":    label,
        "model":    model,
        "y":        y,
        "X":        X,
        "df":       df,
        "n":        len(df),
        "r2":       model.rsquared,
        "r2_adj":   model.rsquared_adj,
        "dw":       dw,
        "bp_p":     bp_p,
        "jb_p":     jb_p,
    }


def run_all_regressions(panel: pd.DataFrame) -> list:
    """Run the core set of regressions for the article."""
    specs = [
        # (dep_var,                 ind_vars,                           label)
        ("GDP_growth_pct",
         ["WTI_Crude_Oil_USD", "Inflation_CPI_pct"],
         "GDP Growth ~ Oil Price + Inflation"),

        ("Trade_Balance_pct_GDP",
         ["WTI_Crude_Oil_USD", "EU_NatGas_USD"],
         "Trade Balance ~ Oil + Gas Prices"),

        ("Inflation_CPI_pct",
         ["WTI_Crude_Oil_USD", "EU_NatGas_USD"],
         "Inflation ~ Oil + Gas Prices"),

        ("Current_Account_pct_GDP",
         ["WTI_Crude_Oil_USD", "Fuel_Imports_pct_merchandise"],
         "Current Account ~ Oil Price + Fuel Import Share"),

        ("External_Debt_pct_GNI",
         ["WTI_Crude_Oil_USD", "Current_Account_pct_GDP"],
         "External Debt ~ Oil Price + Current Account"),
    ]

    results = []
    print("\n── OLS Regression Results (Mauritania) ──────────────────────────")
    for dep, ind, label in specs:
        avail_ind = [v for v in ind if v in panel.columns]
        if dep not in panel.columns or not avail_ind:
            print(f"  ⚠  Skipping '{label}' — columns missing")
            continue
        r = run_ols(panel, dep, avail_ind, label)
        if r:
            results.append(r)
            m = r["model"]
            print(f"\n  {label}")
            print(f"    N={r['n']}  R²={r['r2']:.3f}  Adj-R²={r['r2_adj']:.3f}"
                  f"  DW={r['dw']:.2f}  BP-p={r['bp_p']:.3f}")
            for var, coef, pval in zip(m.params.index, m.params, m.pvalues):
                sig = "***" if pval<0.01 else "**" if pval<0.05 else "*" if pval<0.1 else ""
                print(f"    {var:<35} β={coef:>8.4f}  p={pval:.3f} {sig}")
    return results


# ─── 5.  Chow Test — Structural Break ────────────────────────────────────────

def chow_test(panel: pd.DataFrame, dep_var: str, ind_var: str,
              break_year: int = SHOCK_DATE) -> dict:
    """
    Chow test: does the regression slope change before vs. after break_year?
    H0: no structural break (same coefficients in both sub-periods)
    """
    df = panel[panel["country_code"] == "MRT"].dropna(
        subset=[dep_var, ind_var]).sort_values("year")
    if len(df) < 8:
        return {}

    pre  = df[df["year"] <  break_year]
    post = df[df["year"] >= break_year]

    def sse(sub):
        X = sm.add_constant(sub[[ind_var]])
        m = sm.OLS(sub[dep_var], X).fit()
        return np.sum(m.resid ** 2), len(sub)

    sse_full, n  = sse(df)
    sse_pre,  n1 = sse(pre)
    sse_post, n2 = sse(post)

    k = 2   # constant + 1 regressor
    if (sse_pre + sse_post) == 0:
        return {}

    F = ((sse_full - (sse_pre + sse_post)) / k) / \
        ((sse_pre + sse_post) / (n - 2*k))
    p = 1 - stats.f.cdf(F, k, n - 2*k)

    return {"F": F, "p": p, "n_pre": n1, "n_post": n2,
            "dep_var": dep_var, "ind_var": ind_var, "break_year": break_year}


# ─── 6.  Before / After Comparison ───────────────────────────────────────────

def before_after_table(panel: pd.DataFrame) -> pd.DataFrame:
    """Mean of each indicator for Mauritania before vs. after Oct 7 shock."""
    mrt = panel[panel["country_code"] == "MRT"].copy()
    metrics = [
        "GDP_growth_pct", "Inflation_CPI_pct", "Current_Account_pct_GDP",
        "Trade_Balance_pct_GDP", "Fuel_Imports_pct_merchandise",
        "External_Debt_pct_GNI", "WTI_Crude_Oil_USD",
    ]
    rows = []
    for m in metrics:
        if m not in mrt.columns:
            continue
        pre_val  = mrt[mrt["year"] <  SHOCK_DATE][m].mean()
        post_val = mrt[mrt["year"] >= SHOCK_DATE][m].mean()
        delta    = post_val - pre_val
        pct_chg  = (delta / abs(pre_val) * 100) if pre_val != 0 else None
        rows.append({
            "Indicator":      m.replace("_", " "),
            "Pre-Shock Mean": round(pre_val,  2),
            "Post-Shock Mean":round(post_val, 2),
            "Change":         round(delta,    2),
            "% Change":       round(pct_chg, 1) if pct_chg else None,
        })
    df_ba = pd.DataFrame(rows)
    df_ba.to_csv(OUTPUT_DIR / "before_after.csv", index=False)
    print(f"\n✓ Before/After table → output/mauritania_analysis/before_after.csv")
    return df_ba


# ─── 7.  Charts ──────────────────────────────────────────────────────────────

def chart_macro_dashboard(panel: pd.DataFrame):
    """4-panel macro dashboard: GDP, inflation, current account, debt."""
    mrt   = panel[panel["country_code"] == "MRT"].sort_values("year")
    peers = panel[panel["country_code"].isin(PEER_CODES)].sort_values("year")

    metrics = [
        ("GDP_growth_pct",          "GDP Growth (%)",               PALETTE["mrt"]),
        ("Inflation_CPI_pct",       "Inflation — CPI (%)",          PALETTE["oil"]),
        ("Current_Account_pct_GDP", "Current Account (% GDP)",      PALETTE["gas"]),
        ("External_Debt_pct_GNI",   "External Debt (% GNI)",        "#8E44AD"),
    ]
    available = [(m,l,c) for m,l,c in metrics if m in panel.columns]

    fig, axes = plt.subplots(2, 2, figsize=(14, 9), facecolor=PALETTE["bg"])
    fig.suptitle("Mauritania — Macro Dashboard vs. Sub-Saharan Peers",
                 fontsize=14, fontweight="bold")
    axes = axes.flatten()

    for ax, (metric, label, colour) in zip(axes, available):
        ax.set_facecolor(PALETTE["bg"])

        # Peer band
        peer_grp = peers.groupby("year")[metric]
        peer_med = peer_grp.median()
        peer_lo  = peer_grp.quantile(0.25)
        peer_hi  = peer_grp.quantile(0.75)
        ax.fill_between(peer_lo.index, peer_lo, peer_hi,
                        color=PALETTE["peer"], alpha=0.25, label="Peer IQR")
        ax.plot(peer_med.index, peer_med, color=PALETTE["peer"],
                lw=1.2, ls="--", label="Peer Median")

        # Mauritania line
        ax.plot(mrt["year"], mrt[metric], color=colour,
                lw=2.5, marker="o", ms=4, label="Mauritania")

        # Shock marker
        ax.axvline(SHOCK_DATE, color=PALETTE["neg"], lw=1.2, ls=":",
                   alpha=0.8, label="Oct 7 Shock")
        ax.axvline(2022, color="#E67E22", lw=1, ls=":", alpha=0.6,
                   label="Ukraine War")

        ax.set_title(label, fontsize=10, fontweight="bold")
        ax.set_xlabel("Year", fontsize=8)
        ax.legend(fontsize=7.5, loc="best")
        ax.grid(axis="y", alpha=0.3)
        ax.tick_params(labelsize=8)

    plt.tight_layout()
    out = OUTPUT_DIR / "G_macro_dashboard.png"
    fig.savefig(out, dpi=DPI, bbox_inches="tight")
    plt.close()
    print(f"✓ Chart G saved → {out}")


def chart_oil_vs_outcomes(panel: pd.DataFrame):
    """Scatter: WTI oil price vs. key Mauritania outcomes with OLS line."""
    mrt = panel[panel["country_code"] == "MRT"].dropna(
        subset=["WTI_Crude_Oil_USD"]).sort_values("year")

    outcomes = [
        ("GDP_growth_pct",          "GDP Growth (%)",          PALETTE["mrt"]),
        ("Inflation_CPI_pct",       "Inflation (%)",           PALETTE["oil"]),
        ("Current_Account_pct_GDP", "Current Account (% GDP)", PALETTE["gas"]),
        ("Trade_Balance_pct_GDP",   "Trade Balance (% GDP)",   "#8E44AD"),
    ]
    available = [(o,l,c) for o,l,c in outcomes if o in mrt.columns]

    fig, axes = plt.subplots(1, len(available), figsize=(15, 5), facecolor=PALETTE["bg"])
    fig.suptitle("Mauritania — Oil Price vs. Economic Outcomes",
                 fontsize=13, fontweight="bold")
    if len(available) == 1:
        axes = [axes]

    for ax, (outcome, label, colour) in zip(axes, available):
        sub = mrt.dropna(subset=[outcome])
        x   = sub["WTI_Crude_Oil_USD"]
        y   = sub[outcome]

        ax.set_facecolor(PALETTE["bg"])
        ax.scatter(x, y, color=colour, s=60, zorder=3, alpha=0.85)

        # Label each point with year
        for _, row in sub.iterrows():
            ax.annotate(str(int(row["year"])),
                        (row["WTI_Crude_Oil_USD"], row[outcome]),
                        textcoords="offset points", xytext=(4, 3),
                        fontsize=7, color=PALETTE["neutral"])

        # OLS line
        if len(sub) >= 4:
            slope, intercept, r, p, _ = stats.linregress(x, y)
            x_line = np.linspace(x.min(), x.max(), 100)
            ax.plot(x_line, intercept + slope * x_line,
                    color="black", lw=1.5, ls="--", alpha=0.7)
            ax.text(0.05, 0.95,
                    f"β={slope:.3f}\nR²={r**2:.3f}\np={p:.3f}",
                    transform=ax.transAxes, fontsize=8, va="top",
                    bbox=dict(boxstyle="round", fc="white", alpha=0.8, ec="grey"))

        ax.set_xlabel("WTI Crude Oil (USD/bbl)", fontsize=9)
        ax.set_ylabel(label, fontsize=9)
        ax.set_title(label, fontsize=9, fontweight="bold")
        ax.grid(alpha=0.3)

    plt.tight_layout()
    out = OUTPUT_DIR / "H_oil_vs_outcomes.png"
    fig.savefig(out, dpi=DPI, bbox_inches="tight")
    plt.close()
    print(f"✓ Chart H saved → {out}")


def chart_regression_results(results: list):
    """Coefficient plot (forest plot) for all regression specs."""
    if not results:
        print("⚠  No regression results to plot — skipping chart I")
        return

    rows = []
    for r in results:
        m = r["model"]
        for var in m.params.index:
            if var == "const":
                continue
            rows.append({
                "spec":  r["label"],
                "var":   var.replace("_", " "),
                "coef":  m.params[var],
                "ci_lo": m.conf_int().loc[var, 0],
                "ci_hi": m.conf_int().loc[var, 1],
                "pval":  m.pvalues[var],
                "sig":   m.pvalues[var] < 0.1,
            })

    df_coef = pd.DataFrame(rows)
    if df_coef.empty:
        return

    fig, ax = plt.subplots(figsize=(12, max(5, len(df_coef) * 0.45)),
                           facecolor=PALETTE["bg"])
    ax.set_facecolor(PALETTE["bg"])

    colours = [PALETTE["mrt"] if s else PALETTE["peer"] for s in df_coef["sig"]]
    y_pos   = range(len(df_coef))

    ax.barh(list(y_pos), df_coef["coef"],
            xerr=[df_coef["coef"] - df_coef["ci_lo"],
                  df_coef["ci_hi"] - df_coef["coef"]],
            color=colours, alpha=0.8, capsize=4, height=0.6)
    ax.axvline(0, color="black", lw=1, alpha=0.6)
    ax.set_yticks(list(y_pos))
    ax.set_yticklabels(
        [f"{r['var']}\n({r['spec'][:35]})" for _, r in df_coef.iterrows()],
        fontsize=7.5
    )
    ax.set_xlabel("Coefficient (with 95% CI)", fontsize=9)
    ax.set_title("Regression Coefficients — Mauritania Energy Shock Analysis\n"
                 "Red = significant (p<0.1), Grey = not significant",
                 fontsize=11, fontweight="bold")
    ax.grid(axis="x", alpha=0.3)

    plt.tight_layout()
    out = OUTPUT_DIR / "I_regression_coefficients.png"
    fig.savefig(out, dpi=DPI, bbox_inches="tight")
    plt.close()
    print(f"✓ Chart I saved → {out}")


def chart_trade_flows(ct_imp: pd.DataFrame, ct_exp: pd.DataFrame):
    """Two-panel: top partners + fuel imports over time."""
    fig, axes = plt.subplots(1, 2, figsize=(14, 6), facecolor=PALETTE["bg"])
    fig.suptitle("Mauritania — Trade Flow Analysis", fontsize=13, fontweight="bold")

    # Panel 1: Top import partners (latest year)
    ax = axes[0]
    ax.set_facecolor(PALETTE["bg"])
    if not ct_imp.empty and "partnerDesc" in ct_imp.columns:
        latest = ct_imp["year"].max()
        top_partners = (
            ct_imp[ct_imp["year"] == latest]
            .groupby("partnerDesc")["trade_value_USD"]
            .sum()
            .sort_values(ascending=False)
            .head(10)
        )
        bars = ax.barh(range(len(top_partners)), top_partners.values / 1e6,
                       color=PALETTE["gas"], alpha=0.8)
        ax.set_yticks(range(len(top_partners)))
        ax.set_yticklabels(top_partners.index, fontsize=8)
        ax.set_xlabel("Import Value (USD millions)", fontsize=9)
        ax.set_title(f"Top 10 Import Partners ({latest})", fontsize=10, fontweight="bold")
        ax.grid(axis="x", alpha=0.3)

        # Label bars
        for bar, val in zip(bars, top_partners.values / 1e6):
            ax.text(val + 1, bar.get_y() + bar.get_height()/2,
                    f"${val:.0f}M", va="center", fontsize=7.5)

    # Panel 2: Fuel imports value over time
    ax = axes[1]
    ax.set_facecolor(PALETTE["bg"])
    if not ct_imp.empty and "cmdCode" in ct_imp.columns:
        fuel_imp = (
            ct_imp[ct_imp["cmdCode"].astype(str).str.startswith("27")]
            .groupby("year")["trade_value_USD"]
            .sum()
        )
        total_imp = ct_imp.groupby("year")["trade_value_USD"].sum()
        fuel_share = (fuel_imp / total_imp * 100).dropna()

        ax2 = ax.twinx()
        ax.bar(fuel_imp.index, fuel_imp.values / 1e6,
               color=PALETTE["oil"], alpha=0.6, label="Fuel Imports (USD M)")
        ax2.plot(fuel_share.index, fuel_share.values,
                 color=PALETTE["mrt"], lw=2.5, marker="o", ms=5,
                 label="Fuel as % of Total Imports")

        ax.axvline(2022, color=PALETTE["neutral"], lw=1, ls="--", alpha=0.6)
        ax.axvline(2023, color=PALETTE["mrt"],     lw=1, ls="--", alpha=0.6)
        ax.text(2022.05, ax.get_ylim()[1]*0.85, "Ukraine\nWar", fontsize=7,
                color=PALETTE["neutral"])
        ax.text(2023.05, ax.get_ylim()[1]*0.85, "Oct 7\nShock", fontsize=7,
                color=PALETTE["mrt"])

        ax.set_xlabel("Year", fontsize=9)
        ax.set_ylabel("Fuel Import Value (USD millions)", fontsize=9)
        ax2.set_ylabel("Fuel Imports (% of Total)", fontsize=9, color=PALETTE["mrt"])
        ax2.tick_params(axis="y", labelcolor=PALETTE["mrt"])
        ax.set_title("Mauritania Fuel Import Value & Share", fontsize=10, fontweight="bold")
        ax.legend(fontsize=8, loc="upper left")
        ax2.legend(fontsize=8, loc="upper right")
        ax.grid(axis="y", alpha=0.3)

    plt.tight_layout()
    out = OUTPUT_DIR / "J_trade_flows.png"
    fig.savefig(out, dpi=DPI, bbox_inches="tight")
    plt.close()
    print(f"✓ Chart J saved → {out}")


def chart_peer_comparison_bar(panel: pd.DataFrame):
    """Grouped bar: Mauritania vs. peers, pre vs. post shock."""
    metrics = [
        ("GDP_growth_pct",          "GDP Growth (%)"),
        ("Inflation_CPI_pct",       "Inflation (%)"),
        ("Fuel_Imports_pct_merchandise", "Fuel Imports\n(% Merch.)"),
    ]
    available = [(m,l) for m,l in metrics if m in panel.columns]
    if not available:
        return

    country_names = {
        "MRT":"Mauritania","SEN":"Senegal","MLI":"Mali",
        "CIV":"Côte d'Ivoire","GHA":"Ghana","NGA":"Nigeria",
        "DZA":"Algeria","MAR":"Morocco",
    }

    fig, axes = plt.subplots(1, len(available), figsize=(14, 6), facecolor=PALETTE["bg"])
    fig.suptitle("Peer Comparison — Pre-Shock (2019–2022) vs. Post-Shock (2023–2024)",
                 fontsize=12, fontweight="bold")
    if len(available) == 1:
        axes = [axes]

    for ax, (metric, label) in zip(axes, available):
        ax.set_facecolor(PALETTE["bg"])
        codes = [c for c in PEER_CODES if c in panel["country_code"].values]
        names = [country_names.get(c, c) for c in codes]

        pre_vals  = [panel[(panel["country_code"]==c) & (panel["year"]<SHOCK_DATE)][metric].mean()
                     for c in codes]
        post_vals = [panel[(panel["country_code"]==c) & (panel["year"]>=SHOCK_DATE)][metric].mean()
                     for c in codes]

        x    = np.arange(len(codes))
        w    = 0.38
        bars1 = ax.bar(x - w/2, pre_vals,  w, label="Pre-Shock",
                       color=PALETTE["gas"], alpha=0.8)
        bars2 = ax.bar(x + w/2, post_vals, w, label="Post-Shock",
                       color=PALETTE["mrt"], alpha=0.8)

        # Highlight Mauritania
        mrt_idx = codes.index("MRT") if "MRT" in codes else None
        if mrt_idx is not None:
            for b in [bars1[mrt_idx], bars2[mrt_idx]]:
                b.set_edgecolor("black")
                b.set_linewidth(2)

        ax.set_xticks(x)
        ax.set_xticklabels(names, rotation=35, ha="right", fontsize=8)
        ax.set_title(label, fontsize=10, fontweight="bold")
        ax.legend(fontsize=8)
        ax.grid(axis="y", alpha=0.3)
        ax.axhline(0, color="black", lw=0.6, alpha=0.5)

    plt.tight_layout()
    out = OUTPUT_DIR / "K_peer_comparison.png"
    fig.savefig(out, dpi=DPI, bbox_inches="tight")
    plt.close()
    print(f"✓ Chart K saved → {out}")


def chart_energy_import_cost(panel: pd.DataFrame):
    """
    Estimate the additional annual cost Mauritania paid for fuel imports
    due to the price shock.  Counterfactual: what if prices stayed at 2019 levels?
    """
    mrt = panel[panel["country_code"] == "MRT"].sort_values("year").copy()
    if "WTI_Crude_Oil_USD" not in mrt.columns or "Fuel_Imports_pct_merchandise" not in mrt.columns:
        return
    if "Imports_pct_GDP" not in mrt.columns:
        return

    # Rough estimate: fuel_import_value ≈ fuel_share × total_imports
    # Total imports = imports_pct_gdp × GDP (proxied by index)
    # GDP proxy: start from 100 and grow by GDP_growth_pct each year
    mrt = mrt.dropna(subset=["GDP_growth_pct","WTI_Crude_Oil_USD"])
    gdp_index = [100]
    for g in mrt["GDP_growth_pct"].iloc[1:]:
        gdp_index.append(gdp_index[-1] * (1 + g/100))
    mrt["gdp_index"] = gdp_index

    if "Fuel_Imports_pct_merchandise" in mrt.columns:
        mrt["fuel_cost_index"] = (
            mrt["Fuel_Imports_pct_merchandise"] / 100
            * mrt["gdp_index"]
        )
        # Counterfactual: freeze price at 2019/2020 level
        base_price = mrt[mrt["year"] <= 2020]["WTI_Crude_Oil_USD"].mean()
        mrt["price_ratio"] = mrt["WTI_Crude_Oil_USD"] / base_price
        mrt["counterfactual_fuel_cost"] = mrt["fuel_cost_index"] / mrt["price_ratio"]
        mrt["excess_cost"]              = mrt["fuel_cost_index"] - mrt["counterfactual_fuel_cost"]

        fig, ax = plt.subplots(figsize=FIGSIZE, facecolor=PALETTE["bg"])
        ax.set_facecolor(PALETTE["bg"])

        ax.fill_between(mrt["year"], mrt["fuel_cost_index"],
                        mrt["counterfactual_fuel_cost"],
                        where=(mrt["fuel_cost_index"] > mrt["counterfactual_fuel_cost"]),
                        interpolate=True, alpha=0.4, color=PALETTE["mrt"],
                        label="Energy price shock premium")
        ax.plot(mrt["year"], mrt["fuel_cost_index"],
                color=PALETTE["mrt"], lw=2.5, marker="o", ms=4, label="Actual fuel cost index")
        ax.plot(mrt["year"], mrt["counterfactual_fuel_cost"],
                color=PALETTE["gas"], lw=2, ls="--", marker="s", ms=4,
                label="Counterfactual (2019 price baseline)")

        ax.axvline(2022,        color=PALETTE["neutral"], lw=1, ls=":", alpha=0.7)
        ax.axvline(SHOCK_DATE,  color=PALETTE["neg"],     lw=1, ls=":", alpha=0.7)
        ax.text(2022.05, ax.get_ylim()[1]*0.95, "Ukraine", fontsize=7.5,
                color=PALETTE["neutral"])
        ax.text(SHOCK_DATE+0.05, ax.get_ylim()[1]*0.95, "Oct 7", fontsize=7.5,
                color=PALETTE["neg"])

        ax.set_title("Mauritania — Energy Import Cost Shock Estimation\n"
                     "(Relative index, base=100 in first year)",
                     fontsize=11, fontweight="bold")
        ax.set_xlabel("Year", fontsize=9)
        ax.set_ylabel("Fuel Import Cost Index", fontsize=9)
        ax.legend(fontsize=9)
        ax.grid(axis="y", alpha=0.3)

        plt.tight_layout()
        out = OUTPUT_DIR / "L_energy_cost_shock.png"
        fig.savefig(out, dpi=DPI, bbox_inches="tight")
        plt.close()
        print(f"✓ Chart L saved → {out}")


# ─── 8.  Excel Summary ───────────────────────────────────────────────────────

def export_results_excel(panel: pd.DataFrame, results: list,
                         ba_table: pd.DataFrame, chow_results: list):
    out = OUTPUT_DIR / "mauritania_analysis.xlsx"
    with pd.ExcelWriter(out, engine="openpyxl") as writer:

        # Full panel
        panel.to_excel(writer, sheet_name="Panel Data", index=False)

        # Mauritania only
        mrt = panel[panel["country_code"] == "MRT"]
        mrt.to_excel(writer, sheet_name="Mauritania", index=False)

        # Before/After
        ba_table.to_excel(writer, sheet_name="Before-After Shock", index=False)

        # Regression summaries
        reg_rows = []
        for r in results:
            if not r:
                continue
            m = r["model"]
            for var in m.params.index:
                reg_rows.append({
                    "Specification":  r["label"],
                    "Variable":       var,
                    "Coefficient":    round(m.params[var], 4),
                    "Std Error":      round(m.bse[var], 4),
                    "t-stat":         round(m.tvalues[var], 3),
                    "p-value":        round(m.pvalues[var], 4),
                    "CI Lower":       round(m.conf_int().loc[var, 0], 4),
                    "CI Upper":       round(m.conf_int().loc[var, 1], 4),
                    "R-squared":      round(r["r2"], 4),
                    "Adj R-squared":  round(r["r2_adj"], 4),
                    "N":              r["n"],
                    "Durbin-Watson":  round(r["dw"], 3),
                    "BP het. p-val":  round(r["bp_p"], 4),
                })
        if reg_rows:
            pd.DataFrame(reg_rows).to_excel(
                writer, sheet_name="Regression Results", index=False)

        # Chow tests
        if chow_results:
            pd.DataFrame(chow_results).to_excel(
                writer, sheet_name="Chow Tests", index=False)

    print(f"✓ Excel report saved → {out}")


# ─── Main ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 60)
    print("  MAURITANIA ENERGY SHOCK — EMPIRICAL ANALYSIS")
    print("=" * 60)

    # Load
    wb      = load_wb()
    prices  = load_prices_annual()
    ct_imp  = load_comtrade("imports")
    ct_exp  = load_comtrade("exports")

    # Build merged panel
    panel   = build_panel(wb, prices)
    print(f"\n✓ Panel: {len(panel)} rows × {len(panel.columns)} cols"
          f"  |  years {panel['year'].min()}–{panel['year'].max()}"
          f"  |  countries: {panel['country_code'].nunique()}")

    # Regressions
    results = run_all_regressions(panel)

    # Structural break tests
    print("\n── Chow Structural Break Tests ─────────────────────────────")
    chow_results = []
    for dep, ind in [
        ("GDP_growth_pct",          "WTI_Crude_Oil_USD"),
        ("Inflation_CPI_pct",       "WTI_Crude_Oil_USD"),
        ("Current_Account_pct_GDP", "WTI_Crude_Oil_USD"),
    ]:
        if dep in panel.columns and ind in panel.columns:
            c = chow_test(panel, dep, ind, SHOCK_DATE)
            if c:
                chow_results.append(c)
                sig = "✓ BREAK DETECTED" if c["p"] < 0.1 else "– not significant"
                print(f"  {dep:<32} F={c['F']:.3f}  p={c['p']:.3f}  {sig}")

    # Before/After table
    ba_table = before_after_table(panel)
    print("\nBefore / After Summary (Mauritania):")
    print(ba_table.to_string(index=False))

    # Charts
    print(f"\nGenerating charts → {OUTPUT_DIR}/\n")
    chart_macro_dashboard(panel)
    chart_oil_vs_outcomes(panel)
    chart_regression_results(results)
    chart_trade_flows(ct_imp, ct_exp)
    chart_peer_comparison_bar(panel)
    chart_energy_import_cost(panel)

    # Excel
    export_results_excel(panel, results, ba_table, chow_results)

    print("\n" + "=" * 60)
    print("  DONE — all outputs in output/mauritania_analysis/")
    print("=" * 60)
    print("\nFiles generated:")
    for f in sorted(OUTPUT_DIR.iterdir()):
        print(f"  {f.name}")
    print("\nNext step: python synthetic_control.py")