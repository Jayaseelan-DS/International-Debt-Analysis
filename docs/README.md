# International Debt Analysis

An end-to-end data analytics project analyzing World Bank International Debt Statistics (Jan 2022 release) using Python, MySQL, Power BI, and Streamlit.

---

## 1. Project Overview

This project analyzes external debt data for 120 countries across 576 economic indicators and 25 years (2000–2024), sourced from the World Bank's International Debt Statistics dataset. The pipeline covers data cleaning, database design, SQL-based analysis, and two forms of visualization (Power BI dashboard and a Streamlit query explorer).

**Objectives:**
- Clean and structure raw World Bank debt data into a normalized relational database
- Answer 30 analytical questions (basic, intermediate, advanced) using SQL
- Visualize key trends and comparisons through an interactive Power BI dashboard
- Provide an interactive Streamlit app to explore all 30 SQL queries and their results

---

## 2. Data Source

Data was sourced from the World Bank's **International Debt Statistics (IDS), January 2022** release, provided as five CSV files:

| File | Used? | Purpose |
|---|---|---|
| `IDS_ALLCountries_Data.csv` | ✅ | Primary dataset — debt values by country, indicator, and year |
| `IDS_CountryMetaData.csv` | ✅ | Country reference data (region, income group, lending category) |
| `IDS_SeriesMetaData.csv` | ✅ | Indicator reference data (topic classification) |
| `IDS_FootNoteMetaData.csv` | ❌ | Source citations/caveats only — not analytical data |
| `Country-Series - Metadata.csv` | ❌ | Source notes only — not analytical data |

---

## 3. Data Preprocessing

Performed in Python (Pandas), inside `notebooks/01_data_exploration.ipynb`.

**Key steps:**
1. **Reshaping (wide → long):** the raw data had one column per year (2000–2032). Used `pd.melt()` to convert this into a long format with `Year` and `Value` columns — required for a normalized relational schema.
2. **Year filtering:** removed years 2025–2032, which were unpopulated forecast years with no real reported data.
3. **Null handling:** applied **backward fill, then forward fill**, grouped by (Country, Indicator) — filling gaps using the nearest real year for that specific country/indicator combination. This was chosen over mean/median fill because debt values trend over time rather than clustering around an average. Combinations with *no* real data in any year (i.e., nothing to fill from) were dropped afterward.
4. **Removing aggregate/regional rows:** the raw data included 14 World Bank aggregate codes (e.g., `EAP`, `LIC`, `IDA` — regional/income-group totals, not individual countries). These were removed from both the country reference table and the main dataset to avoid double-counting in any "total"-style calculation.
5. **Whitespace cleanup:** country and indicator codes had trailing whitespace (a World Bank CSV export artifact) which silently broke foreign key joins in MySQL — fixed with `.str.strip()`.
6. **Duplicate removal:** identified and removed fully blank rows (CSV export artifacts).

**Final cleaned dataset:** 1,290,500 rows across 120 countries and 576 indicators.

---

## 4. Exploratory Data Analysis (EDA)

Key findings:
- The `Value` column spans an extreme range (−$445B to $18.6T) because it blends fundamentally different indicator types — dollar amounts, percentages, and year-counts — under one column. **Any aggregation must filter to a specific indicator to be economically meaningful.**
- ~18 of ~20 indicator "topics" are core external-debt metrics; `Population, total` and `GNI` are useful *supporting* metrics (e.g., for per-capita calculations), not debt themselves.
- Indicator coverage is generally strong — even the sparsest indicator has 200+ data points; median coverage is ~3,075 out of a possible 3,350 (120 countries × ~28 years).

---

## 5. Database Design

A normalized **star schema** was built in MySQL: one fact table, two dimension tables.

```
countries (120 rows)          indicators (576 rows)
├── country_code (PK)         ├── series_code (PK)
├── country_name              ├── indicator_name
├── region                    └── topic
├── income_group
└── lending_category
        \                           /
         \                         /
          debt_data (1,290,500 rows)
          ├── id (PK, auto-increment)
          ├── country_code (FK → countries)
          ├── series_code (FK → indicators)
          ├── year
          └── value
```

Indexes were added on `debt_data.country_code` and `debt_data.series_code` to support fast joins/aggregations over the 1.29M-row fact table.

---

## 6. SQL Analysis — Important Methodology Note

The 30 required queries fall into three tiers (10 basic, 10 intermediate, 10 advanced) — see `sql/queries.sql` for the full set.

