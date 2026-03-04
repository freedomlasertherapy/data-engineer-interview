# Data Engineering Take-Home Assessment

## About iRESTORE

iRESTORE is a fast-growing company dedicated to providing innovative solutions in the wellness and beauty space. Our mission is to restore confidence by delivering safe and effective solutions that improve health and beauty.

As we continue to scale, we are looking for a Data Engineer who will help lead and optimize our BI stack — from data warehouse infrastructure to modeling, reporting, and AI — enabling data-informed decision-making across the company.

## About the Position

iRESTORE is seeking a highly skilled and hands-on Data Engineer to lead the design, implementation, and optimization of our business intelligence infrastructure.

This role will oversee our full BI stack — from our data warehouse (BigQuery), through data modeling and transformation, to reporting and visualization — and will eventually support advanced analytics and modeling capabilities.

We're looking for a strategic, execution-focused team player who can bridge deep technical expertise with business understanding. You will work closely with teams across Marketing, Operations, Customer Experience, and Creative to build scalable data solutions that unlock growth opportunities, optimize performance, and improve customer satisfaction.

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

The transformation layer must be built using **dbt**. There are two free options:

- **dbt Cloud** – browser-based IDE, free for a single user. Sign up at [cloud.getdbt.com](https://cloud.getdbt.com).
- **dbt Core** – open source, runs locally. Install with:
  ```bash
  pip install dbt-duckdb
  ```
  Full installation guide: [docs.getdbt.com](https://docs.getdbt.com/docs/core/installation-overview).

A dbt project scaffold is already included in the `dbt_project/` folder.

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

## Submission

The expected deliverable is a dashboard presenting sales performance broken down by stores, along with the supporting files and documentation that demonstrate the full data workflow.

Your submission should include:
- A dashboard that clearly presents sales metrics and allows exploration by store and other relevant dimensions
- The data transformation logic used to prepare the dataset (SQL queries, models, or scripts)
- Any supporting files or documentation that illustrate the data pipeline and how the data flows from the raw source to the final dashboard
- Clear assumptions, explanations, and notes about how the analysis was performed
- A short summary of insights or observations you can derive from the data

The goal of this exercise is not only to evaluate the final dashboard, but also to understand how you structure data work end-to-end — from raw data to a clear analytical output.

That said, please use AI tools thoughtfully and responsibly. You are expected to understand, validate, and be able to explain the analysis and conclusions you present.

## Questions?

If you have questions about the requirements, please reach out to your interviewer.

Good luck!
