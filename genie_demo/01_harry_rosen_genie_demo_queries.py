# Databricks notebook source


# COMMAND ----------

# MAGIC %md
# MAGIC # Harry Rosen — Genie Demo: Sample Queries
# MAGIC
# MAGIC This notebook contains **18 demo queries** organized by complexity.
# MAGIC Use it to:
# MAGIC 1. **Verify the data** looks correct before the Jay Sewell demo
# MAGIC 2. **Mirror what Genie answers** — each cell shows the NL question + the SQL Genie generates
# MAGIC 3. **Run directly** in the SQL editor if needed as a fallback
# MAGIC
# MAGIC > **Tip:** In the real demo, type the question text into the Genie space chat — don't run SQL directly.
# MAGIC > This notebook is the "what should come out" reference.

# COMMAND ----------

DB = "ramin_aws_serverless_sandbox.harry_rosen"

# COMMAND ----------

# MAGIC %md
# MAGIC ---
# MAGIC ## Tier 1 — Warm-Up (Simple Aggregations)
# MAGIC *Ask these first in the demo to show instant results and build confidence.*

# COMMAND ----------

# MAGIC %md
# MAGIC ### Q1: "What is our total revenue this year?"
# MAGIC *Expected: single number ~$400K–$700K*

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT
# MAGIC   ROUND(SUM(total_amount), 2) AS total_revenue_ytd
# MAGIC FROM ramin_aws_serverless_sandbox.harry_rosen.transactions
# MAGIC WHERE is_return = FALSE
# MAGIC   AND YEAR(transaction_date) = YEAR(CURRENT_DATE)

# COMMAND ----------

# MAGIC %md
# MAGIC ### Q2: "Show me revenue by store for the last 12 months"
# MAGIC *Expected: bar chart — Toronto Bloor should lead*

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT
# MAGIC   s.store_name,
# MAGIC   s.city,
# MAGIC   s.region,
# MAGIC   ROUND(SUM(t.total_amount), 2)    AS revenue,
# MAGIC   COUNT(DISTINCT t.client_id)       AS unique_clients,
# MAGIC   ROUND(AVG(t.total_amount), 2)     AS avg_order_value
# MAGIC FROM ramin_aws_serverless_sandbox.harry_rosen.transactions t
# MAGIC JOIN ramin_aws_serverless_sandbox.harry_rosen.stores s
# MAGIC   ON t.store_id = s.store_id
# MAGIC WHERE t.is_return = FALSE
# MAGIC   AND t.transaction_date >= DATE_SUB(CURRENT_DATE, 365)
# MAGIC GROUP BY s.store_name, s.city, s.region
# MAGIC ORDER BY revenue DESC

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT
# MAGIC   t.store_id,
# MAGIC   s.store_name,
# MAGIC   SUM(t.total_amount) AS revenue_last_12_months
# MAGIC FROM
# MAGIC   `ramin_aws_serverless_sandbox`.`harry_rosen`.`transactions` t
# MAGIC     JOIN `ramin_aws_serverless_sandbox`.`harry_rosen`.`stores` s
# MAGIC       ON t.store_id = s.store_id
# MAGIC WHERE
# MAGIC   t.transaction_date BETWEEN DATE_SUB('2026-03-18', 365 - 1) AND '2026-03-18'
# MAGIC   AND t.is_return = false
# MAGIC   AND t.store_id IS NOT NULL
# MAGIC   AND t.total_amount IS NOT NULL
# MAGIC GROUP BY
# MAGIC   t.store_id,
# MAGIC   s.store_name
# MAGIC ORDER BY
# MAGIC   revenue_last_12_months DESC

# COMMAND ----------

# MAGIC %md
# MAGIC ### Q3: "How many clients do we have in each membership tier?"

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT
# MAGIC   membership_tier,
# MAGIC   COUNT(*)                                       AS client_count,
# MAGIC   ROUND(AVG(lifetime_spend), 2)                  AS avg_lifetime_spend,
# MAGIC   ROUND(SUM(lifetime_spend), 2)                  AS total_lifetime_spend
# MAGIC FROM ramin_aws_serverless_sandbox.harry_rosen.clients
# MAGIC GROUP BY membership_tier
# MAGIC ORDER BY CASE membership_tier
# MAGIC   WHEN 'Platinum' THEN 1 WHEN 'Gold' THEN 2
# MAGIC   WHEN 'Silver'   THEN 3 ELSE 4 END