**⚠️ Key caveat on "total debt" style questions:**
Generic questions (e.g., *"calculate the total global debt"*, *"find the country with the highest total debt"*) do not name a specific indicator or year. For these, `value` was aggregated as-is across **all 576 indicators and all 25 years**, per the assignment's practice-style phrasing. This means these totals blend fundamentally different units (dollars, percentages, years) and years together, and **should not be read as real economic figures** — they demonstrate correct SQL mechanics (`JOIN`, `GROUP BY`, `HAVING`, window functions, subqueries, views) rather than a rigorous financial analysis.

For contrast, two queries were also built using a **filtered, single-indicator, single-year** approach for genuine real-world accuracy:
- Total global external debt stock, 2024 only (`series_code = 'DT.DOD.DECT.CD'`, `year = 2024`): **$8,939,920,662,152**
- Top 10 countries and Top 3-per-indicator, both restricted to `year = 2024` for a real point-in-time snapshot

These 2024-accurate versions are the ones used to feed the Power BI dashboard and should be treated as the more defensible figures for any real-world interpretation.

**SQL techniques demonstrated across the 30 queries:**
`SELECT`/`WHERE`/`ORDER BY`/`LIMIT`, aggregate functions (`SUM`, `AVG`, `MIN`, `MAX`, `COUNT`), `JOIN`, `GROUP BY`/`HAVING`, scalar and correlated subqueries, `CASE WHEN` categorization, `VIEW` creation, and window functions (`RANK() OVER`, `PARTITION BY`, cumulative `SUM() OVER`).

---

## 7. Power BI Dashboard

File: `dashboard/debt_dashboard.pbix`

| Visual | Insight |
|---|---|
| Card | Total global external debt, 2024: **$8.94T** |
| Bar chart | Top 10 countries by debt (China leads at $2.4T) |
| Pie chart | Debt by region — East Asia & Pacific leads at 38.1% |
| Column chart | Debt by income group — Upper-middle-income countries hold the most external debt ($6.4T) |
| Line chart | Debt trend 2000–2024 — debt roughly quadrupled, with a visible acceleration around 2008–2009 |
| Slicer + Table | Interactive country deep-dive across 4 core indicators (debt stock, interest, repayments, disbursements) |

All measures use DAX `CALCULATE()` filtered to `series_code = 'DT.DOD.DECT.CD'` and `year = 2024` (or unfiltered by year for the trend line) to ensure dashboard figures are real, comparable, point-in-time numbers — consistent with the 2024-accurate SQL queries above.

---

## 8. Streamlit Query Explorer

File: `scripts/app.py`

An interactive app where a user selects any of the 30 required questions from a dropdown; the app runs the corresponding SQL query live against MySQL and displays both the query and its result as a table.

Run with:
```bash
streamlit run scripts/app.py
```

---

## 9. Key Insights

1. Global external debt stock grew roughly **4x from 2000 to 2024** (~$2T → ~$8.94T), with a visible inflection around the 2008 financial crisis.
2. **Upper-middle-income countries**, not low-income countries, hold the largest share of external debt — driven by large economies like China, Brazil, Mexico, and Turkey.
3. **East Asia & Pacific** is the most indebted region (38% of global total), largely driven by China.
4. Debt is highly concentrated: a small number of countries account for a disproportionate share of global external debt.

---

## 10. Tools & Technologies

- **Python** (Pandas) — data cleaning, reshaping, EDA
- **MySQL** (Workbench) — relational database, schema design, SQL analysis
- **Power BI Desktop** — interactive dashboard
- **Streamlit** (Python) — interactive SQL query explorer
- **VS Code** — development environment (Jupyter notebooks + scripts)

---

## Project Structure

```
International_Debt_Analysis/
├── data/
│   ├── raw/                       # Original World Bank CSVs
│   └── cleaned/                   # Cleaned datasets
├── notebooks/
│   └── data_exploration.ipynb     # Cleaning, EDA
├── sql/
│   ├── International_debt.sql     # Database/table creation + exploratory queries
│   └── queries.sql                # Final 30 required queries + bonus 2024-accurate fixes
├── scripts/
│   ├── load_to_mysql.py           # Loads cleaned CSVs into MySQL
│   └── app.py                     # Streamlit query explorer (all 30 queries)
├── dashboard/
│   └── Dashboard.pbix             # Power BI dashboard
├── docs/
│   └── README.md                  # This file
```
