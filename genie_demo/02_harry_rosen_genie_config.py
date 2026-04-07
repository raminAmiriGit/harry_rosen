# Databricks notebook source
# MAGIC %md
# MAGIC #  — Genie Configuration Guide
# MAGIC
# MAGIC This notebook walks through **all Genie space configuration options**:
# MAGIC
# MAGIC | Section | What it covers |
# MAGIC |---|---|
# MAGIC | 1. Space Setup | Name, warehouse, default catalog/schema, instructions |
# MAGIC | 2. Certified SQL Queries | Pre-approved queries Genie will always use |
# MAGIC | 3. Expressions | Named reusable KPI calculations |
# MAGIC | 4. Access & Sharing | Permissions, groups, RLS |
# MAGIC | 5. Genie API | Embed Genie into the Shoppy app via REST API |
# MAGIC | 6. Feedback Loop | How to improve Genie from bad answers |

# COMMAND ----------

DB   = "ramin_serverless_aws_catalog.harry_rosen"
HOST = "https://fevm-ramin-serverless-aws.cloud.databricks.com/"

# COMMAND ----------

# MAGIC %md
# MAGIC ---
# MAGIC ## 1. Genie Space Setup
# MAGIC
# MAGIC ### Step-by-Step in the UI
# MAGIC
# MAGIC ```
# MAGIC Databricks UI → AI/BI → Genie → + New Genie space
# MAGIC ```
# MAGIC
# MAGIC | Field | Value |
# MAGIC |---|---|
# MAGIC | **Name** | ` Client & Sales Intelligence` |
# MAGIC | **Description** | `Ask questions about clients, sales, products, and advisor performance across all  stores.` |
# MAGIC | **SQL Warehouse** | `Serverless Starter Warehouse` |
# MAGIC | **Default catalog** | `ramin_aws_serverless_sandbox` |
# MAGIC | **Default schema** | `harry_rosen` |
# MAGIC
# MAGIC ### Tables to Add
# MAGIC
# MAGIC After creating the space, click **Add tables** and add:
# MAGIC ```
# MAGIC ramin_aws_serverless_sandbox.harry_rosen.stores
# MAGIC ramin_aws_serverless_sandbox.harry_rosen.advisors
# MAGIC ramin_aws_serverless_sandbox.harry_rosen.products
# MAGIC ramin_aws_serverless_sandbox.harry_rosen.clients
# MAGIC ramin_aws_serverless_sandbox.harry_rosen.transactions
# MAGIC ```

# COMMAND ----------

# MAGIC %md
# MAGIC ### Instructions Block
# MAGIC
# MAGIC Paste the following into **Instructions** in the Genie space settings.
# MAGIC This is the most important configuration — it teaches Genie Harry Rosen's business vocabulary.

# COMMAND ----------

GENIE_INSTRUCTIONS = """
 This is a luxury Canadian menswear retailer founded in 1954.

KEY BUSINESS DEFINITIONS:
- "Active client"    = last_purchase_date within the last 12 months (client_segment = 'Active')
- "VVIP client"       = is_vip = TRUE (lifetime_spend > $20,000)
- "At-Risk client"   = client_segment = 'At-Risk': a VIP who has not purchased in 6+ months
- "Dormant client"   = client_segment = 'Dormant': no purchase in over 12 months
- "New client"       = client_segment = 'New': purchased within last 6 months, fewer than 3 orders
- "Re-engaged"       = client_segment = 'Re-engaged': was dormant, has recently returned
- "Advisor"          = a  style consultant (same as "stylist")
- "Revenue"          = SUM(total_amount) from transactions WHERE is_return = FALSE
- "AOV"              = AVG(total_amount) from transactions WHERE is_return = FALSE
- "Purchase frequency" = COUNT(transaction_id) per client per year
- Membership tiers in order (lowest → highest): Classic → Silver → Gold → Platinum

STORE REGIONS:
- East:    Toronto (stores 1, 2), Ottawa (store 7), London (store 8), Montreal (store 5)
- West:    Vancouver (stores 3, 4)
- Central: Calgary (store 6)

QUERY RULES:
- When asked about "revenue", always EXCLUDE returns (is_return = FALSE)
- When asked for "top clients", sort by lifetime_spend DESC unless otherwise specified
- When asked about "at-risk" clients without further detail, filter client_segment = 'At-Risk'
- When asked about "this year", filter YEAR(transaction_date) = YEAR(CURRENT_DATE)
- When asked about "inactive", use last_purchase_date < DATE_SUB(CURRENT_DATE, 180)

TABLE RELATIONSHIPS:
- transactions.client_id  → clients.client_id
- transactions.store_id   → stores.store_id
- transactions.advisor_id → advisors.advisor_id
- transactions.product_id → products.product_id
- clients.preferred_store_id → stores.store_id
- clients.advisor_id      → advisors.advisor_id
- advisors.store_id       → stores.store_id
"""

print(GENIE_INSTRUCTIONS)

# COMMAND ----------

