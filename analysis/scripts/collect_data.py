"""
collect_data.py
================
Data pipeline for: "Middle East Energy Crisis — Impact on the Global and Mauritanian Economy"

Pulls from:
  1. FRED       — Oil/LNG commodity prices
  2. World Bank — Macro indicators for Mauritania and peer countries
  3. UN COMTRADE (Public API v2) — Mauritania trade flows
  4. IMF World Economic Outlook (JSON API) — GDP/inflation forecasts

Outputs (in /output/):
  - prices.csv           : commodity price time series
  - wb_macro.csv         : World Bank macro panel data
  - comtrade_exports.csv : Mauritania export flows by partner
  - comtrade_imports.csv : Mauritania import flows by partner
  - imf_weo.csv          : IMF WEO selected indicators
  - summary.xlsx         : All sheets combined for review

Dependencies (install once):
  pip install fredapi pandas requests openpyxl wbgapi tqdm
"""

import os
import time
import logging
import requests
import pandas as pd
from tqdm import tqdm
from pathlib import Path
from datetime import datetime

# ─── Config ──────────────────────────────────────────────────────────────────

# Get a free FRED API key at: https://fred.stlouisfed.org/docs/api/api_key.html
# Set it as an env var: export FRED_API_KEY=""
# Or paste it directly below (not recommended for shared code)
FRED_API_KEY = os.environ.get("FRED_API_KEY", "a6ac84fb97e4bd58cda7277c5f0d6ea1")

START_DATE = "2020-01-01"
END_DATE   = datetime.today().strftime("%Y-%m-%d")

OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)s  %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)

# ─── 1. FRED — Commodity Prices ──────────────────────────────────────────────

FRED_SERIES = {
    # Oil
    "WTI_Crude_Oil_USD":         "DCOILWTICO",      # WTI crude, daily
    "Brent_Crude_Oil_USD":       "DCOILBRENTEU",    # Brent crude, daily
    # Natural Gas
    "Henry_Hub_NatGas_USD":      "MHHNGSP",         # Henry Hub, monthly
    "EU_NatGas_USD":             "PNGASEUUSDM",     # EU natural gas, monthly
    # LNG / Refined
    "Gasoline_USD_per_Gallon":   "GASDESW",         # US regular gasoline
    "Heating_Oil_USD":           "DHOILNYH",        # NY heating oil
    # Context
    "USD_Index_DXY":             "DTWEXBGS",        # Dollar strength
    "Global_CPI_Proxy":          "CPIAUCSL",        # US CPI as global proxy
    "VIX_Volatility":            "VIXCLS",          # Market fear gauge
}

def fetch_fred_series(api_key: str) -> pd.DataFrame:
    """Download FRED time series and return as wide-format DataFrame."""
    if api_key == "YOUR_FRED_API_KEY_HERE":
        log.warning("No FRED API key set — skipping FRED pull.")
        return pd.DataFrame()

    try:
        from fredapi import Fred
        fred = Fred(api_key=api_key)
    except ImportError:
        log.error("fredapi not installed. Run: pip install fredapi")
        return pd.DataFrame()

    frames = {}
    for label, series_id in tqdm(FRED_SERIES.items(), desc="FRED"):
        try:
            s = fred.get_series(series_id, observation_start=START_DATE)
            s.name = label
            frames[label] = s
            time.sleep(0.3)   # be polite to the API
        except Exception as e:
            log.warning(f"  Could not fetch {series_id}: {e}")

    if not frames:
        return pd.DataFrame()

    df = pd.DataFrame(frames)
    df.index.name = "date"
    df = df.sort_index()

    # Resample to monthly for easier merging with other sources
    df_monthly = df.resample("MS").mean()
    df_monthly.to_csv(OUTPUT_DIR / "prices.csv")
    log.info(f"FRED: saved {len(df_monthly)} monthly rows → output/prices.csv")
    return df_monthly


# ─── 2. World Bank — Macro Panel ─────────────────────────────────────────────

