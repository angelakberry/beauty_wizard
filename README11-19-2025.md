# Beauty Wizard: Cosmetic Ingredient Analysis

## Project Summary

Beauty Wizard is a data analytics project focused on examining cosmetic product formulations, ingredient patterns, brand trends, and chemical safety. The project integrates retail product data, ingredient sources, and government chemical reporting into a unified relational database for analysis. The goal is to support informed consumer decision-making, improve ingredient transparency, and analyze how formulations relate to pricing, brand identity, and safety outcomes.

This work includes data cleaning, database design, exploratory analysis, and the development of new metrics such as safety scores and ingredient diversity.

---

## Data Sources

This project draws from several datasets:

| Source | Format | Purpose |
|--------|--------|---------|
| Sephora Skincare Product Ingredients (Kaggle) | CSV | Retail product listings and ingredient text |
| BeautyFeeds Skincare & Haircare Dataset | Cloud Dataset | Supplementary product and ingredient details |
| California Chemicals in Cosmetics | Government dataset | Chemical reporting, flagged substances, discontinuation dates |
| `cosmetic_p.csv` | CSV | Early dataset used for initial analysis |
| Makeup API: `http://makeup-api.herokuapp.com/api/v1/products.json` | API | Real-time product, brand, and ingredient lookup |

---

## Goals

Minimum goals:

- Identify the most common cosmetic ingredients
- Compare products by category (e.g., cleanser vs. moisturizer)
- Analyze ingredient counts per product
- Determine highest and lowest ranked brands based on dataset criteria

Expanded goals:

- Correlate product composition with price, popularity, and safety scores
- Identify brands with high transparency or frequent use of flagged chemicals
- Compare ingredient patterns across product categories
- Track controversial chemicals over time

---

## Database Structure

Multiple datasets are merged using standardized `brand_id` and `product_id` keys. Core tables include:

| Table | Description |
|-------|-------------|
| `brands` | Central reference connecting all datasets |
| `sephora_products` | Products with price, ingredients, product types, and skin type suitability |
| `beauty_feeds` | Supplemental ingredient listings |
| `chemicals_in_cosmetics` | Chemical reports with regulatory and timeline data |

This schema enables multi-source analysis of ingredients, product categories, and chemical exposure.

---

## Methodology

### Standardization and Cleaning

- Converted identifiers to `snake_case`
- Normalized brand and product names
- Tokenized and standardized ingredient lists

### Missing Data Strategy

| Type | Method |
|------|--------|
| Numeric fields (e.g., price) | Median imputation by category or brand |
| Categorical fields | Assigned "Unknown" values |
| Missing key identifiers | Dropped to maintain relational integrity |

### Derived Metrics

- Ingredient Diversity Index (unique ingredients per product)
- Safety Score (weighted presence of flagged chemicals)
- Ingredient Frequency Rank (cross-dataset prevalence)

### Outlier Treatment

- Identified extreme price values
- Retained valid luxury-priced items
- Flagged anomalies for review rather than discarding

---

## Planned Analyses

Initial goals:

- Price distribution comparisons across brands and categories
- Ingredient frequency analysis across datasets
- Correlation between safety score and price or popularity
- Chemical reporting trends over time

Stretch goals:

- Sentiment analysis using public beauty feeds or reviews
- Comparison with regulatory data (FDA, EWG)
- Automated pipeline for data refresh

---

## Tools and Technologies

- Python
- Pandas
- Matplotlib, Seaborn
- NumPy
- Requests
- SQLite and SQL schema design
- Jupyter Notebook
- Regex and text-processing methods

---

## Repository Structure

beauty_wizard
/data Raw and cleaned datasets
/notebooks EDA, transformations, visualizations
/schema ER diagrams and SQL scripts
/scripts ETL and data cleaning utilities
README.md

---

## Current Status

| Task | Status |
|------|--------|
| Dataset acquisition | Complete |
| Initial cleaning and normalization | Complete |
| Schema design and table joining | Complete |
| Core analysis functions | In progress |
| Visualizations | In progress |
| Safety and diversity scoring | Upcoming |

---

## Contributing

Contributions, dataset suggestions, and methodology feedback are welcome. Please open an issue or submit a pull request.

---

## Project Vision

Beauty Wizard advances ingredient transparency and data-driven beauty research. Empowering consumers with smarter, safer, more sustainable choices.

---