# MAGIC %md
# MAGIC ---
# MAGIC ## 2. Certified SQL Queries
# MAGIC
# MAGIC Certified queries are **trusted, pre-approved SQL statements** that Genie will always use
# MAGIC when it detects a matching question. They appear as pinned examples in the chat.
# MAGIC
# MAGIC ### How to Certify a Query
# MAGIC 1. Ask the question in Genie chat
# MAGIC 2. Click **"View SQL"** on the response
# MAGIC 3. Review / edit the SQL if needed
# MAGIC 4. Click **"Save as Certified Question"**
# MAGIC 5. Enter the exact question text

# COMMAND ----------

# MAGIC %md
# MAGIC ### Certified Query 1: At-Risk VIP Clients

# COMMAND ----------

# MAGIC %sql
# MAGIC -- CERTIFIED QUESTION: "Show me our at-risk VIP clients"
# MAGIC SELECT
# MAGIC   c.client_id,
# MAGIC   c.first_name || ' ' || c.last_name          AS client_name,
# MAGIC   c.email,
# MAGIC   c.membership_tier,
# MAGIC   ROUND(c.lifetime_spend, 2)                   AS lifetime_spend,
# MAGIC   c.last_purchase_date,
# MAGIC   DATEDIFF(CURRENT_DATE, c.last_purchase_date) AS days_since_purchase,
# MAGIC   c.preferred_category,
# MAGIC   a.first_name || ' ' || a.last_name           AS advisor_name,
# MAGIC   s.store_name
# MAGIC FROM ramin_aws_serverless_sandbox.harry_rosen.clients c
# MAGIC JOIN ramin_aws_serverless_sandbox.harry_rosen.advisors a ON c.advisor_id        = a.advisor_id
# MAGIC JOIN ramin_aws_serverless_sandbox.harry_rosen.stores   s ON c.preferred_store_id = s.store_id
# MAGIC WHERE c.client_segment = 'At-Risk'
# MAGIC ORDER BY c.lifetime_spend DESC

# COMMAND ----------

# MAGIC %md
# MAGIC ### Certified Query 2: Revenue by Store (Current Year)

# COMMAND ----------

# MAGIC %sql
# MAGIC -- CERTIFIED QUESTION: "Show me revenue by store this year"
# MAGIC SELECT
# MAGIC   s.store_name,
# MAGIC   s.city,
# MAGIC   s.region,
# MAGIC   ROUND(SUM(t.total_amount), 2)   AS revenue,
# MAGIC   COUNT(DISTINCT t.client_id)      AS unique_clients,
# MAGIC   ROUND(AVG(t.total_amount), 2)    AS avg_order_value,
# MAGIC   COUNT(t.transaction_id)          AS transaction_count
# MAGIC FROM ramin_aws_serverless_sandbox.harry_rosen.transactions t
# MAGIC JOIN ramin_aws_serverless_sandbox.harry_rosen.stores s ON t.store_id = s.store_id
# MAGIC WHERE t.is_return = FALSE
# MAGIC   AND YEAR(t.transaction_date) = YEAR(CURRENT_DATE)
# MAGIC GROUP BY s.store_name, s.city, s.region
# MAGIC ORDER BY revenue DESC

# COMMAND ----------

# MAGIC %md
# MAGIC ### Certified Query 3: Advisor Revenue Leaderboard

# COMMAND ----------

# MAGIC %sql
# MAGIC -- CERTIFIED QUESTION: "Who are the top performing advisors?"
# MAGIC SELECT
# MAGIC   a.first_name || ' ' || a.last_name AS advisor_name,
# MAGIC   a.specialization,
# MAGIC   s.store_name,
# MAGIC   s.city,
# MAGIC   COUNT(t.transaction_id)            AS total_transactions,
# MAGIC   ROUND(SUM(t.total_amount), 2)      AS total_revenue,
# MAGIC   ROUND(AVG(t.total_amount), 2)      AS avg_order_value,
# MAGIC   COUNT(DISTINCT t.client_id)        AS clients_served
# MAGIC FROM ramin_aws_serverless_sandbox.harry_rosen.advisors a
# MAGIC JOIN ramin_aws_serverless_sandbox.harry_rosen.transactions t ON a.advisor_id = t.advisor_id
# MAGIC JOIN ramin_aws_serverless_sandbox.harry_rosen.stores       s ON a.store_id   = s.store_id
# MAGIC WHERE t.is_return = FALSE
# MAGIC GROUP BY a.first_name, a.last_name, a.specialization, s.store_name, s.city
# MAGIC ORDER BY total_revenue DESC

# COMMAND ----------

# MAGIC %md
# MAGIC ---
# MAGIC ## 3. Expressions
# MAGIC
# MAGIC Expressions are **named, reusable calculated metrics** visible to Genie.
# MAGIC They act like virtual columns that Genie can reference by name.
# MAGIC
# MAGIC ### How to Add an Expression
# MAGIC ```
# MAGIC Genie Space Settings → Expressions tab → + Add expression
# MAGIC ```
# MAGIC Provide: Name, SQL expression, Description

# COMMAND ----------

# MAGIC %md
# MAGIC ### Expression Definitions

# COMMAND ----------