# Mauritania + sub-Saharan peers for synthetic control / benchmarking
WB_COUNTRIES = {
    "MRT": "Mauritania",
    "SEN": "Senegal",
    "MLI": "Mali",
    "CIV": "Côte d'Ivoire",
    "GHA": "Ghana",
    "NGA": "Nigeria",
    "ZAF": "South Africa",
    "MAR": "Morocco",
    "DZA": "Algeria",          # North Africa oil exporter (comparison)
    "SAU": "Saudi Arabia",     # Shock origin
    "WLD": "World",
    "SSF": "Sub-Saharan Africa (aggregate)",
}

WB_INDICATORS = {
    "NY.GDP.MKTP.KD.ZG":  "GDP_growth_pct",
    "NY.GDP.PCAP.KD.ZG":  "GDP_per_capita_growth_pct",
    "FP.CPI.TOTL.ZG":     "Inflation_CPI_pct",
    "NE.IMP.GNFS.ZS":     "Imports_pct_GDP",
    "NE.EXP.GNFS.ZS":     "Exports_pct_GDP",
    "BN.CAB.XOKA.GD.ZS":  "Current_Account_pct_GDP",
    "GC.XPN.TOTL.GD.ZS":  "Govt_Expenditure_pct_GDP",
    "DT.DOD.DECT.GN.ZS":  "External_Debt_pct_GNI",
    "EN.ATM.CO2E.KT":     "CO2_Emissions_kt",
    "EG.USE.PCAP.KG.OE":  "Energy_Use_per_capita",
    "TX.VAL.FUEL.ZS.UN":  "Fuel_Exports_pct_merchandise",
    "TM.VAL.FUEL.ZS.UN":  "Fuel_Imports_pct_merchandise",
    "PA.NUS.FCRF":         "Official_Exchange_Rate_per_USD",
}

def fetch_world_bank() -> pd.DataFrame:
    """Download World Bank indicators for all countries and return long-format DataFrame."""
    try:
        import wbgapi as wb
    except ImportError:
        log.error("wbgapi not installed. Run: pip install wbgapi")
        return pd.DataFrame()

    records = []
    year_range = range(2015, int(END_DATE[:4]) + 1)
    countries  = list(WB_COUNTRIES.keys())
    indicators = list(WB_INDICATORS.keys())

    log.info(f"World Bank: fetching {len(indicators)} indicators × {len(countries)} countries...")
    for ind_code, ind_label in tqdm(WB_INDICATORS.items(), desc="World Bank"):
        try:
            df_raw = wb.data.DataFrame(
                ind_code,
                economy=countries,
                time=year_range,
                labels=False,
            )
            # wbgapi returns years as columns — melt to long
            df_raw = df_raw.reset_index()
            id_col = df_raw.columns[0]        # economy code
            df_long = df_raw.melt(id_vars=id_col, var_name="year", value_name=ind_label)
            df_long.columns = ["country_code", "year", ind_label]
            df_long["country_name"] = df_long["country_code"].map(WB_COUNTRIES)
            df_long["year"] = df_long["year"].astype(str).str.replace("YR", "").astype(int)
            records.append(df_long)
            time.sleep(0.2)
        except Exception as e:
            log.warning(f"  WB indicator {ind_code} failed: {e}")

    if not records:
        return pd.DataFrame()

    # Merge all indicators on country + year
    df_all = records[0]
    for df_next in records[1:]:
        df_all = df_all.merge(df_next, on=["country_code", "country_name", "year"], how="outer")

    df_all = df_all.sort_values(["country_code", "year"])
    df_all.to_csv(OUTPUT_DIR / "wb_macro.csv", index=False)
    log.info(f"World Bank: saved {len(df_all)} rows → output/wb_macro.csv")
    return df_all


