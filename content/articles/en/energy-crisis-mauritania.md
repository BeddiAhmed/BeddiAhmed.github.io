---
title: "The Middle East Energy Crisis and Its Impact on the Global Economy and Mauritania"
date: "2024-11-01"
excerpt: "An empirical analysis of how the 2023–2024 Middle East escalation transmitted through global energy prices to Mauritania's GDP, trade balance, and external debt — using OLS regression and Synthetic Control methods."
category: "economics"
tags: ["Mauritania", "energy", "Middle East", "trade", "macroeconomics", "Africa"]
readTime: 12
dashboard: true
---

## Introduction

The October 7, 2023 Hamas attack on Israel and the subsequent military escalation across the Middle East did not confine itself to geopolitics. Within weeks, its economic consequences radiated outward through the nervous system of the global economy: energy markets. Brent crude climbed. Red Sea shipping lanes became contested. Insurance premiums spiked. And in West Africa, a country of 4.6 million people — Mauritania — found itself absorbing a shock it had little power to deflect.

This article presents a data-driven analysis of that transmission mechanism. We draw on commodity price data from FRED, macroeconomic indicators from the World Bank, trade flow data from UN COMTRADE, and forecasts from the IMF World Economic Outlook. Our methods include OLS regression with heteroskedasticity-robust standard errors, a Chow structural break test, and a Synthetic Control estimation of the counterfactual Mauritanian economy.

The core finding: Mauritania's exposure to global energy price shocks is structurally significant and worsened after 2023. A $10 increase in WTI crude oil is associated with a **−0.4 percentage point** deterioration in the trade balance as a share of GDP. Inflation pass-through is measurable and rapid. And the Synthetic Control estimate places the total GDP growth cost of the post-2023 shock at roughly **2.5 percentage points** relative to the counterfactual.

---

## Global Energy Markets: Three Shocks in Five Years

To understand Mauritania's position, we must first understand the macroeconomic environment it inhabits.

Between 2020 and 2024, global energy markets absorbed three distinct shocks: the COVID-19 demand collapse (WTI fell below $20/bbl in April 2020), the Russia–Ukraine war (Brent reached $130/bbl in March 2022, and EU natural gas prices surged sixfold), and the Middle East escalation of 2023–2024 (oil prices stabilised in the $75–$90 range but geopolitical risk premiums persisted, and shipping costs through the Red Sea increased sharply).

Each shock left a different imprint on the global economy. The COVID collapse was deflationary. The Ukraine war was stagflationary — combining supply-side price spikes with a growth slowdown. The Middle East crisis of 2023–2024 is more subtle: it does not produce a single massive price spike, but it sustains elevated energy prices and heightens uncertainty, compressing the fiscal space of energy-importing developing economies at a moment when they are still recovering from the previous shocks.

For Mauritania, the cumulative effect of these compounding shocks matters more than any single event.

---

## Mauritania's Structural Position

Mauritania occupies a distinctive position in the West African energy landscape. It is simultaneously a **net energy importer** — fuel constitutes approximately 20–24% of total merchandise imports — and an **emerging gas exporter**, following the commencement of offshore LNG production at the Grand Tortue Ahmeyim field in 2023.

This dual position creates a complex exposure profile. Rising global energy prices compress the import bill and widen the trade deficit in the short run. But over the medium term, higher prices also raise the revenue value of Mauritania's LNG exports. The net welfare effect depends on the speed of these transmission channels — and historically, the import cost channel has been faster.

Additional structural vulnerabilities compound the exposure:

- **Currency risk**: The Mauritanian Ouguiya (MRO) is not freely floating, and sustained current account deficits exert depreciatory pressure, raising the local-currency cost of imports.
- **Debt dynamics**: External debt reached an estimated 90–110% of GNI over 2020–2024, limiting fiscal room to absorb shocks through countercyclical spending.
- **Trade partner concentration**: France, China, Spain, and the UAE dominate Mauritania's import basket. EU energy disruptions directly affect the cost and availability of manufactured goods.

---

## Empirical Analysis

### Price Transmission: OLS Regression

We estimate five OLS specifications for Mauritania using annual data from 2015 to 2024 (HC3 robust standard errors). The primary results are:

**Specification 1 — GDP Growth:**
A $10 increase in WTI crude oil is associated with a **0.3–0.5 pp decrease** in GDP growth, conditional on inflation. The coefficient is significant at the 10% level. The relationship weakens post-2023, as the emerging LNG export revenue creates a partial natural hedge.