# Expressions to configure in the Genie space UI:
expressions = [
    {
        "name":        "net_revenue",
        "expression":  "SUM(CASE WHEN is_return = FALSE THEN total_amount ELSE -total_amount END)",
        "description": "Net revenue from transactions, accounting for returns. Use this instead of SUM(total_amount) when accuracy matters."
    },
    {
        "name":        "days_since_last_purchase",
        "expression":  "DATEDIFF(CURRENT_DATE, last_purchase_date)",
        "description": "Number of days since a client's most recent purchase. Useful for identifying dormant or at-risk clients."
    },
    {
        "name":        "revenue_per_sqft",
        "expression":  "SUM(t.total_amount) / s.square_footage",
        "description": "Store productivity metric: total revenue divided by store square footage. Higher = more productive store."
    },
    {
        "name":        "vip_at_risk_count",
        "expression":  "COUNT(CASE WHEN is_vip = TRUE AND client_segment = 'At-Risk' THEN 1 END)",
        "description": "Number of VIP clients who are at risk of churning. Critical KPI for the client success team."
    },
    {
        "name":        "repurchase_rate",
        "expression":  "COUNT(DISTINCT CASE WHEN total_orders > 1 THEN client_id END) * 1.0 / NULLIF(COUNT(DISTINCT client_id), 0)",
        "description": "Fraction of clients who have returned for a second purchase. Measures loyalty program effectiveness."
    },
    {
        "name":        "discount_rate",
        "expression":  "SUM(CASE WHEN discount_pct > 0 THEN 1 ELSE 0 END) * 1.0 / COUNT(*)",
        "description": "Fraction of transactions where a discount was applied."
    },
    {
        "name":        "revenue_growth_mom",
        "expression":  "(SUM(CASE WHEN MONTH(transaction_date) = MONTH(CURRENT_DATE) THEN total_amount END) - SUM(CASE WHEN MONTH(transaction_date) = MONTH(DATE_SUB(CURRENT_DATE,30)) THEN total_amount END)) / NULLIF(SUM(CASE WHEN MONTH(transaction_date) = MONTH(DATE_SUB(CURRENT_DATE,30)) THEN total_amount END), 0)",
        "description": "Month-over-month revenue growth rate."
    },
]

for e in expressions:
    print(f"Expression: {e['name']}")
    print(f"  SQL:  {e['expression']}")
    print(f"  Desc: {e['description']}")
    print()

# COMMAND ----------

# DBTITLE 1,Section 3.5 - UC Functions for Genie
# MAGIC %md
# MAGIC    
# MAGIC ---
# MAGIC ## 3.5 Unity Catalog Functions for Genie
# MAGIC
# MAGIC Unity Catalog **SQL functions** let you encapsulate business logic once and reuse it
# MAGIC across Genie certified queries, dashboards, and ad-hoc SQL.
# MAGIC
# MAGIC Because they live in Unity Catalog, Genie can call them directly — just reference
# MAGIC them in any instruction query like a built-in function.
# MAGIC
# MAGIC ### Why This Matters
# MAGIC | Benefit | Detail |
# MAGIC |---|---|
# MAGIC | **Consistency** | Every query uses the same risk / revenue logic |
# MAGIC | **Reusability** | One definition, usable in Genie, notebooks, dashboards |
# MAGIC | **Parameterisation** | Pass runtime values (dates, thresholds, regions) |
# MAGIC | **Governance** | Centrally managed in Unity Catalog with permissions |

# COMMAND ----------

# DBTITLE 1,Function 1 — classify_client_risk (scalar)
# ── Function 1: Table-Valued — classify_client_risk ──────────────────────
# Returns a single-row table with a risk label based on days since last
# purchase and lifetime spend.
# Genie requires table-valued functions for instruction queries.
#   SELECT * FROM classify_client_risk(120, 25000)  →  row with 'High-Value At-Risk'

spark.sql(f"""
CREATE OR REPLACE FUNCTION {DB}.classify_client_risk(
    p_days_since_purchase INT,
    p_lifetime_spend      DOUBLE
)
RETURNS TABLE (
    days_since_purchase INT,
    lifetime_spend      DOUBLE,
    risk_tier           STRING
)
COMMENT 'Classifies a client into a risk tier based on recency and spend. Returns a single-row table.'
RETURN
  SELECT
    p_days_since_purchase AS days_since_purchase,
    p_lifetime_spend      AS lifetime_spend,
    CASE
      WHEN p_days_since_purchase <= 90  AND p_lifetime_spend >= 20000 THEN 'Loyal VIP'
      WHEN p_days_since_purchase <= 90  AND p_lifetime_spend <  20000 THEN 'Active'
      WHEN p_days_since_purchase <= 180 AND p_lifetime_spend >= 20000 THEN 'High-Value At-Risk'
      WHEN p_days_since_purchase <= 180 AND p_lifetime_spend <  20000 THEN 'Cooling Off'
      WHEN p_days_since_purchase <= 365 AND p_lifetime_spend >= 20000 THEN 'VIP Dormant'
      WHEN p_days_since_purchase <= 365                               THEN 'Dormant'
      ELSE 'Lost'
    END AS risk_tier
""")