# COMMAND ----------

# MAGIC %md
# MAGIC ### Q4: "What are the top 5 best-selling product categories?"

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT
# MAGIC   p.category,
# MAGIC   COUNT(t.transaction_id)           AS units_sold,
# MAGIC   ROUND(SUM(t.total_amount), 2)     AS total_revenue,
# MAGIC   ROUND(AVG(t.total_amount), 2)     AS avg_order_value
# MAGIC FROM ramin_aws_serverless_sandbox.harry_rosen.transactions t
# MAGIC JOIN ramin_aws_serverless_sandbox.harry_rosen.products p
# MAGIC   ON t.product_id = p.product_id
# MAGIC WHERE t.is_return = FALSE
# MAGIC GROUP BY p.category
# MAGIC ORDER BY total_revenue DESC
# MAGIC LIMIT 5

# COMMAND ----------

# MAGIC %md
# MAGIC ### Q5: "Which city has the most VIP clients?"

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT
# MAGIC   city,
# MAGIC   province,
# MAGIC   COUNT(*) AS vip_client_count
# MAGIC FROM ramin_aws_serverless_sandbox.harry_rosen.clients
# MAGIC WHERE is_vip = TRUE
# MAGIC GROUP BY city, province
# MAGIC ORDER BY vip_client_count DESC

# COMMAND ----------

# MAGIC %md
# MAGIC ---
# MAGIC ## Tier 2 — Business Intelligence (Multi-Table Joins)
# MAGIC *These are the queries that show real business value — cross-table analysis.*

# COMMAND ----------

# MAGIC %md
# MAGIC ### Q6: "Who are our top 10 clients by lifetime spend?"
# MAGIC *Expected: Platinum/Gold tier, mostly At-Risk segment — great hook for the next question*

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT
# MAGIC   c.client_id,
# MAGIC   c.first_name || ' ' || c.last_name          AS client_name,
# MAGIC   c.membership_tier,
# MAGIC   c.client_segment,
# MAGIC   c.is_vip,
# MAGIC   ROUND(c.lifetime_spend, 2)                   AS lifetime_spend,
# MAGIC   c.last_purchase_date,
# MAGIC   DATEDIFF(CURRENT_DATE, c.last_purchase_date) AS days_since_last_purchase,
# MAGIC   a.first_name || ' ' || a.last_name           AS advisor,
# MAGIC   s.store_name
# MAGIC FROM ramin_aws_serverless_sandbox.harry_rosen.clients c
# MAGIC JOIN ramin_aws_serverless_sandbox.harry_rosen.advisors a ON c.advisor_id = a.advisor_id
# MAGIC JOIN ramin_aws_serverless_sandbox.harry_rosen.stores  s ON c.preferred_store_id = s.store_id
# MAGIC ORDER BY c.lifetime_spend DESC
# MAGIC LIMIT 10

# COMMAND ----------

# MAGIC %md
# MAGIC ### Q7: "Which clients have not purchased in 6 months but spent more than $10,000 total?"
# MAGIC *The most valuable output of the demo — At-Risk VIP list*

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT
# MAGIC   c.first_name || ' ' || c.last_name          AS client_name,
# MAGIC   c.email,
# MAGIC   c.membership_tier,
# MAGIC   ROUND(c.lifetime_spend, 2)                   AS lifetime_spend,
# MAGIC   c.last_purchase_date,
# MAGIC   DATEDIFF(CURRENT_DATE, c.last_purchase_date) AS days_since_last_purchase,
# MAGIC   c.preferred_category,
# MAGIC   a.first_name || ' ' || a.last_name           AS assigned_advisor,
# MAGIC   s.store_name
# MAGIC FROM ramin_aws_serverless_sandbox.harry_rosen.clients c
# MAGIC JOIN ramin_aws_serverless_sandbox.harry_rosen.advisors a ON c.advisor_id  = a.advisor_id
# MAGIC JOIN ramin_aws_serverless_sandbox.harry_rosen.stores   s ON c.preferred_store_id = s.store_id
# MAGIC WHERE c.lifetime_spend > 10000
# MAGIC   AND c.last_purchase_date < DATE_SUB(CURRENT_DATE, 180)
# MAGIC ORDER BY c.lifetime_spend DESC

