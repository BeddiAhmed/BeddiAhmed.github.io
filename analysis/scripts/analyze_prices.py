"""
analyze_prices.py
==================
Commodity price analysis for:
"Middle East Energy Crisis — Impact on the Global and Mauritanian Economy"

What this script does:
  1. Load & clean prices.csv from the data pipeline
  2. Compute price returns, volatility, and z-score shock detection
  3. Annotate key geopolitical events on the price timeline
  4. Rolling correlations between oil/gas and macro proxies
  5. Regime analysis (pre-war / escalation / current)
  6. Export charts as PNG + an Excel summary

Run after: python collect_data.py
Dependencies: pip install pandas numpy matplotlib seaborn scipy openpyxl
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
from scipy.signal import find_peaks

warnings.filterwarnings("ignore")

# ─── Config ──────────────────────────────────────────────────────────────────

INPUT_FILE  = Path("output/prices.csv")
OUTPUT_DIR  = Path("output/price_analysis")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Colour palette (professional / publication-grade)
PALETTE = {
    "oil":     "#C0392B",    # deep red
    "gas":     "#2980B9",    # blue
    "macro":   "#27AE60",    # green
    "shock":   "#E67E22",    # orange
    "neutral": "#7F8C8D",    # grey
    "bg":      "#FAFAFA",
}

FIGSIZE_WIDE  = (14, 5)
FIGSIZE_PANEL = (14, 10)
DPI           = 150

# ─── Key Geopolitical Events ─────────────────────────────────────────────────
# Each entry: (date_str, short_label, vertical_position_hint)
EVENTS = [
    ("2020-03-01", "COVID\nDemand\nCollapse",   "low"),
    ("2021-07-01", "OPEC+\nOutput Cuts",         "mid"),
    ("2022-02-24", "Russia–Ukraine\nInvasion",   "high"),
    ("2022-06-01", "EU Energy\nSanctions",        "mid"),
    ("2023-10-07", "Hamas Attack\n(Oct 7)",       "high"),
    ("2024-01-12", "Red Sea\nAttacks Escalate",   "mid"),
    ("2024-04-01", "Iran–Israel\nExchange",       "high"),
    ("2024-10-01", "Wider ME\nEscalation",        "high"),
]

# ─── 1. Load & Clean ──────────────────────────────────────────────────────────

def load_prices() -> pd.DataFrame:
    """Load prices.csv; generate synthetic data if file not yet produced."""
    if not INPUT_FILE.exists():
        print(f"⚠  {INPUT_FILE} not found — generating synthetic demo data.")
        print("   Run collect_data.py first for real figures.\n")
        return _make_synthetic_prices()

    df = pd.read_csv(INPUT_FILE, index_col="date", parse_dates=True)
    df = df.sort_index()
    df = df[df.index >= "2020-01-01"]

    # Drop columns that are >60% NaN
    df = df.dropna(axis=1, thresh=int(0.4 * len(df)))
    df = df.ffill().bfill()
    print(f"✓ Loaded prices.csv — {len(df)} months, {len(df.columns)} series")
    return df


def _make_synthetic_prices() -> pd.DataFrame:
    """
    Synthetic price data that roughly mirrors real-world dynamics.
    Useful for developing/testing analysis before FRED key is set.
    """
    np.random.seed(42)
    dates = pd.date_range("2020-01-01", periods=60, freq="MS")
    n = len(dates)

    # WTI: COVID crash → recovery → Ukraine spike → ME escalation
    wti_base = np.array([
        55, 25, 20, 18, 20, 35, 40, 42, 45, 48, 52, 55,   # 2020
        56, 60, 62, 63, 65, 67, 70, 68, 72, 75, 78, 72,   # 2021
        80, 88, 95, 105, 108, 112, 105, 98, 92, 85, 88, 78, # 2022
        76, 79, 75, 80, 72, 68, 74, 80, 84, 88, 75, 72,   # 2023
        74, 78, 80, 82, 85, 88, 90, 92, 88, 85, 82, 80,   # 2024+
    ])[:n]
    wti = wti_base + np.random.normal(0, 2, n)

    brent  = wti + np.random.normal(3, 1, n)
    henry  = 2.2 + 0.03 * (wti - 50) + np.random.normal(0, 0.4, n)
    eu_gas = 10 + 0.08 * (wti - 50) + np.random.normal(0, 5, n)

    # Spike EU gas on Ukraine invasion
    eu_gas[25:35] += np.array([20, 35, 50, 60, 55, 45, 35, 25, 20, 15])
    eu_gas = np.clip(eu_gas, 0, None)

    gasoline   = 2.5 + wti * 0.025 + np.random.normal(0, 0.05, n)
    heat_oil   = 1.8 + wti * 0.04  + np.random.normal(0, 0.04, n)
    dxy        = 96 + np.random.normal(0, 3, n)
    cpi        = np.linspace(260, 315, n) + np.random.normal(0, 1, n)
    vix        = 18 + np.random.normal(0, 5, n)
    vix[2:5]  += [15, 20, 12]    # COVID
    vix[24:27] += [8, 12, 8]     # Ukraine

    df = pd.DataFrame({
        "WTI_Crude_Oil_USD":    wti,
        "Brent_Crude_Oil_USD":  brent,
        "Henry_Hub_NatGas_USD": henry,
        "EU_NatGas_USD":        eu_gas,
        "Gasoline_USD_per_Gallon": gasoline,
        "Heating_Oil_USD":      heat_oil,
        "USD_Index_DXY":        dxy,
        "Global_CPI_Proxy":     cpi,
        "VIX_Volatility":       vix,
    }, index=dates)
    df.index.name = "date"
    return df


# ─── 2. Derived Series ───────────────────────────────────────────────────────

def compute_derived(df: pd.DataFrame) -> pd.DataFrame:
    """Add returns, volatility, z-scores, and composite indices."""
    d = df.copy()

    for col in d.columns:
        d[f"{col}_pct"] = d[col].pct_change() * 100

    # 12-month rolling volatility (std of monthly returns)
    for col in ["WTI_Crude_Oil_USD", "Brent_Crude_Oil_USD",
                "EU_NatGas_USD", "Henry_Hub_NatGas_USD"]:
        if col in d.columns:
            ret_col = f"{col}_pct"
            d[f"{col}_vol12"] = d[ret_col].rolling(12).std()

    # Z-score for shock detection (24-month rolling window)
    for col in ["WTI_Crude_Oil_USD", "EU_NatGas_USD"]:
        if col in d.columns:
            roll_mean = d[col].rolling(24).mean()
            roll_std  = d[col].rolling(24).std()
            d[f"{col}_zscore"] = (d[col] - roll_mean) / roll_std

    # Composite "Energy Stress Index" — avg z-score across oil + gas
    z_cols = [c for c in d.columns if c.endswith("_zscore")]
    if z_cols:
        d["Energy_Stress_Index"] = d[z_cols].mean(axis=1)

    # Indexed price levels (Jan 2020 = 100)
    base = df[df.index == "2020-01-01"]
    if len(base):
        for col in df.columns:
            base_val = base[col].values[0]
            if base_val and base_val != 0:
                d[f"{col}_idx"] = (d[col] / base_val) * 100

    return d


# ─── 3. Regime Classification ─────────────────────────────────────────────────

REGIMES = [
    ("Pre-COVID Baseline",        "2020-01-01", "2020-02-28", "#D5E8D4"),
    ("COVID Demand Collapse",     "2020-03-01", "2020-12-31", "#F8CECC"),
    ("Recovery & Tightening",     "2021-01-01", "2022-01-31", "#DAE8FC"),
    ("Ukraine War Shock",         "2022-02-01", "2023-09-30", "#FFE6CC"),
    ("Middle East Escalation",    "2023-10-01", "2024-06-30", "#E1D5E7"),
    ("Sustained Crisis",          "2024-07-01", "2030-12-31", "#FFF2CC"),
]

def add_regime_shading(ax, alpha=0.25):
    """Shade axis background by geopolitical regime."""
    for label, start, end, colour in REGIMES:
        ax.axvspan(pd.Timestamp(start), pd.Timestamp(end),
                   color=colour, alpha=alpha, zorder=0)


def add_event_lines(ax, df: pd.DataFrame, y_col: str = None):
    """Add vertical dashed lines for key events."""
    ymin, ymax = ax.get_ylim()
    y_range = ymax - ymin

    vpos_map = {"low": 0.10, "mid": 0.50, "high": 0.85}

    for date_str, label, vpos in EVENTS:
        dt = pd.Timestamp(date_str)
        if dt < df.index.min() or dt > df.index.max():
            continue
        ax.axvline(dt, color=PALETTE["shock"], lw=0.9, ls="--", alpha=0.7, zorder=2)
        ax.text(dt, ymin + y_range * vpos_map[vpos], label,
                fontsize=6.5, color=PALETTE["shock"], ha="left", va="bottom",
                rotation=0, bbox=dict(boxstyle="round,pad=0.2", fc="white", alpha=0.7, ec="none"))


# ─── 4. Chart A — Price Levels Timeline ──────────────────────────────────────

def chart_price_timeline(df: pd.DataFrame):
    fig, axes = plt.subplots(3, 1, figsize=(14, 11), facecolor=PALETTE["bg"])
    fig.suptitle("Global Energy Price Timeline (2020–Present)",
                 fontsize=15, fontweight="bold", y=0.98)

    # --- Panel 1: Crude Oil ---
    ax = axes[0]
    ax.set_facecolor(PALETTE["bg"])
    if "WTI_Crude_Oil_USD" in df.columns:
        ax.plot(df.index, df["WTI_Crude_Oil_USD"], color=PALETTE["oil"],
                lw=2, label="WTI Crude (USD/bbl)")
    if "Brent_Crude_Oil_USD" in df.columns:
        ax.plot(df.index, df["Brent_Crude_Oil_USD"], color="#E74C3C",
                lw=1.5, ls="--", label="Brent Crude (USD/bbl)", alpha=0.8)
    add_regime_shading(ax)
    ax.set_ylabel("USD per barrel", fontsize=9)
    ax.set_title("Crude Oil Prices", fontsize=10, fontweight="bold")
    ax.legend(fontsize=8, loc="upper left")
    ax.grid(axis="y", alpha=0.3)
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
    add_event_lines(ax, df)

    # --- Panel 2: Natural Gas ---
    ax = axes[1]
    ax.set_facecolor(PALETTE["bg"])
    if "EU_NatGas_USD" in df.columns:
        ax.plot(df.index, df["EU_NatGas_USD"], color=PALETTE["gas"],
                lw=2, label="EU Natural Gas (USD/MMBtu)")
    if "Henry_Hub_NatGas_USD" in df.columns:
        ax2 = ax.twinx()
        ax2.plot(df.index, df["Henry_Hub_NatGas_USD"], color="#8E44AD",
                 lw=1.5, ls=":", label="Henry Hub (USD/MMBtu)", alpha=0.85)
        ax2.set_ylabel("Henry Hub (USD/MMBtu)", fontsize=8, color="#8E44AD")
        ax2.tick_params(axis="y", labelcolor="#8E44AD")
        ax2.legend(fontsize=8, loc="upper right")
    add_regime_shading(ax)
    ax.set_ylabel("EU Gas (USD/MMBtu)", fontsize=9)
    ax.set_title("Natural Gas Prices — EU vs. Henry Hub", fontsize=10, fontweight="bold")
    ax.legend(fontsize=8, loc="upper left")
    ax.grid(axis="y", alpha=0.3)
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
    add_event_lines(ax, df)

    # --- Panel 3: Market Stress (VIX + DXY) ---
    ax = axes[2]
    ax.set_facecolor(PALETTE["bg"])
    if "VIX_Volatility" in df.columns:
        ax.fill_between(df.index, df["VIX_Volatility"], alpha=0.4,
                        color=PALETTE["shock"], label="VIX (market fear)")
        ax.plot(df.index, df["VIX_Volatility"], color=PALETTE["shock"], lw=1.5)
    if "USD_Index_DXY" in df.columns:
        ax2 = ax.twinx()
        ax2.plot(df.index, df["USD_Index_DXY"], color=PALETTE["macro"],
                 lw=1.8, label="USD Index (DXY)", alpha=0.9)
        ax2.set_ylabel("DXY Index", fontsize=8, color=PALETTE["macro"])
        ax2.tick_params(axis="y", labelcolor=PALETTE["macro"])
        ax2.legend(fontsize=8, loc="lower right")
    add_regime_shading(ax)
    ax.set_ylabel("VIX", fontsize=9)
    ax.set_title("Market Stress Indicators — VIX & USD Strength", fontsize=10, fontweight="bold")
    ax.legend(fontsize=8, loc="upper left")
    ax.grid(axis="y", alpha=0.3)
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
    add_event_lines(ax, df)

    for ax in axes:
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=30, ha="right", fontsize=8)

    # Regime legend
    patches = [mpatches.Patch(color=c, alpha=0.5, label=l)
               for l, s, e, c in REGIMES]
    fig.legend(handles=patches, loc="lower center", ncol=3,
               fontsize=7.5, title="Geopolitical Regimes", title_fontsize=8,
               bbox_to_anchor=(0.5, 0.01), frameon=True)

    plt.tight_layout(rect=[0, 0.06, 1, 0.97])
    out = OUTPUT_DIR / "A_price_timeline.png"
    fig.savefig(out, dpi=DPI, bbox_inches="tight")
    plt.close()
    print(f"✓ Chart A saved → {out}")


# ─── 5. Chart B — Indexed Prices (Base 100 = Jan 2020) ───────────────────────

def chart_indexed_prices(df: pd.DataFrame):
    idx_cols = {
        "WTI_Crude_Oil_USD_idx":     ("WTI Crude",    PALETTE["oil"],  "-"),
        "Brent_Crude_Oil_USD_idx":   ("Brent Crude",  "#E74C3C",       "--"),
        "EU_NatGas_USD_idx":         ("EU Gas",        PALETTE["gas"],  "-"),
        "Henry_Hub_NatGas_USD_idx":  ("Henry Hub Gas","#8E44AD",       "--"),
        "Global_CPI_Proxy_idx":      ("Global CPI",   PALETTE["macro"],":"),
    }
    available = {k: v for k, v in idx_cols.items() if k in df.columns}
    if not available:
        print("⚠  No indexed columns found — skipping chart B")
        return

    fig, ax = plt.subplots(figsize=FIGSIZE_WIDE, facecolor=PALETTE["bg"])
    ax.set_facecolor(PALETTE["bg"])

    for col, (label, colour, ls) in available.items():
        ax.plot(df.index, df[col], label=label, color=colour, lw=2, ls=ls)

    ax.axhline(100, color=PALETTE["neutral"], lw=0.8, ls=":", alpha=0.6,
               label="Jan 2020 baseline")
    add_regime_shading(ax)

    ax.set_title("Energy Price Index (Jan 2020 = 100)", fontsize=13, fontweight="bold")
    ax.set_ylabel("Index (Jan 2020 = 100)", fontsize=10)
    ax.legend(fontsize=9, loc="upper left", ncol=2)
    ax.grid(axis="y", alpha=0.3)
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
    plt.setp(ax.xaxis.get_majorticklabels(), rotation=30, ha="right", fontsize=8)
    add_event_lines(ax, df)

    plt.tight_layout()
    out = OUTPUT_DIR / "B_indexed_prices.png"
    fig.savefig(out, dpi=DPI, bbox_inches="tight")
    plt.close()
    print(f"✓ Chart B saved → {out}")


# ─── 6. Chart C — Rolling Correlations ──────────────────────────────────────

def chart_rolling_correlations(df: pd.DataFrame, window: int = 12):
    """Rolling 12-month correlation: WTI vs. other energy series and macro proxies."""
    anchor = "WTI_Crude_Oil_USD"
    if anchor not in df.columns:
        print("⚠  WTI column not found — skipping rolling correlations")
        return

    targets = {
        "EU_NatGas_USD":          ("WTI vs EU Gas",        PALETTE["gas"]),
        "Henry_Hub_NatGas_USD":   ("WTI vs Henry Hub Gas", "#8E44AD"),
        "VIX_Volatility":         ("WTI vs VIX",           PALETTE["shock"]),
        "USD_Index_DXY":          ("WTI vs DXY",           PALETTE["macro"]),
        "Global_CPI_Proxy":       ("WTI vs CPI",           "#2C3E50"),
    }
    available = {k: v for k, v in targets.items() if k in df.columns}
    if not available:
        print("⚠  No correlation targets — skipping chart C")
        return

    fig, ax = plt.subplots(figsize=FIGSIZE_WIDE, facecolor=PALETTE["bg"])
    ax.set_facecolor(PALETTE["bg"])

    for col, (label, colour) in available.items():
        roll_corr = df[anchor].rolling(window).corr(df[col])
        ax.plot(df.index, roll_corr, label=label, color=colour, lw=2)

    ax.axhline(0,    color="black",            lw=0.8, ls="-",  alpha=0.4)
    ax.axhline(0.7,  color=PALETTE["neutral"], lw=0.7, ls="--", alpha=0.5)
    ax.axhline(-0.7, color=PALETTE["neutral"], lw=0.7, ls="--", alpha=0.5)
    ax.fill_between(df.index,  0.7,  1.0, alpha=0.06, color="green")
    ax.fill_between(df.index, -1.0, -0.7, alpha=0.06, color="red")

    add_regime_shading(ax, alpha=0.15)
    ax.set_ylim(-1.1, 1.1)
    ax.set_title(f"Rolling {window}-Month Correlations with WTI Crude Oil",
                 fontsize=13, fontweight="bold")
    ax.set_ylabel("Pearson Correlation", fontsize=10)
    ax.legend(fontsize=9, loc="lower left", ncol=2)
    ax.grid(axis="y", alpha=0.3)
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
    plt.setp(ax.xaxis.get_majorticklabels(), rotation=30, ha="right", fontsize=8)
    add_event_lines(ax, df)

    plt.tight_layout()
    out = OUTPUT_DIR / "C_rolling_correlations.png"
    fig.savefig(out, dpi=DPI, bbox_inches="tight")
    plt.close()
    print(f"✓ Chart C saved → {out}")


# ─── 7. Chart D — Energy Stress Index & Z-Score Shocks ───────────────────────

def chart_stress_index(df: pd.DataFrame):
    if "Energy_Stress_Index" not in df.columns:
        print("⚠  Energy Stress Index not found — skipping chart D")
        return

    fig, axes = plt.subplots(2, 1, figsize=(14, 8), facecolor=PALETTE["bg"])
    fig.suptitle("Energy Price Shock Detection", fontsize=13, fontweight="bold")

    # Panel 1: Composite stress index
    ax = axes[0]
    ax.set_facecolor(PALETTE["bg"])
    esi = df["Energy_Stress_Index"].dropna()
    ax.fill_between(esi.index, esi, where=(esi > 1),
                    interpolate=True, color=PALETTE["oil"], alpha=0.5, label="High stress")
    ax.fill_between(esi.index, esi, where=(esi < -1),
                    interpolate=True, color=PALETTE["gas"], alpha=0.5, label="Price collapse")
    ax.plot(esi.index, esi, color="#2C3E50", lw=2)
    ax.axhline(1,  color=PALETTE["oil"],  lw=1, ls="--", alpha=0.7)
    ax.axhline(-1, color=PALETTE["gas"], lw=1, ls="--", alpha=0.7)
    ax.axhline(0,  color="black",         lw=0.6, alpha=0.4)
    add_regime_shading(ax, alpha=0.15)
    ax.set_title("Composite Energy Stress Index (avg Z-score: oil + gas)", fontsize=10, fontweight="bold")
    ax.set_ylabel("Z-score", fontsize=9)
    ax.legend(fontsize=8)
    ax.grid(axis="y", alpha=0.3)
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
    add_event_lines(ax, df)

    # Panel 2: WTI z-score with shock peaks labelled
    ax = axes[1]
    ax.set_facecolor(PALETTE["bg"])
    if "WTI_Crude_Oil_USD_zscore" in df.columns:
        z = df["WTI_Crude_Oil_USD_zscore"].dropna()
        ax.bar(z.index, z, color=[
            PALETTE["oil"] if v > 0 else PALETTE["gas"] for v in z
        ], alpha=0.7, width=20, label="WTI Z-score")

        # Auto-detect peaks (shocks)
        peaks_pos, _ = find_peaks(z.values, height=1.5, distance=6)
        peaks_neg, _ = find_peaks(-z.values, height=1.5, distance=6)
        for p in peaks_pos:
            ax.annotate(f"+{z.iloc[p]:.1f}σ",
                        xy=(z.index[p], z.iloc[p]),
                        xytext=(0, 6), textcoords="offset points",
                        ha="center", fontsize=7.5, color=PALETTE["oil"], fontweight="bold")
        for p in peaks_neg:
            ax.annotate(f"{z.iloc[p]:.1f}σ",
                        xy=(z.index[p], z.iloc[p]),
                        xytext=(0, -10), textcoords="offset points",
                        ha="center", fontsize=7.5, color=PALETTE["gas"], fontweight="bold")

    add_regime_shading(ax, alpha=0.15)
    ax.axhline(0, color="black", lw=0.6, alpha=0.4)
    ax.set_title("WTI Crude Oil Z-Score (24-Month Rolling Window)", fontsize=10, fontweight="bold")
    ax.set_ylabel("Z-score", fontsize=9)
    ax.legend(fontsize=8)
    ax.grid(axis="y", alpha=0.3)
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
    plt.setp(axes[1].xaxis.get_majorticklabels(), rotation=30, ha="right", fontsize=8)
    add_event_lines(ax, df)

    plt.tight_layout()
    out = OUTPUT_DIR / "D_stress_index.png"
    fig.savefig(out, dpi=DPI, bbox_inches="tight")
    plt.close()
    print(f"✓ Chart D saved → {out}")


# ─── 8. Chart E — Correlation Heatmap by Regime ──────────────────────────────

def chart_regime_heatmap(df: pd.DataFrame):
    """Pairwise correlation matrix split into pre-war vs. crisis period."""
    cols_of_interest = [c for c in [
        "WTI_Crude_Oil_USD", "Brent_Crude_Oil_USD",
        "EU_NatGas_USD", "Henry_Hub_NatGas_USD",
        "Gasoline_USD_per_Gallon", "Heating_Oil_USD",
        "VIX_Volatility", "USD_Index_DXY", "Global_CPI_Proxy",
    ] if c in df.columns]

    if len(cols_of_interest) < 3:
        print("⚠  Too few columns for heatmap — skipping chart E")
        return

    pre_war  = df[df.index < "2022-02-01"][cols_of_interest].corr()
    crisis   = df[df.index >= "2022-02-01"][cols_of_interest].corr()

    fig, axes = plt.subplots(1, 2, figsize=(16, 7), facecolor=PALETTE["bg"])
    fig.suptitle("Correlation Structure: Pre-War vs. Crisis Period",
                 fontsize=13, fontweight="bold")

    short_names = {
        "WTI_Crude_Oil_USD":         "WTI",
        "Brent_Crude_Oil_USD":       "Brent",
        "EU_NatGas_USD":             "EU Gas",
        "Henry_Hub_NatGas_USD":      "HH Gas",
        "Gasoline_USD_per_Gallon":   "Gasoline",
        "Heating_Oil_USD":           "Heat Oil",
        "VIX_Volatility":            "VIX",
        "USD_Index_DXY":             "DXY",
        "Global_CPI_Proxy":          "CPI",
    }

    for ax, corr, title in [
        (axes[0], pre_war,  "Pre-War  (Jan 2020 – Jan 2022)"),
        (axes[1], crisis,   "Crisis Period  (Feb 2022 – Present)"),
    ]:
        corr.rename(index=short_names, columns=short_names, inplace=True)
        sns.heatmap(
            corr, ax=ax, annot=True, fmt=".2f", cmap="RdYlGn",
            vmin=-1, vmax=1, center=0, linewidths=0.5,
            annot_kws={"size": 8}, cbar_kws={"shrink": 0.8},
        )
        ax.set_title(title, fontsize=10, fontweight="bold")
        ax.tick_params(axis="x", rotation=45, labelsize=8)
        ax.tick_params(axis="y", rotation=0,  labelsize=8)

    plt.tight_layout()
    out = OUTPUT_DIR / "E_correlation_heatmap.png"
    fig.savefig(out, dpi=DPI, bbox_inches="tight")
    plt.close()
    print(f"✓ Chart E saved → {out}")


# ─── 9. Chart F — Price Returns Distribution ─────────────────────────────────

def chart_return_distributions(df: pd.DataFrame):
    """Histogram of monthly price returns with normal overlay — shows fat tails."""
    ret_map = {
        "WTI_Crude_Oil_USD_pct":  ("WTI Monthly Returns (%)",  PALETTE["oil"]),
        "EU_NatGas_USD_pct":      ("EU Gas Monthly Returns (%)", PALETTE["gas"]),
    }
    available = {k: v for k, v in ret_map.items() if k in df.columns}
    if not available:
        print("⚠  No return columns — skipping chart F")
        return

    fig, axes = plt.subplots(1, len(available), figsize=(13, 5), facecolor=PALETTE["bg"])
    if len(available) == 1:
        axes = [axes]

    for ax, (col, (title, colour)) in zip(axes, available.items()):
        data = df[col].dropna()
        ax.set_facecolor(PALETTE["bg"])

        # Histogram
        ax.hist(data, bins=25, color=colour, alpha=0.6, density=True,
                edgecolor="white", linewidth=0.4, label="Actual")

        # Normal overlay
        mu, sigma = data.mean(), data.std()
        x = np.linspace(data.min(), data.max(), 200)
        ax.plot(x, stats.norm.pdf(x, mu, sigma), color="black",
                lw=2, ls="--", label=f"Normal (μ={mu:.1f}%, σ={sigma:.1f}%)")

        # Annotations
        kurt = float(stats.kurtosis(data.dropna()))
        skew = float(stats.skew(data.dropna()))
        jb_stat, jb_p = stats.jarque_bera(data.dropna())

        ax.set_title(title, fontsize=10, fontweight="bold")
        ax.set_xlabel("Monthly Return (%)", fontsize=9)
        ax.set_ylabel("Density", fontsize=9)
        ax.legend(fontsize=8)
        ax.grid(axis="y", alpha=0.3)

        stats_text = (f"Kurtosis: {kurt:.2f}  (normal=3)\n"
                      f"Skewness: {skew:.2f}\n"
                      f"Jarque-Bera p: {jb_p:.3f}")
        ax.text(0.97, 0.97, stats_text, transform=ax.transAxes,
                fontsize=7.5, va="top", ha="right",
                bbox=dict(boxstyle="round", fc="white", alpha=0.8, ec="grey"))

    fig.suptitle("Return Distribution Analysis — Fat Tails in Energy Markets",
                 fontsize=12, fontweight="bold")
    plt.tight_layout()
    out = OUTPUT_DIR / "F_return_distributions.png"
    fig.savefig(out, dpi=DPI, bbox_inches="tight")
    plt.close()
    print(f"✓ Chart F saved → {out}")


# ─── 10. Statistical Summary Table ───────────────────────────────────────────

def build_stats_table(df: pd.DataFrame) -> pd.DataFrame:
    """Regime-level descriptive stats table for the article."""
    price_cols = [c for c in [
        "WTI_Crude_Oil_USD", "Brent_Crude_Oil_USD",
        "EU_NatGas_USD", "Henry_Hub_NatGas_USD",
    ] if c in df.columns]

    rows = []
    for label, start, end, _ in REGIMES:
        mask = (df.index >= start) & (df.index <= end)
        sub  = df.loc[mask, price_cols]
        if sub.empty:
            continue
        for col in price_cols:
            if col in sub.columns:
                rows.append({
                    "Regime":   label,
                    "Series":   col.replace("_USD", "").replace("_", " "),
                    "Mean":     round(sub[col].mean(), 2),
                    "Median":   round(sub[col].median(), 2),
                    "Std Dev":  round(sub[col].std(), 2),
                    "Min":      round(sub[col].min(), 2),
                    "Max":      round(sub[col].max(), 2),
                    "Change %": round((sub[col].iloc[-1] / sub[col].iloc[0] - 1) * 100, 1)
                                if len(sub) > 1 else None,
                })

    stats_df = pd.DataFrame(rows)
    stats_df.to_csv(OUTPUT_DIR / "stats_table.csv", index=False)
    print(f"✓ Stats table saved → output/price_analysis/stats_table.csv")
    return stats_df


# ─── 11. Excel Export ─────────────────────────────────────────────────────────

def export_excel(df: pd.DataFrame, stats_df: pd.DataFrame):
    out = OUTPUT_DIR / "price_analysis.xlsx"
    with pd.ExcelWriter(out, engine="openpyxl") as writer:
        df.reset_index().to_excel(writer, sheet_name="Full Time Series", index=False)
        stats_df.to_excel(writer, sheet_name="Regime Stats", index=False)

        # Correlation matrices
        price_cols = [c for c in [
            "WTI_Crude_Oil_USD", "Brent_Crude_Oil_USD",
            "EU_NatGas_USD", "Henry_Hub_NatGas_USD",
            "VIX_Volatility", "USD_Index_DXY",
        ] if c in df.columns]
        df[df.index < "2022-02-01"][price_cols].corr().round(3).to_excel(
            writer, sheet_name="Corr Pre-War")
        df[df.index >= "2022-02-01"][price_cols].corr().round(3).to_excel(
            writer, sheet_name="Corr Crisis")

    print(f"✓ Excel report saved → {out}")


# ─── Main ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 55)
    print("  ENERGY PRICE ANALYSIS PIPELINE")
    print("=" * 55)

    # Load & enrich
    raw_df    = load_prices()
    df        = compute_derived(raw_df)

    print(f"\nGenerating charts → {OUTPUT_DIR}/\n")

    # Charts
    chart_price_timeline(df)
    chart_indexed_prices(df)
    chart_rolling_correlations(df, window=12)
    chart_stress_index(df)
    chart_regime_heatmap(df)
    chart_return_distributions(df)

    # Tables
    stats_df = build_stats_table(df)
    export_excel(df, stats_df)

    print("\n" + "=" * 55)
    print("  DONE — all outputs in output/price_analysis/")
    print("=" * 55)
    print("\nFiles generated:")
    for f in sorted(OUTPUT_DIR.iterdir()):
        print(f"  {f.name}")
    print("\nNext step: python analyze_mauritania.py")