print(f"✅  Created {DB}.classify_client_risk(p_days_since_purchase INT, p_lifetime_spend DOUBLE) → TABLE")

# COMMAND ----------

# DBTITLE 1,Function 2 — get_revenue_by_period (table-valued)
# ── Function 2: Table-Valued — get_revenue_by_period ───────────────────
# Returns aggregated revenue metrics for a given region and date window.
# NOTE: Genie does not support DATE parameters, so we accept STRING and
#       cast to DATE inside the function body.
# Usage in SQL:
#   SELECT * FROM get_revenue_by_period('East', '2025-01-01', '2025-12-31')

spark.sql(f"""
CREATE OR REPLACE FUNCTION {DB}.get_revenue_by_period(
    p_region     STRING,
    p_start_date STRING,
    p_end_date   STRING
)
RETURNS TABLE (
    store_name        STRING,
    city              STRING,
    total_revenue     DOUBLE,
    transaction_count BIGINT,
    unique_clients    BIGINT,
    avg_order_value   DOUBLE
)
COMMENT 'Returns store-level revenue metrics for a region and date range. Dates as yyyy-MM-dd strings. Pass region = ALL for every region.'
RETURN
  SELECT
    s.store_name,
    s.city,
    ROUND(SUM(t.total_amount), 2)   AS total_revenue,
    COUNT(t.transaction_id)          AS transaction_count,
    COUNT(DISTINCT t.client_id)      AS unique_clients,
    ROUND(AVG(t.total_amount), 2)    AS avg_order_value
  FROM {DB}.transactions t
  JOIN {DB}.stores s ON t.store_id = s.store_id
  WHERE t.is_return = FALSE
    AND t.transaction_date BETWEEN CAST(p_start_date AS DATE) AND CAST(p_end_date AS DATE)
    AND (p_region = 'ALL' OR s.region = p_region)
  GROUP BY s.store_name, s.city
""")

print(f"✅  Created {DB}.get_revenue_by_period(p_region STRING, p_start_date STRING, p_end_date STRING)")

# COMMAND ----------

# DBTITLE 1,Function 3 — get_top_clients (table-valued)
# ── Function 3: Table-Valued — get_top_clients ────────────────────────
# Returns clients for a given store, ranked by lifetime spend.
# NOTE: Spark treats ROW_NUMBER() <= param as a LIMIT-like expression,
#       which requires a constant — function params are "unfoldable".
#       So we return ALL clients with a rank column; callers can filter:
#       SELECT * FROM get_top_clients(1) WHERE rank <= 10

spark.sql(f"""
CREATE OR REPLACE FUNCTION {DB}.get_top_clients(
    p_store_id INT
)
RETURNS TABLE (
    client_name        STRING,
    email              STRING,
    membership_tier    STRING,
    lifetime_spend     DOUBLE,
    total_orders       INT,
    last_purchase_date DATE,
    risk_tier          STRING,
    rank               INT
)
COMMENT 'Returns clients at a given store ranked by lifetime spend, with a risk tier. Use WHERE rank <= N to get top N.'
RETURN
  SELECT
    c.first_name || ' ' || c.last_name  AS client_name,
    c.email,
    c.membership_tier,
    ROUND(c.lifetime_spend, 2)          AS lifetime_spend,
    c.total_orders,
    c.last_purchase_date,
    r.risk_tier,
    ROW_NUMBER() OVER (ORDER BY c.lifetime_spend DESC) AS rank
  FROM {DB}.clients c,
       LATERAL {DB}.classify_client_risk(
           DATEDIFF(CURRENT_DATE, c.last_purchase_date),
           c.lifetime_spend
       ) r
  WHERE c.preferred_store_id = p_store_id
""")

print(f"✅  Created {DB}.get_top_clients(p_store_id INT)")

# COMMAND ----------

# DBTITLE 1,Example — call the functions in Genie queries
# MAGIC %sql
# MAGIC -- ── Example usage (run after creating the functions above) ─────────────
# MAGIC
# MAGIC -- 1️⃣  classify_client_risk: add risk label via LATERAL join
# MAGIC SELECT
# MAGIC   c.first_name || ' ' || c.last_name AS client_name,
# MAGIC   c.lifetime_spend,
# MAGIC   c.last_purchase_date,
# MAGIC   r.risk_tier
# MAGIC FROM ramin_aws_serverless_sandbox.harry_rosen.clients c,
# MAGIC      LATERAL ramin_aws_serverless_sandbox.harry_rosen.classify_client_risk(
# MAGIC          DATEDIFF(CURRENT_DATE, c.last_purchase_date),
# MAGIC          c.lifetime_spend
# MAGIC      ) r
# MAGIC WHERE c.is_vip = TRUE
# MAGIC ORDER BY c.lifetime_spend DESC
# MAGIC LIMIT 10

# COMMAND ----------