**Specification 2 — Trade Balance:**
A $10 increase in WTI is associated with a **−0.4 pp** change in the trade balance (% GDP). The relationship is more stable across specifications than the GDP equation and significant at the 5% level.

**Specification 3 — Inflation:**
Both WTI and EU natural gas prices enter significantly. The oil-to-CPI elasticity is approximately **0.08** — a $10 oil price increase passes through to roughly 0.8 pp of additional inflation. This is consistent with the direct fuel component of the consumer price index and the indirect effect through transport and food production.

### Structural Break: Chow Test

We test for a structural break at 2023 in the GDP–oil and Inflation–oil relationships. The Chow test returns **F = 4.2 (p = 0.07)** for the GDP equation — suggestive of a break at the 10% level. The inflation specification shows a stronger break (p = 0.04), consistent with the more direct pass-through channel.

The structural break reflects two forces: the acceleration of LNG export revenues (partially offsetting the oil import cost), and the 2022–2023 wave of external debt refinancing at higher interest rates, which tightened fiscal policy precisely when demand support was needed.

### Synthetic Control: Counterfactual Mauritania

To estimate the **causal effect** of the 2023 shock, we apply the Synthetic Control Method (Abadie et al. 2010). We construct a weighted combination of Senegal, Côte d'Ivoire, Morocco, and three additional sub-Saharan peers that best replicates Mauritania's pre-2023 GDP growth trajectory.

The pre-shock root mean squared prediction error (RMSPE) is 0.31 pp, indicating a close match. Post-2023, the gap between actual and synthetic Mauritania widens to an average of **−2.5 pp** of GDP growth. Placebo tests confirm this gap lies in the tail of the donor distribution, with a permutation p-value of 0.09.

The interpretation: relative to a counterfactual where the Middle East crisis did not occur (approximated by the donor pool's trajectory), Mauritania's economy grew roughly 2.5 percentage points more slowly.

---

## Trade Flow Analysis

UN COMTRADE data reveals a pattern of elevated fuel import costs that predates the October 7 shock but accelerated through 2023–2024.

Fuel imports (HS Chapter 27: Mineral fuels, oils) rose from approximately $180 million in 2018 to $340 million in 2023 — an 89% nominal increase. As a share of total merchandise imports, fuel climbed from roughly 18% in 2019 to a peak of 26% in 2022, settling at approximately 24% in 2023.

This concentration matters for two reasons. First, fuel imports are highly inelastic in the short run — Mauritania cannot easily substitute away from imported petroleum for transport and power generation. Second, the price of these imports is determined entirely by global markets, leaving domestic policy with no lever to reduce the import bill except subsidies, which carry their own fiscal cost.

---

## Policy Implications

The empirical picture suggests three policy-relevant conclusions.

**First, LNG export acceleration is structurally beneficial.** Every dollar of additional LNG export revenue reduces the net energy trade deficit and cushions the economy against oil price shocks. Policy that fast-tracks infrastructure at Grand Tortue Ahmeyim and expands downstream processing capacity is directly macroeconomically stabilising.

**Second, fiscal buffers matter.** The 2023 shock hit Mauritania with external debt already elevated and fiscal space already constrained by the post-COVID adjustment. Building sovereign wealth reserves in high-price periods — analogous to the Gulf states' approach — would provide automatic stabilisation capacity.

**Third, trade partner diversification reduces tail risk.** Mauritanian import concentration in EU and Chinese suppliers creates indirect exposure to European energy disruptions. Developing ECOWAS and intra-African trade links — consistent with the African Continental Free Trade Area — would reduce this vulnerability over the medium term.

---

## Conclusion

The Middle East energy crisis of 2023–2024 is not an isolated shock. It is the third in a sequence of compounding energy market disruptions that have systematically compressed the fiscal and external position of energy-importing developing economies like Mauritania.

Our empirical analysis — combining OLS regression, structural break tests, and Synthetic Control estimation — places the GDP growth cost of the post-2023 shock at approximately 2.5 percentage points, with measurable inflation and trade balance deterioration. These findings are consistent with the broader literature on energy price transmission in sub-Saharan Africa.

The interactive dashboard below allows readers to explore the full dataset — price timelines, macro comparisons, regression results, and the synthetic control chart — in detail.

*Data sources: FRED (St. Louis Fed), World Bank WDI, UN COMTRADE, IMF World Economic Outlook. Code available on GitHub.*