# ─── 3. UN COMTRADE — Mauritania Trade Flows ─────────────────────────────────
#
# Uses the free public COMTRADE API (no key needed for basic calls, ~100/hr limit).
# Docs: https://comtradeplus.un.org/TradeFlow
#
# HS Chapters relevant to energy:
#   27  — Mineral fuels, mineral oils (crude + refined energy)
#   84  — Machinery (capital goods)
#   85  — Electrical equipment
#   10  — Cereals (food security link to energy costs)

COMTRADE_BASE = "https://comtradeapi.un.org/public/v1/preview/C/A/HS"

COMTRADE_PARAMS_BASE = {
    "reporterCode": "478",      # Mauritania's UN COMTRADE code
    "period":       None,       # filled per year in loop
    "cmdCode":      "27,84,85,10,26",   # energy + machinery + mining
    "flowCode":     None,       # "M" imports, "X" exports
    "partnerCode":  "0",        # 0 = World total; change to specific ISO if needed
    "includeDesc":  "True",
}

def fetch_comtrade(flow: str = "M", years: list = None) -> pd.DataFrame:
    """
    Pull Mauritania trade data from UN COMTRADE public API.
    flow = "M" (imports) or "X" (exports)
    """
    if years is None:
        years = list(range(2018, int(END_DATE[:4]) + 1))

    all_rows = []
    label = "imports" if flow == "M" else "exports"

    for year in tqdm(years, desc=f"COMTRADE {label}"):
        params = {**COMTRADE_PARAMS_BASE, "period": str(year), "flowCode": flow}
        try:
            resp = requests.get(COMTRADE_BASE, params=params, timeout=30)
            resp.raise_for_status()
            data = resp.json().get("data", [])
            if data:
                all_rows.extend(data)
            time.sleep(1.2)   # stay within 100 req/hr free tier
        except requests.exceptions.HTTPError as e:
            if resp.status_code == 429:
                log.warning("COMTRADE rate limit hit — waiting 60s...")
                time.sleep(60)
            else:
                log.warning(f"  COMTRADE {year} {flow} failed: {e}")
        except Exception as e:
            log.warning(f"  COMTRADE {year} {flow} error: {e}")

    if not all_rows:
        log.warning(f"No COMTRADE data returned for flow={flow}")
        return pd.DataFrame()

    df = pd.DataFrame(all_rows)

    # Keep only most relevant columns
    keep_cols = [c for c in [
        "period", "reporterDesc", "partnerDesc", "flowDesc",
        "cmdCode", "cmdDesc", "primaryValue", "netWgt",
        "qty", "qtyUnitAbbr",
    ] if c in df.columns]
    df = df[keep_cols].copy()
    df.rename(columns={"primaryValue": "trade_value_USD", "period": "year"}, inplace=True)

    out_path = OUTPUT_DIR / f"comtrade_{label}.csv"
    df.to_csv(out_path, index=False)
    log.info(f"COMTRADE: saved {len(df)} rows → output/comtrade_{label}.csv")
    return df


# ─── 4. IMF WEO — Forecasts & Projections ────────────────────────────────────
#
# IMF publishes WEO data in bulk. We download the latest release CSV directly.
# URL updates each April/October; check https://www.imf.org/en/Publications/WEO

IMF_WEO_URL = (
    "https://www.imf.org/external/pubs/ft/weo/2024/02/weodata/WEOOct2024all.xls"
)

WEO_SUBJECTS = [
    "NGDP_RPCH",   # Real GDP growth
    "PCPIPCH",     # Inflation (CPI % change)
    "BCA_NGDPD",   # Current account % GDP
    "GGR_NGDP",    # Govt revenue % GDP
    "GGX_NGDP",    # Govt expenditure % GDP
    "GGXWDG_NGDP", # Gross debt % GDP
    "TM_RPCH",     # Import volume growth
    "TX_RPCH",     # Export volume growth
]

WEO_COUNTRIES = ["Mauritania", "Senegal", "Mali", "Algeria", "Nigeria",
                  "Saudi Arabia", "World", "Sub-Saharan Africa"]