# COMMAND ----------

# MAGIC %md
# MAGIC ### Q8: "Show me revenue by advisor, ranked highest to lowest"

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT
# MAGIC   a.first_name || ' ' || a.last_name AS advisor_name,
# MAGIC   a.specialization,
# MAGIC   s.store_name,
# MAGIC   COUNT(t.transaction_id)            AS transactions,
# MAGIC   ROUND(SUM(t.total_amount), 2)      AS total_revenue,
# MAGIC   ROUND(AVG(t.total_amount), 2)      AS avg_order_value,
# MAGIC   COUNT(DISTINCT t.client_id)        AS unique_clients
# MAGIC FROM ramin_aws_serverless_sandbox.harry_rosen.advisors a
# MAGIC JOIN ramin_aws_serverless_sandbox.harry_rosen.transactions t ON a.advisor_id = t.advisor_id
# MAGIC JOIN ramin_aws_serverless_sandbox.harry_rosen.stores       s ON a.store_id   = s.store_id
# MAGIC WHERE t.is_return = FALSE
# MAGIC GROUP BY a.first_name, a.last_name, a.specialization, s.store_name
# MAGIC ORDER BY total_revenue DESC

# COMMAND ----------

# MAGIC %md
# MAGIC ### Q9: "What is the average order value per product category?"

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT
# MAGIC   p.category,
# MAGIC   ROUND(AVG(t.total_amount), 2)   AS avg_order_value,
# MAGIC   ROUND(MIN(t.total_amount), 2)   AS min_sale,
# MAGIC   ROUND(MAX(t.total_amount), 2)   AS max_sale,
# MAGIC   COUNT(t.transaction_id)         AS total_transactions
# MAGIC FROM ramin_aws_serverless_sandbox.harry_rosen.transactions t
# MAGIC JOIN ramin_aws_serverless_sandbox.harry_rosen.products p ON t.product_id = p.product_id
# MAGIC WHERE t.is_return = FALSE
# MAGIC GROUP BY p.category
# MAGIC ORDER BY avg_order_value DESC

# COMMAND ----------

# MAGIC %md
# MAGIC ### Q10: "Compare revenue in Toronto vs Vancouver for the past year"

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT
# MAGIC   s.city,
# MAGIC   COUNT(DISTINCT t.transaction_id)  AS transactions,
# MAGIC   COUNT(DISTINCT t.client_id)        AS unique_clients,
# MAGIC   ROUND(SUM(t.total_amount), 2)      AS total_revenue,
# MAGIC   ROUND(AVG(t.total_amount), 2)      AS avg_order_value,
# MAGIC   COUNT(DISTINCT t.store_id)         AS store_count
# MAGIC FROM ramin_aws_serverless_sandbox.harry_rosen.transactions t
# MAGIC JOIN ramin_aws_serverless_sandbox.harry_rosen.stores s ON t.store_id = s.store_id
# MAGIC WHERE t.is_return = FALSE
# MAGIC   AND t.transaction_date >= DATE_SUB(CURRENT_DATE, 365)
# MAGIC   AND s.city IN ('Toronto', 'Vancouver')
# MAGIC GROUP BY s.city
# MAGIC ORDER BY total_revenue DESC

# COMMAND ----------

# MAGIC %md
# MAGIC ---
# MAGIC ## Tier 3 — Power Moves (Conversational Context + Complex Logic)
# MAGIC *These demonstrate Genie's ability to chain follow-up questions and handle complex filters.*

# COMMAND ----------