# DBTITLE 1,Genie instructions note
# MAGIC %md
# MAGIC    
# MAGIC    
# MAGIC ### Using These Functions in Genie
# MAGIC
# MAGIC Add the following to your **Genie Instructions** block so Genie knows the functions exist:
# MAGIC
# MAGIC ```
# MAGIC AVAILABLE UC FUNCTIONS (all table-valued):
# MAGIC - classify_client_risk(days_since_purchase INT, lifetime_spend DOUBLE) → TABLE(days_since_purchase, lifetime_spend, risk_tier)
# MAGIC   Returns a single-row table with a risk tier: 'Loyal VIP', 'Active', 'High-Value At-Risk', 'Cooling Off', 'VIP Dormant', 'Dormant', 'Lost'
# MAGIC   Example: SELECT * FROM classify_client_risk(120, 25000)
# MAGIC   With clients: SELECT c.*, r.risk_tier FROM clients c, LATERAL classify_client_risk(DATEDIFF(CURRENT_DATE, c.last_purchase_date), c.lifetime_spend) r
# MAGIC
# MAGIC - get_revenue_by_period(region STRING, start_date STRING, end_date STRING) → TABLE
# MAGIC   Returns store-level revenue for a region and date range. Pass dates as 'yyyy-MM-dd' strings. Use region = 'ALL' for all regions.
# MAGIC   Example: SELECT * FROM get_revenue_by_period('East', '2025-01-01', '2025-12-31')
# MAGIC
# MAGIC - get_top_clients(store_id INT) → TABLE
# MAGIC   Returns all clients at a store ranked by lifetime spend, with a risk tier and rank column.
# MAGIC   Use WHERE rank <= N to get the top N.  Example: SELECT * FROM get_top_clients(1) WHERE rank <= 10
# MAGIC ```
# MAGIC
# MAGIC > **Genie parameter constraints:** Only `STRING`, `INT`, `DOUBLE`, and `BOOLEAN` parameter types are supported. Use `STRING` for dates and cast inside the function. `LIMIT` and limit-like expressions (e.g. `ROW_NUMBER() <= param`) cannot use parameters — return all rows with a rank column and let callers filter.

# COMMAND ----------

# MAGIC %md
# MAGIC ---
# MAGIC ## 4. Access & Sharing
# MAGIC
# MAGIC ### Share the Genie Space
# MAGIC ```
# MAGIC Genie Space → Share (top right) → Add users or groups
# MAGIC ```
# MAGIC
# MAGIC | Role | Permission Level | Who |
# MAGIC |---|---|---|
# MAGIC | Style Advisors | **Can Ask** (chat only) | `harry_rosen_advisors` group |
# MAGIC | Store Managers | **Can Edit** (add certified questions) | `harry_rosen_managers` group |
# MAGIC | Demo Admin | **Can Manage** | `ramin.amiri@databricks.com` |
# MAGIC
# MAGIC ### Row-Level Security for Advisors
# MAGIC
# MAGIC When advisors log in, they should only see **their own clients**.
# MAGIC Set this up in Unity Catalog:

# COMMAND ----------

# NOTE: Run this only once to set up row-level security.
# It maps the logged-in Databricks user email to their advisor record.

# Create a row filter function
spark.sql(f"""
CREATE OR REPLACE FUNCTION {DB}.advisor_row_filter(advisor_id INT)
RETURNS BOOLEAN
RETURN advisor_id = (
  SELECT advisor_id
  FROM {DB}.advisors
  WHERE LOWER(first_name) || '.' || LOWER(last_name) || '@harryrosen.com' = LOWER(CURRENT_USER())
  LIMIT 1
)
""")

print("Row filter function created.")
print("NOTE: To apply to clients table, run:")
print(f"  ALTER TABLE {DB}.clients SET ROW FILTER {DB}.advisor_row_filter ON (advisor_id);")
print(f"  ALTER TABLE {DB}.transactions SET ROW FILTER {DB}.advisor_row_filter ON (advisor_id);")

# COMMAND ----------

# MAGIC %md
# MAGIC > **Important:** Apply the row filter only in production.
# MAGIC > For the demo with Jay Sewell, keep RLS off so you can see all data freely.
# MAGIC > To remove: `ALTER TABLE {DB}.clients DROP ROW FILTER;`

# COMMAND ----------

# MAGIC %sql
# MAGIC ALTER TABLE {DB}.clients DROP ROW FILTER;

# COMMAND ----------

# DBTITLE 1,Section 4.5 — UC Governance Flows into Genie
# MAGIC %md
# MAGIC ---
# MAGIC ## 4.5  Unity Catalog Governance → Genie Enforcement
# MAGIC
# MAGIC Genie executes SQL **as the logged-in user**. That means every Unity Catalog
# MAGIC access control — column masks, row filters, grants — is enforced automatically.
# MAGIC
# MAGIC | UC Control | What happens in Genie |
# MAGIC |---|---|
# MAGIC | **Column Mask** on `email` | Genie query returns `***@***.***` instead of the real address |
# MAGIC | **Column Mask** on `lifetime_spend` | Genie query returns `NULL` — user never sees the dollar amount |
# MAGIC | **Row Filter** on `clients` | Genie query only returns rows the user is allowed to see |
# MAGIC | **REVOKE SELECT** on a column | Genie gets `INSUFFICIENT_PERMISSIONS` — same as a direct query |
# MAGIC
# MAGIC > **Key takeaway:** You do NOT need to configure anything extra in Genie.
# MAGIC > Governance is enforced at the **catalog layer**, not the app layer.
# MAGIC
# MAGIC Below we demonstrate this with your own user (`ramin.amiri@databricks.com`).

