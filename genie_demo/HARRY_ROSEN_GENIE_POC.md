# Harry Rosen — Databricks Genie POC Runbook

**Client:** Harry Rosen
**Contact:** Jay Sewell
**Workspace:** `fe-sandbox-ramin-aws-serverless-sandbox.cloud.databricks.com`
**Catalog / Schema:** `ramin_aws_serverless_sandbox.harry_rosen`

---

## Table of Contents

1. [Step 1 — Grant Access to the Workspace](#step-1--grant-access-to-the-workspace)
2. [Step 2 — Generate the Demo Data](#step-2--generate-the-demo-data)
3. [Step 3 — Create the Genie Space](#step-3--create-the-genie-space)
4. [Step 4 — Run Questions Without Configuration (Baseline)](#step-4--run-questions-without-configuration-baseline)
5. [Step 5 — Add Configuration and Instructions](#step-5--add-configuration-and-instructions)
6. [Step 6 — Monitoring](#step-6--monitoring)
7. [Step 7 — Benchmarks](#step-7--benchmarks)

---

## Step 1 — Grant Access to the Workspace

Before anything else, the Harry Rosen team needs access to the Databricks workspace so they can view notebooks, query data, and eventually use the Genie space.

### 1.1 Add Users to the Workspace

1. Go to **Settings → Identity & Access → Users**
2. Click **Add User**
3. Enter the email address (e.g. `jay.sewell@harryrosen.com`)
4. Assign the role: **User** (not Admin)
5. Click **Send Invite**

Repeat for each Harry Rosen team member attending the POC.

> **Tip:** If Harry Rosen has an existing SSO / identity provider (Okta, Azure AD), ask your Databricks account team to enable SCIM provisioning — this lets them manage users automatically without manual invites.

### 1.2 Grant Unity Catalog Permissions

After the user is added to the workspace, grant access to the demo catalog and schema:

```sql
-- Grant access to browse the catalog
GRANT USE CATALOG ON CATALOG ramin_aws_serverless_sandbox TO `jay.sewell@harryrosen.com`;

-- Grant access to the schema
GRANT USE SCHEMA ON SCHEMA ramin_aws_serverless_sandbox.harry_rosen TO `jay.sewell@harryrosen.com`;

-- Grant read access to all demo tables
GRANT SELECT ON TABLE ramin_aws_serverless_sandbox.harry_rosen.stores       TO `jay.sewell@harryrosen.com`;
GRANT SELECT ON TABLE ramin_aws_serverless_sandbox.harry_rosen.advisors     TO `jay.sewell@harryrosen.com`;
GRANT SELECT ON TABLE ramin_aws_serverless_sandbox.harry_rosen.products     TO `jay.sewell@harryrosen.com`;
GRANT SELECT ON TABLE ramin_aws_serverless_sandbox.harry_rosen.clients      TO `jay.sewell@harryrosen.com`;
GRANT SELECT ON TABLE ramin_aws_serverless_sandbox.harry_rosen.transactions TO `jay.sewell@harryrosen.com`;
```

> **For a group of users:** Create a Unity Catalog group first (`harry_rosen_poc`), add all users to it, then grant to the group instead of each user individually.

```sql
-- Create group and add members
CREATE GROUP `harry_rosen_poc`;

-- Grant permissions to the group (cleaner for multi-user POCs)
GRANT USE CATALOG ON CATALOG ramin_aws_serverless_sandbox TO `harry_rosen_poc`;
GRANT USE SCHEMA  ON SCHEMA  ramin_aws_serverless_sandbox.harry_rosen TO `harry_rosen_poc`;
GRANT SELECT ON TABLE ramin_aws_serverless_sandbox.harry_rosen.clients      TO `harry_rosen_poc`;
GRANT SELECT ON TABLE ramin_aws_serverless_sandbox.harry_rosen.transactions TO `harry_rosen_poc`;
GRANT SELECT ON TABLE ramin_aws_serverless_sandbox.harry_rosen.products     TO `harry_rosen_poc`;
GRANT SELECT ON TABLE ramin_aws_serverless_sandbox.harry_rosen.advisors     TO `harry_rosen_poc`;
GRANT SELECT ON TABLE ramin_aws_serverless_sandbox.harry_rosen.stores       TO `harry_rosen_poc`;
```

### 1.3 Share the Data Setup Notebook

Share the notebook path with the team so they can follow along:

```
/Workspace/Users/ramin.amiri@databricks.com/harry_rosen/genie_demo/00_harry_rosen_data_setup
```

1. Open the notebook in the Databricks UI
2. Click **Share** (top right)
3. Add `jay.sewell@harryrosen.com` with **Can View** permission
4. Copy the link and share it with the team

---

## Step 2 — Generate the Demo Data

This step creates all five Harry Rosen tables in Unity Catalog using realistic luxury retail synthetic data.

### 2.1 Open the Setup Notebook

Navigate to:
```
/Workspace/Users/ramin.amiri@databricks.com/harry_rosen/genie_demo/00_harry_rosen_data_setup
```

### 2.2 Review What Will Be Created

| Table | Rows | Description |
|---|---|---|
| `stores` | 8 | Canadian retail locations (Toronto, Vancouver, Montreal, Calgary, Ottawa, London) |
| `advisors` | 20 | Style advisors with specialization, YTD revenue, client count |
| `products` | 40 | Full luxury SKU catalogue — Suits, Shirts, Shoes, Outerwear, Accessories, Trousers |
| `clients` | 250 | Client profiles with VIP flag, loyalty tier, segment, lifetime spend |
| `transactions` | ~3,800 | Two years of point-of-sale history with discount, advisor, and return data |

### 2.3 Configure the Catalog Target

At the top of the notebook, update if running in a different workspace:

```python
CATALOG = "ramin_aws_serverless_sandbox"   # change if needed
SCHEMA  = "harry_rosen"
```

### 2.4 Run All Cells

Click **Run All** and wait approximately 2–3 minutes. Each section will print a row count confirmation:

```
Inserted 8 stores
Inserted 20 advisors
Inserted 40 products
Inserted 250 clients
Inserted 3830 transactions
```

### 2.5 Verify in the Catalog Explorer

1. Click **Catalog** in the left sidebar
2. Navigate to `ramin_aws_serverless_sandbox` → `harry_rosen`
3. Confirm all 5 tables appear
4. Click any table → **Sample Data** tab to preview rows

> **Talk track for Jay:** "All of this data lives in Unity Catalog — your single governed data layer. Every table has column-level comments, data types, and lineage tracked automatically. Genie will read this metadata to understand your data model."

---

## Step 3 — Create the Genie Space

### 3.1 Navigate to Genie

```
Left sidebar → AI/BI → Genie → + New Genie space
```

### 3.2 Basic Configuration

Fill in the following fields:

| Field | Value |
|---|---|
| **Name** | `Harry Rosen Client & Sales Intelligence` |
| **Description** | `Ask questions about clients, sales performance, product trends, and advisor effectiveness across all Harry Rosen stores.` |
| **SQL Warehouse** | `Serverless Starter Warehouse` |
| **Default catalog** | `ramin_aws_serverless_sandbox` |
| **Default schema** | `harry_rosen` |

Click **Create**.

### 3.3 Add Tables

Inside the newly created space, click **Add tables** and add all five tables:

```
ramin_aws_serverless_sandbox.harry_rosen.stores
ramin_aws_serverless_sandbox.harry_rosen.advisors
ramin_aws_serverless_sandbox.harry_rosen.products
ramin_aws_serverless_sandbox.harry_rosen.clients
ramin_aws_serverless_sandbox.harry_rosen.transactions
```

> **Why adding tables matters:** Genie only generates SQL against tables you explicitly add. Adding more tables with good column comments significantly improves answer quality without any other configuration.

### 3.4 Share the Genie Space with the Team

1. Click **Share** in the top-right corner of the Genie space
2. Add `jay.sewell@harryrosen.com` with **Can Ask** permission
3. Copy the Genie space link and share it

> **Permission levels explained:**
> - **Can Ask** — chat only, cannot edit settings or certify queries (right for end users)
> - **Can Edit** — can add certified questions and expressions (right for power users)
> - **Can Manage** — full admin access (right for the SA)

---

## Step 4 — Run Questions Without Configuration (Baseline)

Before adding any instructions or certified queries, run a set of questions to establish a **baseline** of Genie's out-of-the-box accuracy. This is important for two reasons:

1. It shows the client what Genie can do with zero setup
2. It creates a comparison point to show improvement after configuration in Step 5

> **Important:** Do NOT add instructions or certified queries before this step. You want to capture raw performance.

### 4.1 Baseline Questions to Ask

Open the Genie space and ask each of these questions exactly as written. Note whether the result is ✅ correct, ⚠️ partially correct, or ❌ wrong.

#### Simple Aggregations

| # | Question | What to look for |
|---|---|---|
| B1 | `What is our total revenue this year?` | Should exclude returns; check if it filters `is_return = FALSE` |
| B2 | `How many VIP clients do we have?` | Should filter `is_vip = TRUE`; note how it interprets "VIP" |
| B3 | `Show me the top 5 products by revenue` | Should join transactions → products |
| B4 | `Which store makes the most money?` | Should join transactions → stores |
| B5 | `How many clients are at risk?` | Check if it uses `client_segment = 'At-Risk'` or tries to infer it |

#### Business Intelligence (Multi-Table)

| # | Question | What to look for |
|---|---|---|
| B6 | `Who are my at-risk VIP clients?` | Does it combine `is_vip = TRUE` AND `client_segment = 'At-Risk'`? |
| B7 | `Compare revenue between Toronto and Vancouver` | Does it correctly group by city via store join? |
| B8 | `Which advisor has the highest average order value?` | Requires join: transactions → advisors |
| B9 | `Show me clients who haven't purchased in 6 months` | Does it use `last_purchase_date` or query transactions? |
| B10 | `What is our return rate by category?` | Requires `is_return = TRUE` filter and join to products |

### 4.2 Record the Results

Use this table to track baseline accuracy during the demo:

| Question | Result | Notes |
|---|---|---|
| B1 | ✅ / ⚠️ / ❌ | |
| B2 | ✅ / ⚠️ / ❌ | |
| B3 | ✅ / ⚠️ / ❌ | |
| B4 | ✅ / ⚠️ / ❌ | |
| B5 | ✅ / ⚠️ / ❌ | |
| B6 | ✅ / ⚠️ / ❌ | |
| B7 | ✅ / ⚠️ / ❌ | |
| B8 | ✅ / ⚠️ / ❌ | |
| B9 | ✅ / ⚠️ / ❌ | |
| B10 | ✅ / ⚠️ / ❌ | |

> **Talk track for Jay:** "What you're seeing here is Genie with zero configuration — just the tables and their column names. Some answers are already correct because Unity Catalog column comments give Genie enough context. The next step shows how a few minutes of configuration dramatically improves accuracy."

---

## Step 5 — Add Configuration and Instructions

This is the highest-leverage step. Genie's configuration has four areas: **About**, **Data**, **Instructions**, and **SQL**. Each one addresses a different layer of context.

### 5.1 About Section

**Where:** Genie Space Settings → **About** tab

The About section defines the **identity and audience** of the Genie space. It is surfaced to users when they open the space for the first time and helps them understand what questions to ask.

Fill in:

- **Title:** `Harry Rosen Client & Sales Intelligence`
- **Summary:** `This Genie space gives Harry Rosen store managers, style advisors, and merchandising teams instant answers about client behaviour, sales performance, product trends, and advisor effectiveness — no SQL required.`
- **Example questions to suggest to users:**
  - Who are my at-risk VIP clients?
  - What was our revenue by store this month?
  - Which advisor closed the most sales this quarter?
  - Show me clients who bought suits but never bought shoes.
  - What is our top-selling brand?

> **Why this section matters:** The About section sets user expectations, reduces "I don't know what to ask" friction, and surfaces the most valuable questions immediately. It's the onboarding experience for non-technical users.

---

### 5.2 Data Section

**Where:** Genie Space Settings → **Data** tab

The Data section shows which Unity Catalog tables are connected to the Genie space. Beyond adding tables, you can add **table-level descriptions** that supplement or override Unity Catalog comments.

**Review and update descriptions for each table:**

| Table | Add/Confirm Description |
|---|---|
| `stores` | `Physical Harry Rosen retail locations across Canada. Contains region, square footage, and manager info.` |
| `advisors` | `Style advisors (also called stylists) employed at Harry Rosen. Each advisor belongs to one store. YTD revenue and client count are pre-aggregated.` |
| `products` | `Harry Rosen SKU catalogue. Category is the top-level grouping (Suits, Shirts, etc.). Unit price is retail price in CAD.` |
| `clients` | `Harry Rosen client profiles. is_vip and client_segment are key fields for identifying high-value and at-risk clients.` |
| `transactions` | `Point-of-sale history for the past two years. Always filter is_return = FALSE when calculating revenue. Join to all other tables via foreign keys.` |

> **Why this section matters:** Table descriptions are the most direct way to give Genie business context about each dataset. Well-written descriptions reduce join errors and field misinterpretation — especially for tables with ambiguous column names like `total_amount` or `segment`.

---

### 5.3 Instructions Section

**Where:** Genie Space Settings → **Instructions** tab

Instructions are the most powerful configuration lever. They teach Genie the business vocabulary, calculation rules, and query patterns specific to Harry Rosen. Instructions are organized into four parts.

---

#### Part 1 — General Instructions

> **Why:** General instructions define business terminology and calculation rules that apply across all questions. Without them, Genie will guess at the meaning of terms like "VIP", "at-risk", or "revenue" — often incorrectly.

```
Harry Rosen is a luxury Canadian menswear retailer founded in 1954.

KEY BUSINESS DEFINITIONS:
- "Active client"    = client whose last_purchase_date is within the last 12 months
- "VIP client"       = is_vip = TRUE (lifetime_spend > $10,000 or manually flagged)
- "At-Risk client"   = client_segment = 'At-Risk': a VIP who has not purchased in 6+ months
- "Dormant client"   = client_segment = 'Dormant': no purchase in over 12 months
- "New client"       = client_segment = 'New': purchased within the last 6 months, fewer than 3 orders
- "Re-engaged"       = client_segment = 'Re-engaged': was dormant, has recently returned
- "Advisor"          = Harry Rosen style consultant — same as "stylist" in this dataset
- "Revenue"          = SUM(total_amount) WHERE is_return = FALSE
- "AOV"              = AVG(total_amount) WHERE is_return = FALSE
- "Purchase frequency" = COUNT(transaction_id) per client per calendar year
- Membership tiers ranked lowest to highest: Classic → Silver → Gold → Platinum

STORE REGIONS:
- East:    Toronto (stores 1, 2), Ottawa (store 7), London (store 8), Montreal (store 5)
- West:    Vancouver (stores 3, 4)
- Central: Calgary (store 6)

DEFAULT QUERY RULES:
- Always EXCLUDE returns (is_return = FALSE) when calculating revenue or transaction counts
- When asked for "top clients", sort by lifetime_spend DESC unless otherwise specified
- When asked about "at-risk" without further detail, filter client_segment = 'At-Risk'
- When asked about "this year", filter YEAR(transaction_date) = YEAR(CURRENT_DATE)
- When asked about "inactive", use last_purchase_date < DATE_SUB(CURRENT_DATE, 180)
- "High-value" clients means lifetime_spend > $20,000 unless a threshold is specified
```

---

#### Part 2 — Joins

> **Why:** Multi-table queries are the most common source of Genie errors. Explicitly documenting how tables relate to each other — and which joins are safe — prevents Genie from producing cross-joins, missing rows, or using the wrong key.

```
TABLE RELATIONSHIPS (Foreign Keys):

transactions.client_id       → clients.client_id
transactions.store_id        → stores.store_id
transactions.advisor_id      → advisors.advisor_id
transactions.product_id      → products.product_id
clients.preferred_store_id   → stores.store_id
clients.advisor_id           → advisors.advisor_id
advisors.store_id            → stores.store_id

JOIN GUIDANCE:
- To get client details for a transaction: JOIN clients ON transactions.client_id = clients.client_id
- To get store details for a transaction: JOIN stores ON transactions.store_id = stores.store_id
- To get advisor name for a transaction: JOIN advisors ON transactions.advisor_id = advisors.advisor_id
- To get product details for a transaction: JOIN products ON transactions.product_id = products.product_id
- To get an advisor's store: JOIN stores ON advisors.store_id = stores.store_id
- To get a client's preferred store: JOIN stores ON clients.preferred_store_id = stores.store_id

IMPORTANT:
- The transactions table is the central fact table — most revenue and activity queries start here
- advisors.client_count is a pre-aggregated snapshot, not a live count from transactions
- For live client counts per advisor, COUNT(DISTINCT transactions.client_id) grouped by advisor_id
```

---

#### Part 3 — Common SQL Expressions

> **Why:** Repeated calculations (revenue, AOV, days inactive) should be standardized across all answers. Without this, Genie may calculate the same metric differently in different questions, producing inconsistent results that confuse business users.

```
STANDARD EXPRESSIONS TO USE:

Revenue (net of returns):
  SUM(CASE WHEN is_return = FALSE THEN total_amount ELSE 0 END)

Net revenue (credits returns as negative):
  SUM(CASE WHEN is_return = FALSE THEN total_amount ELSE -total_amount END)

Average Order Value (AOV):
  AVG(CASE WHEN is_return = FALSE THEN total_amount END)

Days since last purchase (per client):
  DATEDIFF(CURRENT_DATE, last_purchase_date)

Month-over-month revenue growth:
  (current_month_revenue - prior_month_revenue) / NULLIF(prior_month_revenue, 0)

Discount rate (% of transactions with a discount):
  SUM(CASE WHEN discount_pct > 0 THEN 1 ELSE 0 END) * 100.0 / COUNT(*)

Revenue per square foot (store productivity):
  SUM(t.total_amount) / s.square_footage

Return rate:
  SUM(CASE WHEN is_return = TRUE THEN 1 ELSE 0 END) * 100.0 / COUNT(*)

VIP at-risk count:
  COUNT(CASE WHEN is_vip = TRUE AND client_segment = 'At-Risk' THEN 1 END)

Repurchase rate (% of clients who returned):
  COUNT(DISTINCT CASE WHEN total_orders > 1 THEN client_id END) * 1.0
  / NULLIF(COUNT(DISTINCT client_id), 0)
```

---

#### Part 4 — SQL Queries and Functions

> **Why:** Some business questions require specific SQL patterns (CTEs, window functions, conditional aggregations) that Genie may not use by default. Specifying preferred patterns ensures results are accurate, readable, and consistent with how your team thinks about the data.

```
PREFERRED SQL PATTERNS:

Date filtering:
  - "This year"    → YEAR(transaction_date) = YEAR(CURRENT_DATE)
  - "Last 12 months" → transaction_date >= DATE_SUB(CURRENT_DATE, 365)
  - "Last 6 months"  → transaction_date >= DATE_SUB(CURRENT_DATE, 180)
  - "Last 90 days"   → transaction_date >= DATE_SUB(CURRENT_DATE, 90)

Month-level grouping:
  DATE_TRUNC('month', transaction_date) AS month

Year-over-year comparison:
  CASE WHEN YEAR(transaction_date) = YEAR(CURRENT_DATE) THEN 'Current Year'
       WHEN YEAR(transaction_date) = YEAR(CURRENT_DATE) - 1 THEN 'Prior Year'
  END

Ranking advisors or clients:
  Use ROW_NUMBER() OVER (ORDER BY SUM(total_amount) DESC) for rank
  or simply ORDER BY ... DESC LIMIT N for top-N queries

Cross-sell identification (clients who bought X but not Y):
  Use CTEs with EXCEPT or NOT IN subqueries:
  WITH buyers_of_X AS (SELECT DISTINCT client_id FROM transactions JOIN products ...)
  SELECT ... FROM buyers_of_X WHERE client_id NOT IN (SELECT client_id FROM buyers_of_Y)

Dividing safely (avoid division by zero):
  Always use NULLIF(denominator, 0) in division expressions

Formatting currency output:
  ROUND(SUM(total_amount), 2) — always round monetary values to 2 decimal places

NULL handling:
  Use COALESCE(field, 0) for numeric fields that may be NULL
  Use COALESCE(field, 'Unknown') for string fields that may be NULL
```

---

### 5.4 Re-Run the Baseline Questions

After adding all configuration, re-run the same 10 questions from Step 4 and compare results.

| Question | Baseline (Step 4) | After Config (Step 5) | Improvement? |
|---|---|---|---|
| B1 — Total revenue this year | | | |
| B2 — VIP client count | | | |
| B3 — Top 5 products by revenue | | | |
| B4 — Which store makes the most? | | | |
| B5 — How many clients are at risk? | | | |
| B6 — At-risk VIP clients | | | |
| B7 — Toronto vs Vancouver revenue | | | |
| B8 — Advisor with highest AOV | | | |
| B9 — Clients inactive 6 months | | | |
| B10 — Return rate by category | | | |

> **Talk track for Jay:** "Notice how the same questions now produce more accurate, consistent results. This is the power of Genie's configuration layer — it's not a black box. You control the business vocabulary, the join logic, and the calculation standards. As your team uses Genie and gives feedback, these instructions get refined over time."

---

## Step 6 — Monitoring

**Where:** Genie Space → **Monitoring** tab (gear icon → Monitoring)

The Monitoring section gives administrators visibility into how the Genie space is being used, where it's succeeding, and where it needs improvement.

### 6.1 What's Available in Monitoring

#### Query History
- Every question asked in the Genie space is logged with:
  - The natural language question text
  - The SQL Genie generated
  - Execution time
  - Whether it succeeded or failed
  - The user who asked it
- Use this to identify the most common questions — if the same question is asked 20 times, it should be a **Certified Query**

#### User Activity
- See which users are actively using the space
- Identify power users (advisors or managers using it daily)
- Identify users who haven't logged in — follow up to understand blockers

#### Thumbs Up / Thumbs Down Feedback
- Every response can be rated by the user
- Monitoring shows the aggregate rating for each question type
- Low-rated questions are your highest-priority improvement targets
- Click any low-rated question → view the SQL → edit and certify

#### Failed Queries
- Genie logs questions it could not answer at all
- Common causes:
  - Question references a table not added to the space
  - Question uses a business term not defined in instructions
  - Ambiguous question with multiple valid interpretations
- Each failed query is an opportunity to add a certified question or update instructions

#### SQL Execution Performance
- See average query runtime per question type
- Identify slow queries and optimize them in the certified SQL layer
- Serverless warehouses auto-scale, but inefficient SQL still affects user experience

### 6.2 Monitoring Best Practices for the Harry Rosen POC

| Cadence | Action |
|---|---|
| **Daily (first 2 weeks)** | Review all thumbs-down responses and fix the SQL |
| **Weekly** | Review the most-asked questions — certify the top 5 not yet certified |
| **Weekly** | Check for failed queries — add instructions or new certified questions |
| **Monthly** | Review user activity — identify non-adopters and do targeted training |
| **Monthly** | Review avg query time — tune any consistently slow certified queries |

---

## Step 7 — Benchmarks

**Where:** Genie Space → **Benchmarks** tab

Benchmarks are Genie's built-in evaluation framework. They allow you to measure answer quality systematically — across a set of questions with known correct answers — so you can track improvement over time and validate configuration changes.

### 7.1 Why Benchmarks Matter

Without benchmarks, evaluating Genie is subjective ("that looked about right"). With benchmarks, you have:
- A **quantitative accuracy score** for the Genie space
- The ability to detect **regression** (a config change that broke previously correct answers)
- A clear **before/after comparison** when adding instructions or certified queries
- A credible **handoff artefact** to leave with the Harry Rosen team

### 7.2 How to Create a Benchmark

1. Go to **Genie Space → Benchmarks → + New Benchmark**
2. Give the benchmark a name: `Harry Rosen POC Baseline`
3. Click **+ Add Question** for each benchmark question
4. For each question, provide:
   - **Natural language question** — exactly as a user would type it
   - **Expected SQL** — the correct SQL answer
   - **Expected result** (optional) — if you want to validate the output, not just the SQL

#### Recommended Benchmark Question Set

Use the 10 questions from Step 4 as your benchmark. Here are the expected SQL answers:

**BQ1 — Total revenue this year**
```sql
SELECT ROUND(SUM(total_amount), 2) AS total_revenue
FROM ramin_aws_serverless_sandbox.harry_rosen.transactions
WHERE is_return = FALSE
  AND YEAR(transaction_date) = YEAR(CURRENT_DATE)
```

**BQ2 — VIP client count**
```sql
SELECT COUNT(*) AS vip_client_count
FROM ramin_aws_serverless_sandbox.harry_rosen.clients
WHERE is_vip = TRUE
```

**BQ3 — Top 5 products by revenue**
```sql
SELECT p.product_name, p.brand, p.category,
       ROUND(SUM(t.total_amount), 2) AS revenue
FROM ramin_aws_serverless_sandbox.harry_rosen.transactions t
JOIN ramin_aws_serverless_sandbox.harry_rosen.products p ON t.product_id = p.product_id
WHERE t.is_return = FALSE
GROUP BY p.product_name, p.brand, p.category
ORDER BY revenue DESC
LIMIT 5
```

**BQ4 — Store with most revenue**
```sql
SELECT s.store_name, s.city,
       ROUND(SUM(t.total_amount), 2) AS revenue
FROM ramin_aws_serverless_sandbox.harry_rosen.transactions t
JOIN ramin_aws_serverless_sandbox.harry_rosen.stores s ON t.store_id = s.store_id
WHERE t.is_return = FALSE
GROUP BY s.store_name, s.city
ORDER BY revenue DESC
LIMIT 1
```

**BQ5 — At-risk client count**
```sql
SELECT COUNT(*) AS at_risk_count
FROM ramin_aws_serverless_sandbox.harry_rosen.clients
WHERE client_segment = 'At-Risk'
```

**BQ6 — At-risk VIP clients**
```sql
SELECT c.first_name || ' ' || c.last_name AS client_name,
       c.email, c.lifetime_spend, c.last_purchase_date,
       DATEDIFF(CURRENT_DATE, c.last_purchase_date) AS days_inactive
FROM ramin_aws_serverless_sandbox.harry_rosen.clients c
WHERE c.is_vip = TRUE AND c.client_segment = 'At-Risk'
ORDER BY c.lifetime_spend DESC
```

**BQ7 — Toronto vs Vancouver revenue**
```sql
SELECT s.city, ROUND(SUM(t.total_amount), 2) AS revenue
FROM ramin_aws_serverless_sandbox.harry_rosen.transactions t
JOIN ramin_aws_serverless_sandbox.harry_rosen.stores s ON t.store_id = s.store_id
WHERE t.is_return = FALSE AND s.city IN ('Toronto', 'Vancouver')
GROUP BY s.city
ORDER BY revenue DESC
```

**BQ8 — Advisor with highest AOV**
```sql
SELECT a.first_name || ' ' || a.last_name AS advisor_name,
       ROUND(AVG(t.total_amount), 2) AS avg_order_value
FROM ramin_aws_serverless_sandbox.harry_rosen.transactions t
JOIN ramin_aws_serverless_sandbox.harry_rosen.advisors a ON t.advisor_id = a.advisor_id
WHERE t.is_return = FALSE
GROUP BY a.first_name, a.last_name
ORDER BY avg_order_value DESC
LIMIT 1
```

**BQ9 — Clients inactive for 6 months**
```sql
SELECT first_name || ' ' || last_name AS client_name,
       email, last_purchase_date,
       DATEDIFF(CURRENT_DATE, last_purchase_date) AS days_inactive
FROM ramin_aws_serverless_sandbox.harry_rosen.clients
WHERE last_purchase_date < DATE_SUB(CURRENT_DATE, 180)
ORDER BY last_purchase_date ASC
```

**BQ10 — Return rate by category**
```sql
SELECT p.category,
       COUNT(*) AS total_transactions,
       SUM(CASE WHEN t.is_return = TRUE THEN 1 ELSE 0 END) AS returns,
       ROUND(100.0 * SUM(CASE WHEN t.is_return = TRUE THEN 1 ELSE 0 END) / COUNT(*), 1) AS return_rate_pct
FROM ramin_aws_serverless_sandbox.harry_rosen.transactions t
JOIN ramin_aws_serverless_sandbox.harry_rosen.products p ON t.product_id = p.product_id
GROUP BY p.category
ORDER BY return_rate_pct DESC
```

### 7.3 How to Run a Benchmark

1. Go to **Benchmarks → Select benchmark → Run**
2. Genie will execute each question and compare the generated SQL to the expected SQL
3. Results are scored as:
   - **Pass** — generated SQL matches expected SQL semantically and produces the same result
   - **Partial** — SQL is different but result is equivalent
   - **Fail** — SQL is wrong or produces different results

4. Review the score:
   - **8–10 / 10 Pass** → Genie is production-ready for this question set
   - **5–7 / 10 Pass** → Add more certified queries and refine instructions
   - **< 5 / 10 Pass** → Review instructions for the failing questions; certify the expected SQL

### 7.4 Run Benchmarks in Two Phases

**Phase A — Before configuration (Step 4 baseline)**
- Create benchmark: `HR POC — No Config`
- Run it immediately after creating the Genie space (before adding instructions)
- Record the score

**Phase B — After configuration (Step 5)**
- Create benchmark: `HR POC — With Config`
- Run it after completing all instruction sections
- Compare scores to demonstrate improvement

> **Expected improvement:** Most POCs see benchmark scores go from ~40–50% before configuration to 80–90% after adding instructions, certified queries, and expressions. This delta is a powerful closing argument for the business value of the configuration investment.

### 7.5 Share the Benchmark Results with Jay

After running both benchmarks:

1. Screenshot the before/after scores
2. Walk Jay through specific examples of questions that improved
3. Show the `View SQL` comparison — the SQL Genie generated before vs. after configuration
4. Explain that this benchmark set can grow over time as the Harry Rosen team identifies their most important recurring questions

---

## Appendix — Quick Reference

### Key Links

| Resource | Path |
|---|---|
| Data setup notebook | `/Workspace/Users/ramin.amiri@databricks.com/harry_rosen/genie_demo/00_harry_rosen_data_setup` |
| Demo queries notebook | `/Workspace/Users/ramin.amiri@databricks.com/harry_rosen/genie_demo/01_harry_rosen_genie_demo_queries` |
| Config guide notebook | `/Workspace/Users/ramin.amiri@databricks.com/harry_rosen/genie_demo/02_harry_rosen_genie_config` |
| Workspace | `https://fe-sandbox-ramin-aws-serverless-sandbox.cloud.databricks.com` |
| Google Doc | `https://docs.google.com/document/d/1hg06oI2HFw8TlkZuSCizjQm2MyBOSr7Oyjo9DTt5yNw` |

### POC Agenda (Suggested 90 min)

| Time | Step | Activity |
|---|---|---|
| 0:00 – 0:05 | Intro | Context, agenda, goals for the session |
| 0:05 – 0:15 | Steps 1–2 | Access grant + data setup walkthrough |
| 0:15 – 0:25 | Step 3 | Create Genie space live |
| 0:25 – 0:40 | Step 4 | Baseline questions — no config |
| 0:40 – 0:65 | Step 5 | Add configuration — re-run same questions |
| 0:65 – 0:75 | Step 6 | Monitoring walkthrough |
| 0:75 – 0:85 | Step 7 | Benchmarks — show before/after scores |
| 0:85 – 0:90 | Close | Next steps, production path, Q&A |

### Contacts

| Role | Name | Email |
|---|---|---|
| Harry Rosen | Jay Sewell | `jay.sewell@harryrosen.com` |
| Databricks SA | Ramin Amiri | `ramin.amiri@databricks.com` |