# MAGIC %md
# MAGIC ### Q11a: "Show me clients who bought suits in 2025"
# MAGIC *Then follow up: "Of those, which haven't bought anything in the last 3 months?"*

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Step 1: Clients who bought suits in 2025
# MAGIC SELECT DISTINCT
# MAGIC   c.client_id,
# MAGIC   c.first_name || ' ' || c.last_name AS client_name,
# MAGIC   c.email,
# MAGIC   c.membership_tier,
# MAGIC   c.last_purchase_date
# MAGIC FROM ramin_aws_serverless_sandbox.harry_rosen.transactions t
# MAGIC JOIN ramin_aws_serverless_sandbox.harry_rosen.products p ON t.product_id = p.product_id
# MAGIC JOIN ramin_aws_serverless_sandbox.harry_rosen.clients  c ON t.client_id  = c.client_id
# MAGIC WHERE p.category = 'Suits'
# MAGIC   AND YEAR(t.transaction_date) = 2025
# MAGIC   AND t.is_return = FALSE

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Step 2: Of those suit buyers, who hasn't purchased in 3 months?
# MAGIC WITH suit_buyers_2025 AS (
# MAGIC   SELECT DISTINCT t.client_id
# MAGIC   FROM ramin_aws_serverless_sandbox.harry_rosen.transactions t
# MAGIC   JOIN ramin_aws_serverless_sandbox.harry_rosen.products p ON t.product_id = p.product_id
# MAGIC   WHERE p.category = 'Suits'
# MAGIC     AND YEAR(t.transaction_date) = 2025
# MAGIC     AND t.is_return = FALSE
# MAGIC )
# MAGIC SELECT
# MAGIC   c.first_name || ' ' || c.last_name          AS client_name,
# MAGIC   c.email,
# MAGIC   c.membership_tier,
# MAGIC   c.lifetime_spend,
# MAGIC   c.last_purchase_date,
# MAGIC   DATEDIFF(CURRENT_DATE, c.last_purchase_date) AS days_inactive,
# MAGIC   a.first_name || ' ' || a.last_name           AS advisor
# MAGIC FROM suit_buyers_2025 sb
# MAGIC JOIN ramin_aws_serverless_sandbox.harry_rosen.clients  c ON sb.client_id  = c.client_id
# MAGIC JOIN ramin_aws_serverless_sandbox.harry_rosen.advisors a ON c.advisor_id  = a.advisor_id
# MAGIC WHERE c.last_purchase_date < DATE_SUB(CURRENT_DATE, 90)
# MAGIC ORDER BY c.lifetime_spend DESC

# COMMAND ----------

# MAGIC %md
# MAGIC ### Q12: "Which advisors have more than 60 active clients and an AOV above $800?"

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT
# MAGIC   a.first_name || ' ' || a.last_name AS advisor_name,
# MAGIC   a.specialization,
# MAGIC   s.store_name,
# MAGIC   a.client_count,
# MAGIC   ROUND(SUM(t.total_amount) / NULLIF(COUNT(t.transaction_id), 0), 2) AS actual_aov,
# MAGIC   ROUND(SUM(t.total_amount), 2) AS total_revenue
# MAGIC FROM ramin_aws_serverless_sandbox.harry_rosen.advisors a
# MAGIC JOIN ramin_aws_serverless_sandbox.harry_rosen.transactions t ON a.advisor_id = t.advisor_id
# MAGIC JOIN ramin_aws_serverless_sandbox.harry_rosen.stores       s ON a.store_id   = s.store_id
# MAGIC WHERE t.is_return = FALSE
# MAGIC GROUP BY a.first_name, a.last_name, a.specialization, a.client_count, s.store_name
# MAGIC HAVING a.client_count > 60
# MAGIC    AND (SUM(t.total_amount) / NULLIF(COUNT(t.transaction_id), 0)) > 800
# MAGIC ORDER BY total_revenue DESC

# COMMAND ----------