def fetch_imf_weo() -> pd.DataFrame:
    """Download IMF WEO bulk file and filter to relevant countries/subjects."""
    log.info("IMF WEO: downloading bulk file (this may take a moment)...")
    try:
        # WEO files are tab-separated with mixed encoding
        df_raw = pd.read_csv(
            IMF_WEO_URL,
            sep="\t",
            encoding="latin-1",
            low_memory=False,
        )
    except Exception as e:
        log.warning(f"  IMF WEO download failed: {e}")
        log.info("  Trying fallback URL...")
        # Fallback: April 2024 release
        fallback = "https://www.imf.org/external/pubs/ft/weo/2024/01/weodata/WEOApr2024all.xls"
        try:
            df_raw = pd.read_csv(fallback, sep="\t", encoding="latin-1", low_memory=False)
        except Exception as e2:
            log.error(f"  IMF WEO fallback also failed: {e2}")
            return pd.DataFrame()

    # Filter to relevant subjects and countries
    if "WEO Subject Code" in df_raw.columns and "Country" in df_raw.columns:
        df = df_raw[
            df_raw["WEO Subject Code"].isin(WEO_SUBJECTS) &
            df_raw["Country"].isin(WEO_COUNTRIES)
        ].copy()
    else:
        log.warning("WEO columns unexpected — returning raw file head for inspection")
        df = df_raw.head(500)

    # Melt year columns to long format
    year_cols = [c for c in df.columns if str(c).isdigit() and 2015 <= int(c) <= 2030]
    id_cols   = [c for c in df.columns if c not in year_cols]
    df_long   = df.melt(id_vars=id_cols, value_vars=year_cols,
                         var_name="year", value_name="value")
    df_long["year"] = df_long["year"].astype(int)

    df_long.to_csv(OUTPUT_DIR / "imf_weo.csv", index=False)
    log.info(f"IMF WEO: saved {len(df_long)} rows → output/imf_weo.csv")
    return df_long


# ─── 5. Bundle into Excel ─────────────────────────────────────────────────────

def save_summary_excel(dfs: dict):
    """Write all DataFrames to a single Excel workbook, one sheet each."""
    out_path = OUTPUT_DIR / "summary.xlsx"
    with pd.ExcelWriter(out_path, engine="openpyxl") as writer:
        for sheet_name, df in dfs.items():
            if df is not None and not df.empty:
                df.to_excel(writer, sheet_name=sheet_name[:31], index=False)
                log.info(f"  Excel sheet '{sheet_name}' → {len(df)} rows")
    log.info(f"Excel bundle saved → output/summary.xlsx")


# ─── 6. Quick Validation Report ───────────────────────────────────────────────

def print_validation(dfs: dict):
    print("\n" + "="*60)
    print("DATA VALIDATION SUMMARY")
    print("="*60)
    for name, df in dfs.items():
        if df is None or df.empty:
            print(f"  ⚠  {name:<25} — EMPTY (check logs above)")
        else:
            print(f"  ✓  {name:<25} — {len(df):>6} rows × {len(df.columns):>3} cols")
    print("="*60)
    print(f"\nAll files saved to: ./{OUTPUT_DIR}/\n")


# ─── Main ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    log.info("Starting data collection pipeline...")
    log.info(f"Date range: {START_DATE} → {END_DATE}")

    prices      = fetch_fred_series(FRED_API_KEY)
    wb_macro    = fetch_world_bank()
    ct_imports  = fetch_comtrade(flow="M")
    ct_exports  = fetch_comtrade(flow="X")
    imf_weo     = fetch_imf_weo()

    dfs = {
        "Commodity Prices":    prices,
        "WB Macro Panel":      wb_macro,
        "COMTRADE Imports":    ct_imports,
        "COMTRADE Exports":    ct_exports,
        "IMF WEO Forecasts":   imf_weo,
    }

    save_summary_excel(dfs)
    print_validation(dfs)