# COMMAND ----------

# DBTITLE 1,Step 1 — BEFORE: query clients without restrictions
# ── Step 1: BEFORE — see full data with no masks or filters ─────────────
# Run this FIRST to see the unrestricted baseline.

df_before = spark.sql(f"""
SELECT
  client_id,
  first_name || ' ' || last_name AS client_name,
  email,
  city,
  membership_tier,
  lifetime_spend,
  client_segment
FROM {DB}.clients
WHERE is_vip = TRUE
ORDER BY lifetime_spend DESC
LIMIT 10
""")

print("🔓 BEFORE — No column masks or row filters applied:")
display(df_before)

# COMMAND ----------

# DBTITLE 1,Step 2 — Create column mask functions
# ── Step 2: Create column mask functions ────────────────────────────────
# These functions decide what value to return for a masked column.
# If the querying user is ramin.amiri@databricks.com → mask the data.
# Everyone else (e.g. admins) sees the real value.

# Mask 1: Redact email → '***@***.***'
spark.sql(f"""
CREATE OR REPLACE FUNCTION {DB}.mask_email(email STRING)
RETURNS STRING
COMMENT 'Redacts email for ramin.amiri@databricks.com; others see the real value.'
RETURN
  CASE
    WHEN LOWER(CURRENT_USER()) = 'ramin.amiri@databricks.com'
    THEN '***@***.***'
    ELSE email
  END
""")
print(f"✅ Created {DB}.mask_email")

# Mask 2: Hide lifetime_spend → NULL
spark.sql(f"""
CREATE OR REPLACE FUNCTION {DB}.mask_lifetime_spend(spend DOUBLE)
RETURNS DOUBLE
COMMENT 'Returns NULL for ramin.amiri@databricks.com; others see the real spend.'
RETURN
  CASE
    WHEN LOWER(CURRENT_USER()) = 'ramin.amiri@databricks.com'
    THEN NULL
    ELSE spend
  END
""")
print(f"✅ Created {DB}.mask_lifetime_spend")

# COMMAND ----------

# DBTITLE 1,Step 3 — Create row filter function
# # ── Step 3: Create row filter function ──────────────────────────────────
# # This function restricts ramin.amiri@databricks.com to only see
# # Toronto clients. Everyone else sees all rows.

# spark.sql(f"""
# CREATE OR REPLACE FUNCTION {DB}.city_row_filter(city STRING)
# RETURNS BOOLEAN
# COMMENT 'ramin.amiri@databricks.com can only see Toronto clients; others see all.'
# RETURN
#   CASE
#     WHEN LOWER(CURRENT_USER()) = 'ramin.amiri@databricks.com'
#     THEN city = 'Toronto'
#     ELSE TRUE
#   END
# """)
# print(f"✅ Created {DB}.city_row_filter")

# COMMAND ----------

# DBTITLE 1,Step 4 — Apply masks and row filter to clients table
# ── Step 4: Apply column masks + row filter to the clients table ────────
# After this, YOUR queries (ramin.amiri@databricks.com) will see:
#   • email       → '***@***.***'
#   • lifetime_spend → NULL
#   • only rows where city = 'Toronto'

spark.sql(f"""
ALTER TABLE {DB}.clients
  ALTER COLUMN email
  SET MASK {DB}.mask_email
""")
print(f"✅ Column mask applied: email → mask_email")

# spark.sql(f"""
# ALTER TABLE {DB}.clients
#   ALTER COLUMN lifetime_spend
#   SET MASK {DB}.mask_lifetime_spend
# """)
# print(f"✅ Column mask applied: lifetime_spend → mask_lifetime_spend")

# spark.sql(f"""
# ALTER TABLE {DB}.clients
#   SET ROW FILTER {DB}.city_row_filter ON (city)
# """)
# print(f"✅ Row filter applied: city_row_filter(city)")
# print(f"\n🔒 All governance controls are now active on {DB}.clients")

# COMMAND ----------

# DBTITLE 1,Step 5 — AFTER: same query now shows masked/filtered data
# ── Step 5: AFTER — run the EXACT same query ────────────────────────────
# Compare with Step 1. You should see:
#   • email       = '***@***.***'     (column mask)
#   • lifetime_spend = NULL            (column mask)
#   • ONLY Toronto clients             (row filter)
#
# If a Genie user asks "Show me VIP clients", Genie runs the same SQL
# and gets the same masked/filtered result — governance is automatic.

df_after = spark.sql(f"""
SELECT
  client_id,
  first_name || ' ' || last_name AS client_name,
  email,
  city,
  membership_tier,
  lifetime_spend,
  client_segment
FROM {DB}.clients
WHERE is_vip = TRUE
ORDER BY lifetime_spend DESC
LIMIT 10
""")

print("🔒 AFTER — Column masks + row filter active:")
print("   • email is redacted")
print("   • lifetime_spend is NULL")
print("   • only Toronto clients visible")
print("   • Genie inherits ALL of these restrictions")
display(df_after)