# MAGIC %md
# MAGIC ### Q13: "What percentage of our transactions have a discount applied?"

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT
# MAGIC   COUNT(*)                                                AS total_transactions,
# MAGIC   SUM(CASE WHEN discount_pct > 0 THEN 1 ELSE 0 END)      AS discounted_transactions,
# MAGIC   ROUND(
# MAGIC     100.0 * SUM(CASE WHEN discount_pct > 0 THEN 1 ELSE 0 END) / COUNT(*), 1
# MAGIC   )                                                       AS discount_rate_pct,
# MAGIC   ROUND(AVG(CASE WHEN discount_pct > 0 THEN discount_pct END), 1) AS avg_discount_when_applied
# MAGIC FROM ramin_aws_serverless_sandbox.harry_rosen.transactions
# MAGIC WHERE is_return = FALSE

# COMMAND ----------

# MAGIC %md
# MAGIC ### Q14: "Show me the monthly revenue trend over the past 24 months"

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT
# MAGIC   DATE_TRUNC('month', transaction_date)  AS month,
# MAGIC   ROUND(SUM(total_amount), 2)             AS monthly_revenue,
# MAGIC   COUNT(DISTINCT client_id)               AS unique_clients,
# MAGIC   COUNT(transaction_id)                   AS transaction_count
# MAGIC FROM ramin_aws_serverless_sandbox.harry_rosen.transactions
# MAGIC WHERE is_return = FALSE
# MAGIC   AND transaction_date >= ADD_MONTHS(CURRENT_DATE, -24)
# MAGIC GROUP BY DATE_TRUNC('month', transaction_date)
# MAGIC ORDER BY month

# COMMAND ----------

# MAGIC %md
# MAGIC ### Q15: "Which product brands generate the most revenue?"

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT
# MAGIC   p.brand,
# MAGIC   COUNT(t.transaction_id)        AS transactions,
# MAGIC   ROUND(SUM(t.total_amount), 2)  AS total_revenue,
# MAGIC   ROUND(AVG(t.total_amount), 2)  AS avg_order_value,
# MAGIC   COUNT(DISTINCT t.client_id)    AS unique_buyers
# MAGIC FROM ramin_aws_serverless_sandbox.harry_rosen.transactions t
# MAGIC JOIN ramin_aws_serverless_sandbox.harry_rosen.products p ON t.product_id = p.product_id
# MAGIC WHERE t.is_return = FALSE
# MAGIC GROUP BY p.brand
# MAGIC ORDER BY total_revenue DESC

# COMMAND ----------

# MAGIC %md
# MAGIC ---
# MAGIC ## Tier 4 — Advisor / Personalization Queries

# COMMAND ----------

# MAGIC %md
# MAGIC ### Q16: "Show me all At-Risk clients assigned to Alessandro Ferretti"
# MAGIC *Simulates an advisor checking their own book of business*

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT
# MAGIC   c.first_name || ' ' || c.last_name          AS client_name,
# MAGIC   c.email,
# MAGIC   c.membership_tier,
# MAGIC   ROUND(c.lifetime_spend, 2)                   AS lifetime_spend,
# MAGIC   c.last_purchase_date,
# MAGIC   DATEDIFF(CURRENT_DATE, c.last_purchase_date) AS days_since_purchase,
# MAGIC   c.preferred_category
# MAGIC FROM ramin_aws_serverless_sandbox.harry_rosen.clients  c
# MAGIC JOIN ramin_aws_serverless_sandbox.harry_rosen.advisors a ON c.advisor_id = a.advisor_id
# MAGIC WHERE a.first_name = 'Alessandro'
# MAGIC   AND a.last_name  = 'Ferretti'
# MAGIC   AND c.client_segment = 'At-Risk'
# MAGIC ORDER BY c.lifetime_spend DESC

# COMMAND ----------

# MAGIC %md
# MAGIC ### Q17: "Which clients purchased Canali suits but have never bought shoes?"
# MAGIC *Cross-sell opportunity identification*

# COMMAND ----------

