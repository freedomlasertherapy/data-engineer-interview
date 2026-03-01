# Data Engineering Take-Home Assessment

## Overview

You've been asked to build a data pipeline that unifies sales data from three different retail sources into a single analytical fact table.

**Time expectation:** This task is designed to take approximately 1 hour of focused work.

## The Challenge

Your company has sales data from three different retail channels:
- **Costco** - Warehouse club sales (CSV)
- **Amazon** - Marketplace orders (Parquet)
- **Shopify** - E-commerce store (JSON)

Each source has a different schema, date format, and data characteristics. Your task is to:

1. **Ingest** the data from GCS
2. **Transform** the data using dbt
3. **Produce** a unified `fct_sales` fact table

## Data Sources

### GCS Location
```
gs://irestore-data-eng-assignment/data-engineer-interview/
├── costco/costco_sales.csv          (100k rows, CSV)
├── amazon/amazon_orders.parquet     (100k rows, Parquet)
└── shopify/shopify_orders.json      (100k orders, NDJSON)
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

Create a `fct_sales` table that unifies all sources with a common schema including:
- Unique sale identifier
- Source system identification
- Normalized dates and timestamps
- Product information
- Financial amounts (gross, discount, tax, shipping, net)
- Geographic information
- Order status (normalized across sources)

See `dbt_project/models/marts/_marts.yml` for the full expected schema.

## Prerequisites

### GCP Account (required)

A personal Google Cloud Platform (GCP) account is required to access the source data. GCP is free to sign up.

You can create one by signing up with any Gmail address at [cloud.google.com](https://cloud.google.com). If you don't have a Gmail address, you can create one for free at [gmail.com](https://gmail.com).

Once you have a GCP account, **send us your Gmail address** and we will grant you read access to the source data bucket. You can start working on the exercise once access is confirmed.

### dbt (required)

The transformation layer must be built using **dbt**. dbt is free and open source.

Install it with:
```bash
pip install dbt-duckdb
```

Or follow the official guide at [docs.getdbt.com](https://docs.getdbt.com/docs/core/installation-overview). A dbt project scaffold is already included in the `dbt_project/` folder.

## Deliverables

1. **Working dbt models** - Staging, intermediate (if needed), and mart layers
2. **README updates** - Document your approach, assumptions, and how to run

### Bonus (Optional)
- Add dbt tests (generic and/or custom)

## Evaluation Criteria

You will be evaluated on:
- **Correctness** - Does the pipeline work? Is the data accurate?
- **Code quality** - Readable, maintainable, well-organized
- **Design decisions** - How you handle edge cases, schema choices
- **Documentation** - Clear explanation of your approach

## Hints

- Start with staging models that handle source-specific quirks
- Consider how to handle: cancelled orders, refunds, multi-line orders
- Think about data type consistency across sources
- The data has some quality issues (by design) - handle them appropriately

## Questions?

If you have questions about the requirements, please reach out to your interviewer.

Good luck!