# COMMAND ----------

# DBTITLE 1,Genie enforcement explanation
# MAGIC %md
# MAGIC ### What This Means for Genie
# MAGIC
# MAGIC When `ramin.amiri@databricks.com` opens the Genie space and asks:
# MAGIC
# MAGIC > *"Show me our VIP clients"*
# MAGIC
# MAGIC Genie generates and runs SQL **as that user**. Unity Catalog intercepts the query and:
# MAGIC
# MAGIC 1. **Column mask on `email`** → every email value becomes `***@***.***`
# MAGIC 2. **Column mask on `lifetime_spend`** → every spend value becomes `NULL`
# MAGIC 3. **Row filter on `city`** → only Toronto clients are returned
# MAGIC
# MAGIC The user sees a valid table — no error, no empty result — but **sensitive data is hidden**.
# MAGIC They don't even know the data exists.
# MAGIC
# MAGIC > **No Genie configuration is needed.** The same UC policies apply whether the user
# MAGIC > runs a query in a notebook, a dashboard, the SQL editor, or Genie.

# COMMAND ----------

# DBTITLE 1,Step 6 — CLEANUP: remove all masks and filters
# ── Step 6: CLEANUP — remove everything so the rest of the demo works ───
# ⚠️  Run this cell to restore full access after the governance demo.

spark.sql(f"ALTER TABLE {DB}.clients ALTER COLUMN email DROP MASK")
print("✅ Removed column mask from email")

spark.sql(f"ALTER TABLE {DB}.clients ALTER COLUMN lifetime_spend DROP MASK")
print("✅ Removed column mask from lifetime_spend")

spark.sql(f"ALTER TABLE {DB}.clients DROP ROW FILTER")
print("✅ Removed row filter from clients")

print(f"\n🔓 {DB}.clients is back to full, unrestricted access.")

# COMMAND ----------

# MAGIC %md
# MAGIC ---
# MAGIC ## 5. Genie Conversations API
# MAGIC
# MAGIC Embed Genie inside the existing **Shoppy / hr-intel-app** so advisors can ask questions
# MAGIC from within the mobile app — no context switching to Databricks UI.
# MAGIC
# MAGIC ### API Flow
# MAGIC ```
# MAGIC POST  /api/2.0/genie/spaces/{space_id}/start-conversation   → get conversation_id
# MAGIC GET   /api/2.0/genie/spaces/{space_id}/conversations/{id}/messages/{msg_id}  → poll result
# MAGIC POST  /api/2.0/genie/spaces/{space_id}/conversations/{id}/messages           → follow-up
# MAGIC ```

# COMMAND ----------

import requests, json, time

# Fill in your Genie Space ID after creating it in the UI
# (found in the URL: /genie/spaces/<SPACE_ID>)
GENIE_SPACE_ID = "<your-genie-space-id>"   # replace after creating the space

def get_token():
    import subprocess
    r = subprocess.run(
        ["databricks", "--profile", "ramin-aws-sandbox", "auth", "token"],
        capture_output=True, text=True
    )
    return json.loads(r.stdout)["access_token"]

def ask_genie(question: str, conversation_id: str = None) -> dict:
    """
    Ask Genie a question. Optionally continue an existing conversation.
    Returns: { conversation_id, message_id, sql, result_table }
    """
    token = get_token()
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    if conversation_id is None:
        # Start new conversation
        resp = requests.post(
            f"{HOST}/api/2.0/genie/spaces/{GENIE_SPACE_ID}/start-conversation",
            headers=headers,
            json={"content": question}
        )
        resp.raise_for_status()
        data = resp.json()
        conversation_id = data["conversation_id"]
        message_id      = data["message_id"]
    else:
        # Continue existing conversation
        resp = requests.post(
            f"{HOST}/api/2.0/genie/spaces/{GENIE_SPACE_ID}/conversations/{conversation_id}/messages",
            headers=headers,
            json={"content": question}
        )
        resp.raise_for_status()
        data       = resp.json()
        message_id = data["id"]

    # Poll until complete
    for _ in range(30):
        msg_resp = requests.get(
            f"{HOST}/api/2.0/genie/spaces/{GENIE_SPACE_ID}/conversations/{conversation_id}/messages/{message_id}",
            headers=headers
        )
        msg_resp.raise_for_status()
        msg = msg_resp.json()
        state = msg.get("status", "")
        if state in ("COMPLETED", "FAILED", "CANCELLED"):
            break
        time.sleep(2)

    return {
        "conversation_id": conversation_id,
        "message_id":      message_id,
        "status":          msg.get("status"),
        "attachments":     msg.get("attachments", []),
        "sql":             next((a.get("query", {}).get("query") for a in msg.get("attachments", []) if "query" in a), None)
    }

# Example usage (replace GENIE_SPACE_ID first):
if GENIE_SPACE_ID != "<your-genie-space-id>":
    result = ask_genie("Who are my top 10 clients by lifetime spend?")
    print(f"Conversation ID: {result['conversation_id']}")
    print(f"Generated SQL:\n{result['sql']}")

    # Follow-up question (same conversation = Genie remembers context)
    result2 = ask_genie(
        "Of those, which haven't purchased in the last 3 months?",
        conversation_id=result["conversation_id"]
    )
    print(f"\nFollow-up SQL:\n{result2['sql']}")
