"""
Data generator for the iRESTORE Data Engineer interview assessment.

Generates synthetic sales data for three retail channels:
- Costco (CSV) - 100k rows, multi-row transactions
- Amazon (Parquet) - 100k rows, nested product attributes
- Shopify (NDJSON) - 100k orders with line items

Intentional data quality issues are seeded throughout.
Run: pip install pandas pyarrow faker && python generate_data.py
"""

import json
import os
import random
from datetime import datetime, timedelta, timezone
from decimal import Decimal, ROUND_HALF_UP

import pandas as pd
from faker import Faker

fake = Faker()
Faker.seed(42)
random.seed(42)

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "data")

# ---------- shared constants ----------

DATE_START = datetime(2023, 1, 1)
DATE_END = datetime(2024, 12, 31)
DATE_RANGE_DAYS = (DATE_END - DATE_START).days

PRODUCTS = [
    {"sku": "IR-PRO-001", "name": "iRESTORE Pro Helmet", "category": "Devices", "price": 1195.00},
    {"sku": "IR-ESS-002", "name": "iRESTORE Essential Helmet", "category": "Devices", "price": 695.00},
    {"sku": "IR-SRM-003", "name": "Hair Growth Serum", "category": "Topicals", "price": 39.99},
    {"sku": "IR-SUP-004", "name": "Hair Growth Supplements (90ct)", "category": "Supplements", "price": 34.99},
    {"sku": "IR-SHM-005", "name": "Anti-Thinning Shampoo", "category": "Hair Care", "price": 29.99},
    {"sku": "IR-CND-006", "name": "Anti-Thinning Conditioner", "category": "Hair Care", "price": 29.99},
    {"sku": "IR-BND-007", "name": "Complete Hair Growth Bundle", "category": "Bundles", "price": 1299.00},
    {"sku": "IR-CAP-008", "name": "iRESTORE Flex Cap", "category": "Devices", "price": 495.00},
    {"sku": "IR-OIL-009", "name": "Scalp Revitalizing Oil", "category": "Topicals", "price": 24.99},
    {"sku": "IR-VIT-010", "name": "Biotin Plus Vitamins (60ct)", "category": "Supplements", "price": 19.99},
]

US_STATES = [
    "CA", "TX", "FL", "NY", "IL", "PA", "OH", "GA", "NC", "MI",
    "NJ", "VA", "WA", "AZ", "MA", "TN", "IN", "MO", "MD", "WI",
    "CO", "MN", "SC", "AL", "LA", "KY", "OR", "OK", "CT", "UT",
]

COUNTRIES = ["US"] * 90 + ["CA"] * 5 + ["MX"] * 3 + ["GB"] * 1 + ["AU"] * 1

PAYMENT_METHODS = ["credit_card"] * 50 + ["debit_card"] * 20 + ["paypal"] * 15 + ["apple_pay"] * 10 + ["gift_card"] * 5


def rand_date():
    return DATE_START + timedelta(days=random.randint(0, DATE_RANGE_DAYS))


