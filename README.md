# Data Engineering Take-Home Assessment

## About iRESTORE

iRESTORE is a fast-growing company dedicated to providing innovative solutions in the wellness and beauty space. Our mission is to restore confidence by delivering safe and effective solutions that improve health and beauty.

## About the Position

iRESTORE is seeking a highly skilled and hands-on Data Engineer to lead the design, implementation, and optimization of our business intelligence infrastructure.

This role will oversee our full BI stack — from our data warehouse (BigQuery), through data modeling and transformation, to reporting and visualization — and will eventually support advanced analytics and modeling capabilities.

We're looking for a strategic, execution-focused team player who can bridge deep technical expertise with business understanding. You will work closely with teams across Marketing, Operations, Customer Experience, and Creative to build scalable data solutions that unlock growth opportunities, optimize performance, and improve customer satisfaction.

## The Challenge

You've been asked to build a data pipeline that unifies sales data from three different retail sources into a single analytical fact table, and to present the results in a dashboard.

**Time expectation:** This task is designed to take approximately 2 hours of focused work.

The data comes from three retail channels, each with a different schema, date format, and data characteristics:
- **Costco** — Warehouse club sales (CSV)
- **Amazon** — Marketplace orders (Parquet)
- **Shopify** — E-commerce store (JSON)

Your task is to:

1. **Ingest** the raw data from GCS
2. **Transform** it using dbt into a clean, unified model
3. **Build** a dashboard that presents sales performance broken down by store and other relevant dimensions

## Data Sources

### Location

The source data is publicly available in Google Cloud Storage — no authentication required.

```
gs://irestore-data-eng-assignment/
├── costco_sales.csv          (CSV)
├── amazon_orders.parquet     (Parquet)
└── shopify_orders.json       (NDJSON)
```

### Source Schemas

**Costco (CSV)**
- Date format: `MM/DD/YYYY`
- Amounts formatted as strings with `$` symbol (e.g., `$24.99`)
- Multi-row transactions (one row per item in transaction)

**Amazon (Parquet)**
- ISO timestamp format
- Nested product attributes
- Contains order statuses: Shipped, Cancelled, Returned, Pending

**Shopify (JSON/NDJSON)**
- ISO8601 timestamps with timezone
- Nested customer object
- Line items as array (multiple products per order)
- Discount codes included

## Expected Output

The target data model is a `fct_sales` table that unifies all sources with a consistent schema:
- Unique sale identifier
- Source system identification
- Normalized dates and timestamps
- Product information
- Financial amounts (gross, discount, tax, shipping, net)
- Geographic information
- Order status (normalized across sources)

See `dbt_project/models/marts/_marts.yml` for the full expected schema.

## Getting Started

A `docker-compose.yml` is included with everything you need:

```bash
docker compose up
```

This starts two services:
- **Jupyter Lab** — available at `http://localhost:8888` (token: `interview`). Use this for data exploration and your dashboard.
- **dbt** — a container with `dbt-duckdb` pre-installed. Run transformations with:
  ```bash
  docker compose exec dbt bash
  dbt run
  ```

Both services share the `./data` directory and the DuckDB database, so your dbt models are immediately queryable from Jupyter.

### Without Docker

If you prefer to work locally:

```bash
pip install dbt-duckdb jupyterlab duckdb pandas pyarrow
```

A dbt project scaffold is already included in the `dbt_project/` folder.

## Submission

Your submission should include:
- A dashboard that clearly presents sales metrics and allows exploration by store and other relevant dimensions
- The dbt models and transformation logic used to prepare the dataset (staging, intermediate if needed, and mart layers)
- Any supporting files or documentation that illustrate the data pipeline and how data flows from raw source to final output
- Clear assumptions, explanations, and notes about how the analysis was performed
- A short summary of insights or observations derived from the data

The goal of this exercise is not only to evaluate the final dashboard, but also to understand how you structure data work end-to-end — from raw data to a clear analytical output.

You may use AI tools. Be prepared to explain and walk through your work in a follow-up conversation.

### Bonus (Optional)
- Add dbt tests (generic and/or custom)

## Evaluation Criteria

You will be evaluated on:
- **Correctness** — Does the pipeline work? Is the data accurate?
- **Code quality** — Readable, maintainable, well-organized
- **Design decisions** — How you handle edge cases, schema choices
- **Documentation** — Clear explanation of your approach

## Hints

- Start with staging models that handle source-specific quirks
- Consider how to handle cancelled orders, refunds, and multi-line orders
- Think about data type consistency across sources
- The data has some quality issues by design — handle them appropriately

## Questions?

If you have questions about the requirements, please reach out to your interviewer.

Good luck!