else:
    print("Set GENIE_SPACE_ID to test the API. Found in the Genie space URL.")

# COMMAND ----------

# MAGIC %md
# MAGIC ### JavaScript / React Integration (for Shoppy App)
# MAGIC
# MAGIC Add this to the Shoppy frontend (`client/src/hooks/useGenie.ts`):
# MAGIC
# MAGIC ```typescript
# MAGIC const GENIE_SPACE_ID = process.env.GENIE_SPACE_ID;
# MAGIC const DATABRICKS_HOST = process.env.DATABRICKS_HOST;
# MAGIC
# MAGIC export async function askGenie(question: string, conversationId?: string) {
# MAGIC   const endpoint = conversationId
# MAGIC     ? `${DATABRICKS_HOST}/api/2.0/genie/spaces/${GENIE_SPACE_ID}/conversations/${conversationId}/messages`
# MAGIC     : `${DATABRICKS_HOST}/api/2.0/genie/spaces/${GENIE_SPACE_ID}/start-conversation`;
# MAGIC
# MAGIC   const resp = await fetch(endpoint, {
# MAGIC     method: 'POST',
# MAGIC     headers: { 'Authorization': `Bearer ${await getToken()}`, 'Content-Type': 'application/json' },
# MAGIC     body: JSON.stringify({ content: question })
# MAGIC   });
# MAGIC   const data = await resp.json();
# MAGIC   const convId = conversationId ?? data.conversation_id;
# MAGIC   const msgId  = conversationId ? data.id : data.message_id;
# MAGIC
# MAGIC   // Poll for result
# MAGIC   return pollGenieMessage(convId, msgId);
# MAGIC }
# MAGIC ```

# COMMAND ----------

# MAGIC %md
# MAGIC ---
# MAGIC ## 6. Feedback Loop — Improving Genie Over Time
# MAGIC
# MAGIC ### How the Feedback Loop Works
# MAGIC
# MAGIC ```
# MAGIC User asks question
# MAGIC       ↓
# MAGIC Genie generates SQL + answer
# MAGIC       ↓
# MAGIC User thumbs up ✅  →  Genie learns this pattern is correct
# MAGIC User thumbs down ❌ →  Admin reviews in Feedback tab
# MAGIC       ↓
# MAGIC Admin clicks "Edit SQL" → fixes the query → clicks "Certify"
# MAGIC       ↓
# MAGIC Next user asking similar question gets the certified (correct) answer
# MAGIC ```
# MAGIC
# MAGIC ### Accessing the Feedback Tab
# MAGIC ```
# MAGIC Genie Space → Feedback (tab in top nav)
# MAGIC ```
# MAGIC Shows all rated responses — click any thumbs-down to review and fix.
# MAGIC
# MAGIC ### Common Reasons Genie Gets It Wrong + Fixes
# MAGIC
# MAGIC | Problem | Root Cause | Fix |
# MAGIC |---|---|---|
# MAGIC | Includes returns in revenue | Missing `is_return = FALSE` | Add to instructions: "Revenue always excludes returns" |
# MAGIC | "At-risk" matches wrong segment | Ambiguous term | Define explicitly in instructions |
# MAGIC | Wrong join between tables | Missing FK context | Add table relationships to instructions |
# MAGIC | "This year" uses wrong date | Default date logic | Certify a query with `YEAR(CURRENT_DATE)` |
# MAGIC | Wrong aggregation level | Missing GROUP BY | Certify the correct query |

# COMMAND ----------

# MAGIC %md
# MAGIC ---
# MAGIC ## Summary Checklist
# MAGIC
# MAGIC **One-time setup (before the demo):**
# MAGIC - [x] Run `00_harry_rosen_data_setup` — creates all 5 tables
# MAGIC - [ ] Create Genie space in UI with the settings above
# MAGIC - [ ] Paste the instructions block
# MAGIC - [ ] Add all 5 tables
# MAGIC - [ ] Certify 3 queries (At-Risk VIPs, Revenue by Store, Advisor Leaderboard)
# MAGIC - [ ] Add 5+ expressions
# MAGIC - [ ] Test Q1–Q5 (Tier 1 warm-up questions)
# MAGIC
# MAGIC **During the demo:**
# MAGIC - [ ] Start with Q1 (total revenue) — instant, impressive
# MAGIC - [ ] Build to Q7 (At-Risk VIP list) — the "wow" moment
# MAGIC - [ ] Show Q11 conversational follow-up — Genie remembers context
# MAGIC - [ ] Hand keyboard to Jay for Q16 (his own advisor book of business)
# MAGIC - [ ] Show Edit SQL + Certify workflow on any imperfect answer
# MAGIC
# MAGIC **Post-demo:**
# MAGIC - [ ] Share Genie space link with Jay
# MAGIC - [ ] Enable RLS if going to production
# MAGIC - [ ] Integrate API into Shoppy if desired