# MAGIC %sql
# MAGIC WITH canali_suit_buyers AS (
# MAGIC   SELECT DISTINCT t.client_id
# MAGIC   FROM ramin_aws_serverless_sandbox.harry_rosen.transactions t
# MAGIC   JOIN ramin_aws_serverless_sandbox.harry_rosen.products p ON t.product_id = p.product_id
# MAGIC   WHERE p.brand = 'Canali' AND p.category = 'Suits' AND t.is_return = FALSE
# MAGIC ),
# MAGIC shoe_buyers AS (
# MAGIC   SELECT DISTINCT t.client_id
# MAGIC   FROM ramin_aws_serverless_sandbox.harry_rosen.transactions t
# MAGIC   JOIN ramin_aws_serverless_sandbox.harry_rosen.products p ON t.product_id = p.product_id
# MAGIC   WHERE p.category = 'Shoes' AND t.is_return = FALSE
# MAGIC )
# MAGIC SELECT
# MAGIC   c.first_name || ' ' || c.last_name AS client_name,
# MAGIC   c.membership_tier,
# MAGIC   ROUND(c.lifetime_spend, 2)          AS lifetime_spend,
# MAGIC   c.preferred_category,
# MAGIC   a.first_name || ' ' || a.last_name  AS advisor
# MAGIC FROM canali_suit_buyers csb
# MAGIC JOIN ramin_aws_serverless_sandbox.harry_rosen.clients  c ON csb.client_id = c.client_id
# MAGIC JOIN ramin_aws_serverless_sandbox.harry_rosen.advisors a ON c.advisor_id  = a.advisor_id
# MAGIC WHERE csb.client_id NOT IN (SELECT client_id FROM shoe_buyers)
# MAGIC ORDER BY c.lifetime_spend DESC

# COMMAND ----------

# MAGIC %md
# MAGIC ### Q18: "What is the return rate by product category?"

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT
# MAGIC   p.category,
# MAGIC   COUNT(t.transaction_id)                                                          AS total_transactions,
# MAGIC   SUM(CASE WHEN t.is_return = TRUE THEN 1 ELSE 0 END)                             AS returns,
# MAGIC   ROUND(100.0 * SUM(CASE WHEN t.is_return = TRUE THEN 1 ELSE 0 END) / COUNT(*), 1) AS return_rate_pct
# MAGIC FROM ramin_aws_serverless_sandbox.harry_rosen.transactions t
# MAGIC JOIN ramin_aws_serverless_sandbox.harry_rosen.products p ON t.product_id = p.product_id
# MAGIC GROUP BY p.category
# MAGIC ORDER BY return_rate_pct DESC

# COMMAND ----------

# MAGIC %md
# MAGIC ---
# MAGIC ## Summary Table
# MAGIC
# MAGIC | # | Question | Tier | Key Tables |
# MAGIC |---|---|---|---|
# MAGIC | Q1 | Total revenue this year | Warm-Up | transactions |
# MAGIC | Q2 | Revenue by store (12 months) | Warm-Up | transactions, stores |
# MAGIC | Q3 | Clients per membership tier | Warm-Up | clients |
# MAGIC | Q4 | Top 5 product categories | Warm-Up | transactions, products |
# MAGIC | Q5 | City with most VIP clients | Warm-Up | clients |
# MAGIC | Q6 | Top 10 clients by lifetime spend | BI | clients, advisors, stores |
# MAGIC | Q7 | At-Risk VIPs (>$10K, inactive 6m) | **BI** | clients, advisors, stores |
# MAGIC | Q8 | Advisor revenue leaderboard | BI | advisors, transactions, stores |
# MAGIC | Q9 | AOV per category | BI | transactions, products |
# MAGIC | Q10 | Toronto vs Vancouver revenue | BI | transactions, stores |
# MAGIC | Q11 | Suit buyers → inactive follow-up | **Power** | transactions, products, clients |
# MAGIC | Q12 | Advisors with 60+ clients, AOV $800+ | Power | advisors, transactions, stores |
# MAGIC | Q13 | Discount rate | Power | transactions |
# MAGIC | Q14 | Monthly revenue trend 24m | Power | transactions |
# MAGIC | Q15 | Revenue by brand | Power | transactions, products |
# MAGIC | Q16 | At-Risk clients for one advisor | Advisor | clients, advisors |
# MAGIC | Q17 | Canali suit buyers → no shoes (cross-sell) | **Advisor** | transactions, products, clients |
# MAGIC | Q18 | Return rate by category | Advisor | transactions, products |

# COMMAND ----------