def money(val):
    return float(Decimal(str(val)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


# ---------- Costco ----------

def generate_costco(target_rows=100_000):
    """
    Costco CSV: multi-row transactions (one row per item).
    Dates as MM/DD/YYYY, amounts as "$XX.XX" strings.

    Quality issues:
    - ~0.5% of rows have negative quantities (returns mixed into sales)
    - ~0.3% have missing member_id
    - Some duplicate transaction rows (~0.2%)
    - A few dates are clearly wrong (year 2025 in historical data)
    """
    rows = []
    txn_id = 100000

    while len(rows) < target_rows:
        txn_id += 1
        txn_date = rand_date()
        num_items = random.choices([1, 2, 3, 4, 5], weights=[40, 30, 15, 10, 5])[0]
        member_id = f"M{random.randint(100000, 999999)}"
        store_id = f"WH-{random.randint(100, 999)}"
        state = random.choice(US_STATES)
        payment = random.choice(PAYMENT_METHODS)

        # quality issue: missing member_id
        if random.random() < 0.003:
            member_id = ""

        # quality issue: future/wrong date
        if random.random() < 0.002:
            txn_date = txn_date.replace(year=2025)

        for line in range(1, num_items + 1):
            if len(rows) >= target_rows:
                break

            product = random.choice(PRODUCTS)
            qty = random.randint(1, 3)

            # quality issue: negative quantity (return)
            if random.random() < 0.005:
                qty = -qty

            unit_price = product["price"]
            discount = money(unit_price * random.choice([0, 0, 0, 0.05, 0.10, 0.15]))
            line_total = money(qty * (unit_price - discount))

            row = {
                "Transaction ID": str(txn_id),
                "Line Item": line,
                "Date": txn_date.strftime("%m/%d/%Y"),
                "Member ID": member_id,
                "Store Number": store_id,
                "State": state,
                "SKU": product["sku"],
                "Product Description": product["name"],
                "Category": product["category"],
                "Quantity": qty,
                "Unit Price": f"${unit_price:.2f}",
                "Discount": f"${discount:.2f}",
                "Line Total": f"${line_total:.2f}",
                "Payment Method": payment,
            }
            rows.append(row)

            # quality issue: duplicate rows
            if random.random() < 0.002:
                rows.append(row.copy())

    df = pd.DataFrame(rows[:target_rows])
    path = os.path.join(OUTPUT_DIR, "costco", "costco_sales.csv")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    df.to_csv(path, index=False)
    print(f"Costco: {len(df)} rows -> {path}")
    return df


# ---------- Amazon ----------

def generate_amazon(target_rows=100_000):
    """
    Amazon Parquet: one row per order line.
    ISO timestamps, nested product attributes.

    Quality issues:
    - ~1% have null shipping_address fields
    - Some orders have unit_price = 0 (free promotional items)
    - ~0.5% have product_attributes as empty dict
    - Cancelled orders sometimes still have shipping info
    """
    rows = []
    order_id = 200000

    while len(rows) < target_rows:
        order_id += 1
        order_dt = rand_date()
        order_ts = order_dt.replace(
            hour=random.randint(0, 23),
            minute=random.randint(0, 59),
            second=random.randint(0, 59),
        )

        num_items = random.choices([1, 2, 3, 4], weights=[50, 30, 15, 5])[0]
        customer_id = f"ACUST{random.randint(1000000, 9999999)}"
        status = random.choices(
            ["Shipped", "Cancelled", "Returned", "Pending"],
            weights=[75, 10, 10, 5],
        )[0]

        country = random.choice(COUNTRIES)
        state = random.choice(US_STATES) if country == "US" else ""
        city = fake.city()

        # quality issue: null shipping address
        if random.random() < 0.01:
            country = None
            state = None
            city = None

        payment = random.choice(PAYMENT_METHODS)

        for line_num in range(1, num_items + 1):
            if len(rows) >= target_rows:
                break

            product = random.choice(PRODUCTS)
            qty = random.randint(1, 3)
            unit_price = product["price"]

            # quality issue: free promo item
            if random.random() < 0.005:
                unit_price = 0.0

            discount_pct = random.choices([0, 5, 10, 15, 20], weights=[60, 15, 10, 10, 5])[0]
            discount_amt = money(unit_price * qty * discount_pct / 100)
            tax = money(unit_price * qty * random.uniform(0.05, 0.10))
            shipping = money(random.choice([0, 0, 0, 5.99, 9.99, 14.99]))
            gross = money(unit_price * qty)
            net = money(gross - discount_amt + tax + shipping)

            refund_amount = 0.0
            if status == "Returned":
                refund_amount = net
            elif status == "Shipped" and random.random() < 0.03:
                refund_amount = money(net * random.choice([0.25, 0.5]))

            # product attributes (nested)
            product_attributes = {
                "color": random.choice(["Black", "White", "Silver", "Red", "Blue"]),
                "size": random.choice(["Standard", "Large", "Travel"]),
                "weight_oz": round(random.uniform(2, 48), 1),
            }

            # quality issue: empty attributes
            if random.random() < 0.005:
                product_attributes = {}

            asin = f"B{random.randint(1000000000, 9999999999)}"

            row = {
                "order_id": f"AMZ-{order_id}",
                "line_item_id": line_num,
                "order_timestamp": order_ts.isoformat(),
                "customer_id": customer_id,
                "asin": asin,
                "sku": product["sku"],
                "product_title": product["name"],
                "product_category": product["category"],
                "product_attributes": product_attributes,
                "quantity": qty,
                "unit_price": unit_price,
                "discount_amount": discount_amt,
                "tax_amount": tax,
                "shipping_amount": shipping,
                "gross_amount": gross,
                "net_amount": net,
                "refund_amount": refund_amount,
                "order_status": status,
                "payment_method": payment,
                "ship_country": country,
                "ship_state": state,
                "ship_city": city,
            }
            rows.append(row)

    df = pd.DataFrame(rows[:target_rows])
    path = os.path.join(OUTPUT_DIR, "amazon", "amazon_orders.parquet")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    df.to_parquet(path, index=False)
    print(f"Amazon: {len(df)} rows -> {path}")
    return df


# ---------- Shopify ----------

def generate_shopify(target_orders=100_000):
    """
    Shopify NDJSON: one JSON object per order, with nested line_items array.
    ISO8601 timestamps with timezone, nested customer, discount codes.

    Quality issues:
    - ~1% have null customer email
    - Some discount codes reference non-existent campaigns
    - ~0.3% orders have empty line_items array
    - A few orders have negative total_price (over-refunded)
    """
    path = os.path.join(OUTPUT_DIR, "shopify", "shopify_orders.json")
    os.makedirs(os.path.dirname(path), exist_ok=True)

    discount_codes = [
        {"code": "SAVE10", "amount": "10.00", "type": "percentage"},
        {"code": "WELCOME15", "amount": "15.00", "type": "percentage"},
        {"code": "FLAT20OFF", "amount": "20.00", "type": "fixed_amount"},
        {"code": "SUMMER25", "amount": "25.00", "type": "percentage"},
        {"code": "VIP30", "amount": "30.00", "type": "fixed_amount"},
    ]

    order_count = 0
    order_id = 300000

    with open(path, "w") as f:
        while order_count < target_orders:
            order_id += 1
            order_dt = rand_date()
            tz_offset = random.choice(["-05:00", "-06:00", "-07:00", "-08:00", "+00:00"])
            order_ts = order_dt.replace(
                hour=random.randint(0, 23),
                minute=random.randint(0, 59),
                second=random.randint(0, 59),
            )
            ts_str = order_ts.strftime(f"%Y-%m-%dT%H:%M:%S") + tz_offset

            customer_email = fake.email()
            customer_first = fake.first_name()
            customer_last = fake.last_name()
            customer_id = random.randint(5000000, 9999999)

            # quality issue: null email
            if random.random() < 0.01:
                customer_email = None

            num_items = random.choices([1, 2, 3, 4, 5], weights=[40, 30, 15, 10, 5])[0]

            # quality issue: empty line items
            if random.random() < 0.003:
                num_items = 0

            line_items = []
            subtotal = 0.0
            for li in range(1, num_items + 1):
                product = random.choice(PRODUCTS)
                qty = random.randint(1, 3)
                price = product["price"]
                line_total = money(price * qty)
                subtotal += line_total

                line_items.append({
                    "line_item_id": li,
                    "sku": product["sku"],
                    "title": product["name"],
                    "variant_title": random.choice(["Default", "Standard", "Premium"]),
                    "quantity": qty,
                    "price": str(price),
                    "total_discount": "0.00",
                    "category": product["category"],
                })

            # apply discount
            has_discount = random.random() < 0.25
            discount_applied = 0.0
            applied_discounts = []

            if has_discount and line_items:
                dc = random.choice(discount_codes)
                if dc["type"] == "percentage":
                    discount_applied = money(subtotal * float(dc["amount"]) / 100)
                else:
                    discount_applied = money(min(float(dc["amount"]), subtotal))

                applied_discounts.append(dc)

                # spread discount across line items proportionally
                for li in line_items:
                    li_share = money(discount_applied * float(li["price"]) * li["quantity"] / subtotal) if subtotal > 0 else 0
                    li["total_discount"] = str(li_share)

            # quality issue: bogus discount code
            if random.random() < 0.005:
                applied_discounts = [{"code": "EXPIRED_PROMO_2019", "amount": "0.00", "type": "percentage"}]

            tax = money(subtotal * random.uniform(0.05, 0.10))
            shipping = money(random.choice([0, 0, 0, 5.99, 7.99, 12.99]))
            total = money(subtotal - discount_applied + tax + shipping)

            # quality issue: negative total (over-refund)
            if random.random() < 0.002:
                total = money(-abs(total) * 0.1)

            status = random.choices(
                ["paid", "partially_refunded", "refunded", "pending", "voided"],
                weights=[70, 10, 8, 7, 5],
            )[0]

            country = random.choice(COUNTRIES)
            state = random.choice(US_STATES) if country == "US" else random.choice(["ON", "BC", "QC", "AB"]) if country == "CA" else ""

            order = {
                "order_id": f"SHP-{order_id}",
                "order_number": order_id,
                "created_at": ts_str,
                "updated_at": ts_str,
                "financial_status": status,
                "customer": {
                    "id": customer_id,
                    "email": customer_email,
                    "first_name": customer_first,
                    "last_name": customer_last,
                },
                "line_items": line_items,
                "subtotal_price": str(money(subtotal)),
                "total_discounts": str(money(discount_applied)),
                "total_tax": str(money(tax)),
                "total_shipping": str(money(shipping)),
                "total_price": str(money(total)),
                "discount_codes": applied_discounts,
                "shipping_address": {
                    "city": fake.city(),
                    "province": state,
                    "country": country,
                },
                "payment_method": random.choice(PAYMENT_METHODS),
            }

            f.write(json.dumps(order) + "\n")
            order_count += 1

    print(f"Shopify: {order_count} orders -> {path}")


# ---------- main ----------

if __name__ == "__main__":
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print("Generating synthetic sales data...\n")
    generate_costco()
    generate_amazon()
    generate_shopify()
    print("\nDone! Data written to:", os.path.abspath(OUTPUT_DIR))
