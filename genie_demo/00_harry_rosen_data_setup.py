# Databricks notebook source


# COMMAND ----------

# MAGIC %md
# MAGIC # Harry Rosen — Genie Demo: Data Setup
# MAGIC
# MAGIC This notebook creates all demo tables for the **Harry Rosen Genie Demo**.
# MAGIC
# MAGIC ## What this creates
# MAGIC | Table | Rows | Description |
# MAGIC |---|---|---|
# MAGIC | `stores` | 8 | Canadian retail locations |
# MAGIC | `advisors` | 20 | Style advisors with performance metrics |
# MAGIC | `products` | 40 | Luxury menswear SKUs |
# MAGIC | `clients` | 250 | Client profiles with VIP/segment data |
# MAGIC | `transactions` | ~3,800 | 2-year POS transaction history |
# MAGIC
# MAGIC **Workspace:** `fe-sandbox-ramin-aws-serverless-sandbox.cloud.databricks.com`
# MAGIC **Catalog:** `ramin_aws_serverless_sandbox`
# MAGIC **Schema:** `ramin_aws_serverless_sandbox.harry_rosen`

# COMMAND ----------

# MAGIC %md
# MAGIC ## 0. Configuration

# COMMAND ----------

CATALOG = "ramin_serverless_aws_catalog"
SCHEMA  = "harry_rosen"
DB      = f"{CATALOG}.{SCHEMA}"

print(f"Target: {DB}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1. Create Schema

# COMMAND ----------

spark.sql(f"""
CREATE SCHEMA IF NOT EXISTS {DB}
COMMENT 'Harry Rosen luxury menswear demo data for Genie AI/BI'
""")
print(f"Schema {DB} ready.")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2. Stores

# COMMAND ----------

spark.sql(f"DROP TABLE IF EXISTS {DB}.stores")

spark.sql(f"""
CREATE TABLE {DB}.stores (
  store_id        INT     COMMENT 'Unique store identifier',
  store_name      STRING  COMMENT 'Full store name',
  city            STRING  COMMENT 'City where store is located',
  province        STRING  COMMENT 'Province/territory',
  region          STRING  COMMENT 'Sales region: East, West, Central',
  square_footage  INT     COMMENT 'Store size in sq ft',
  opened_year     INT     COMMENT 'Year store opened',
  manager_name    STRING  COMMENT 'Store manager full name'
)
COMMENT 'Harry Rosen retail store locations across Canada'
""")

stores_data = [
    (1, "Harry Rosen - Bloor Street",            "Toronto",   "ON", "East",    8500, 1954, "Michael Chen"),
    (2, "Harry Rosen - Yorkdale",                 "Toronto",   "ON", "East",    6200, 1998, "Sarah Goldstein"),
    (3, "Harry Rosen - Vancouver Pacific Centre", "Vancouver", "BC", "West",    5800, 1979, "James Nakamura"),
    (4, "Harry Rosen - Oakridge",                 "Vancouver", "BC", "West",    4200, 2005, "Emily Park"),
    (5, "Harry Rosen - Montréal Ogilvy",          "Montreal",  "QC", "East",    5100, 1967, "Pierre Tremblay"),
    (6, "Harry Rosen - Market Mall",              "Calgary",   "AB", "Central", 4800, 1995, "David MacLeod"),
    (7, "Harry Rosen - Rideau Centre",            "Ottawa",    "ON", "East",    3900, 2001, "Laura Singh"),
    (8, "Harry Rosen - Masonville Place",         "London",    "ON", "East",    3600, 2009, "Robert Kovacs"),
]

from pyspark.sql.types import StructType, StructField, IntegerType, StringType

schema = StructType([
    StructField("store_id",       IntegerType()),
    StructField("store_name",     StringType()),
    StructField("city",           StringType()),
    StructField("province",       StringType()),
    StructField("region",         StringType()),
    StructField("square_footage", IntegerType()),
    StructField("opened_year",    IntegerType()),
    StructField("manager_name",   StringType()),
])

df = spark.createDataFrame(stores_data, schema=schema)
df.write.mode("append").saveAsTable(f"{DB}.stores")
print(f"Inserted {df.count()} stores")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 3. Advisors

# COMMAND ----------

spark.sql(f"DROP TABLE IF EXISTS {DB}.advisors")

spark.sql(f"""
CREATE TABLE {DB}.advisors (
  advisor_id      INT     COMMENT 'Unique advisor identifier',
  first_name      STRING  COMMENT 'Advisor first name',
  last_name       STRING  COMMENT 'Advisor last name',
  store_id        INT     COMMENT 'Store where advisor works (FK → stores)',
  hire_date       DATE    COMMENT 'Date advisor was hired',
  specialization  STRING  COMMENT 'Primary expertise: Suiting, Casual, Formalwear, Tailoring, Accessories',
  commission_rate DOUBLE  COMMENT 'Commission percentage on sales',
  ytd_revenue     DOUBLE  COMMENT 'Year-to-date revenue generated',
  client_count    INT     COMMENT 'Number of active clients managed'
)
COMMENT 'Harry Rosen style advisors and their performance metrics'
""")

advisors_data = [
    (1,  "Alessandro", "Ferretti",        1, "2015-03-10", "Suiting",        0.08, 312400.0, 87),
    (2,  "Catherine",  "Beaumont",         1, "2018-07-22", "Formalwear",     0.07, 198700.0, 54),
    (3,  "Marcus",     "Williams",         1, "2011-01-15", "Casual & Sport", 0.08, 245300.0, 72),
    (4,  "Yuki",       "Tanaka",           2, "2019-09-05", "Suiting",        0.07, 178900.0, 45),
    (5,  "Olivia",     "Stern",            2, "2016-04-18", "Accessories",    0.06, 134200.0, 63),
    (6,  "Daniel",     "Rosenthal",        2, "2013-11-28", "Suiting",        0.08, 267800.0, 79),
    (7,  "Priya",      "Mehta",            3, "2017-06-12", "Formalwear",     0.07, 221500.0, 61),
    (8,  "Thomas",     "Larsen",           3, "2020-02-03", "Casual & Sport", 0.06, 145600.0, 38),
    (9,  "Sophie",     "Girard",           5, "2014-08-19", "Suiting",        0.08, 289100.0, 83),
    (10, "Étienne",    "Leblanc",          5, "2018-03-27", "Formalwear",     0.07, 167400.0, 47),
    (11, "Connor",     "MacPherson",       6, "2016-10-14", "Suiting",        0.08, 198300.0, 56),
    (12, "Aisha",      "Patel",            6, "2021-01-08", "Casual & Sport", 0.06, 112700.0, 31),
    (13, "Kevin",      "O'Brien",          7, "2019-05-21", "Suiting",        0.07, 156800.0, 44),
    (14, "Rachel",     "Goldberg",         1, "2012-09-30", "Tailoring",      0.09, 334600.0, 92),
    (15, "James",      "Whitfield",        3, "2015-12-07", "Suiting",        0.08, 243900.0, 68),
    (16, "Nina",       "Kowalski",         4, "2020-07-15", "Accessories",    0.06,  98400.0, 29),
    (17, "Sanjay",     "Krishnamurthy",    2, "2014-02-25", "Suiting",        0.08, 278500.0, 76),
    (18, "Amelia",     "Thornton",         8, "2022-03-01", "Formalwear",     0.06,  87600.0, 22),
    (19, "Lucas",      "Beauchamp",        5, "2017-11-09", "Casual & Sport", 0.07, 189200.0, 53),
    (20, "Natasha",    "Volkov",           6, "2013-06-18", "Tailoring",      0.09, 312700.0, 88),
]

from pyspark.sql.types import DoubleType, DateType

adv_schema = StructType([
    StructField("advisor_id",      IntegerType()),
    StructField("first_name",      StringType()),
    StructField("last_name",       StringType()),
    StructField("store_id",        IntegerType()),
    StructField("hire_date",       StringType()),   # cast below
    StructField("specialization",  StringType()),
    StructField("commission_rate", DoubleType()),
    StructField("ytd_revenue",     DoubleType()),
    StructField("client_count",    IntegerType()),
])

from pyspark.sql import functions as F

df_adv = spark.createDataFrame(advisors_data, schema=adv_schema) \
    .withColumn("hire_date", F.to_date("hire_date"))
df_adv.write.mode("append").saveAsTable(f"{DB}.advisors")
print(f"Inserted {df_adv.count()} advisors")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 4. Products

# COMMAND ----------

spark.sql(f"DROP TABLE IF EXISTS {DB}.products")

spark.sql(f"""
CREATE TABLE {DB}.products (
  product_id    STRING  COMMENT 'Unique product SKU',
  product_name  STRING  COMMENT 'Full product display name',
  category      STRING  COMMENT 'Top-level category: Suits, Shirts, Shoes, Outerwear, Accessories, Trousers',
  subcategory   STRING  COMMENT 'Sub-category for finer grouping',
  brand         STRING  COMMENT 'Designer brand name',
  unit_price    DOUBLE  COMMENT 'Retail price in CAD',
  colour        STRING  COMMENT 'Primary colour',
  season        STRING  COMMENT 'Season: Fall/Winter, Spring/Summer, All-Season',
  stock_qty     INT     COMMENT 'Current inventory across all stores',
  is_active     BOOLEAN COMMENT 'Whether product is currently available for sale'
)
COMMENT 'Harry Rosen product catalogue — luxury menswear items'
""")

products_data = [
    # Suits
    ("SKU-S001",   "Canali Two-Button Wool Suit - Navy",         "Suits",       "Two-Button",     "Canali",        3495.0, "Navy",        "All-Season",    12, True),
    ("SKU-S002",   "Canali Two-Button Wool Suit - Charcoal",     "Suits",       "Two-Button",     "Canali",        3495.0, "Charcoal",    "All-Season",     9, True),
    ("SKU-S003",   "Zegna Trofeo Slim-Fit Suit",                 "Suits",       "Slim-Fit",       "Zegna",         4850.0, "Midnight Blue","All-Season",    6, True),
    ("SKU-S004",   "Boss H-Hutson Double Breasted Suit",         "Suits",       "Double-Breasted","Boss",          1995.0, "Grey",        "All-Season",    14, True),
    ("SKU-S005",   "Brioni Brunico Bespoke Suit",                "Suits",       "Bespoke",        "Brioni",        8500.0, "Charcoal",    "All-Season",     3, True),
    ("SKU-S006",   "Tom Ford Windsor Base Suit",                 "Suits",       "Two-Button",     "Tom Ford",      5200.0, "Black",       "All-Season",     5, True),
    ("SKU-S007",   "Pal Zileri Concept Suit - Taupe",            "Suits",       "Two-Button",     "Pal Zileri",    2200.0, "Taupe",       "Spring/Summer",  8, True),
    ("SKU-S008",   "Corneliani Full Canvas Suit - Khaki",        "Suits",       "Three-Button",   "Corneliani",    2800.0, "Khaki",       "Spring/Summer",  7, True),
    ("SKU-S009",   "Isaia Gregory Suit - Blue Stripe",           "Suits",       "Slim-Fit",       "Isaia",         4200.0, "Blue Stripe", "All-Season",     4, True),
    ("SKU-S010",   "Samuelsohn Custom Suit - Black",             "Suits",       "Made-to-Measure","Samuelsohn",    3800.0, "Black",       "All-Season",     2, True),
    # Shirts
    ("SKU-SH001",  "Canali Slim-Fit Dress Shirt - White",        "Shirts",      "Dress Shirt",    "Canali",         395.0, "White",       "All-Season",    40, True),
    ("SKU-SH002",  "Canali Slim-Fit Dress Shirt - Blue",         "Shirts",      "Dress Shirt",    "Canali",         395.0, "Blue",        "All-Season",    35, True),
    ("SKU-SH003",  "Eton Contemporary Fit Shirt - White",        "Shirts",      "Dress Shirt",    "Eton",           285.0, "White",       "All-Season",    52, True),
    ("SKU-SH004",  "Eton Slim Fit Oxford Shirt",                 "Shirts",      "Casual Shirt",   "Eton",           265.0, "Light Blue",  "All-Season",    47, True),
    ("SKU-SH005",  "Boss Hank Kent Dress Shirt",                 "Shirts",      "Dress Shirt",    "Boss",           225.0, "White",       "All-Season",    63, True),
    ("SKU-SH006",  "Tom Ford Grosgrain-Trimmed Shirt",           "Shirts",      "Dress Shirt",    "Tom Ford",       650.0, "White",       "All-Season",    18, True),
    ("SKU-SH007",  "Zegna Linen Shirt - Light Grey",             "Shirts",      "Casual Shirt",   "Zegna",          480.0, "Light Grey",  "Spring/Summer", 22, True),
    ("SKU-SH008",  "Finamore Napoli Dress Shirt - Ecru",         "Shirts",      "Dress Shirt",    "Finamore",       540.0, "Ecru",        "All-Season",    11, True),
    # Shoes
    ("SKU-SHO001", "Magnanni Cap-Toe Oxford - Black",            "Shoes",       "Oxford",         "Magnanni",       695.0, "Black",       "All-Season",    20, True),
    ("SKU-SHO002", "Magnanni Derby Shoe - Tan",                  "Shoes",       "Derby",          "Magnanni",       625.0, "Tan",         "Spring/Summer", 18, True),
    ("SKU-SHO003", "To Boot New York Chelsea Boot",              "Shoes",       "Chelsea Boot",   "To Boot NY",     498.0, "Dark Brown",  "Fall/Winter",   24, True),
    ("SKU-SHO004", "Common Projects Achilles Low - White",       "Shoes",       "Sneaker",        "Common Projects",580.0, "White",       "All-Season",    16, True),
    ("SKU-SHO005", "John Lobb City II Oxford",                   "Shoes",       "Oxford",         "John Lobb",     1850.0, "Black",       "All-Season",     5, True),
    # Outerwear
    ("SKU-O001",   "Mackage Edward Leather Jacket - Black",      "Outerwear",   "Leather Jacket", "Mackage",       1295.0, "Black",       "Fall/Winter",    9, True),
    ("SKU-O002",   "Canada Goose Langford Parka",                "Outerwear",   "Parka",          "Canada Goose",  1250.0, "Navy",        "Fall/Winter",   11, True),
    ("SKU-O003",   "Zegna Wool Overcoat - Camel",                "Outerwear",   "Overcoat",       "Zegna",         2800.0, "Camel",       "Fall/Winter",    6, True),
    ("SKU-O004",   "Boss Cashmere Topcoat - Charcoal",           "Outerwear",   "Topcoat",        "Boss",          1450.0, "Charcoal",    "Fall/Winter",    8, True),
    ("SKU-O005",   "Ted Baker Wool Peacoat",                     "Outerwear",   "Peacoat",        "Ted Baker",      595.0, "Navy",        "Fall/Winter",   14, True),
    # Accessories
    ("SKU-A001",   "Canali Silk Tie - Burgundy",                 "Accessories", "Tie",            "Canali",         225.0, "Burgundy",    "All-Season",    45, True),
    ("SKU-A002",   "Canali Silk Tie - Navy Stripe",              "Accessories", "Tie",            "Canali",         225.0, "Navy",        "All-Season",    38, True),
    ("SKU-A003",   "Hermès Silk Pocket Square",                  "Accessories", "Pocket Square",  "Hermès",         285.0, "Multi",       "All-Season",    22, True),
    ("SKU-A004",   "Boss Leather Belt - Black",                  "Accessories", "Belt",           "Boss",           185.0, "Black",       "All-Season",    55, True),
    ("SKU-A005",   "Zegna Cashmere Scarf",                       "Accessories", "Scarf",          "Zegna",          495.0, "Grey",        "Fall/Winter",   18, True),
    ("SKU-A006",   "Rolex Datejust 41 - Silver",                 "Accessories", "Watch",          "Rolex",        12800.0, "Silver",      "All-Season",     2, True),
    ("SKU-A007",   "Montblanc Meisterstück Pen",                 "Accessories", "Pen",            "Montblanc",      895.0, "Black",       "All-Season",     7, True),
    ("SKU-A008",   "Canali Leather Dress Belt - Brown",          "Accessories", "Belt",           "Canali",         245.0, "Brown",       "All-Season",    32, True),
    # Trousers
    ("SKU-T001",   "Canali Flat-Front Wool Trousers - Grey",     "Trousers",    "Dress Trouser",  "Canali",         595.0, "Grey",        "All-Season",    28, True),
    ("SKU-T002",   "PT01 Five-Pocket Stretch Trousers",          "Trousers",    "Casual Trouser", "PT01",           395.0, "Navy",        "All-Season",    33, True),
    ("SKU-T003",   "Boss Slim-Fit Trousers - Black",             "Trousers",    "Dress Trouser",  "Boss",           325.0, "Black",       "All-Season",    40, True),
    ("SKU-T004",   "Zegna Chino - Beige",                        "Trousers",    "Chino",          "Zegna",          580.0, "Beige",       "Spring/Summer", 22, True),
]

from pyspark.sql.types import BooleanType

prod_schema = StructType([
    StructField("product_id",   StringType()),
    StructField("product_name", StringType()),
    StructField("category",     StringType()),
    StructField("subcategory",  StringType()),
    StructField("brand",        StringType()),
    StructField("unit_price",   DoubleType()),
    StructField("colour",       StringType()),
    StructField("season",       StringType()),
    StructField("stock_qty",    IntegerType()),
    StructField("is_active",    BooleanType()),
])

df_prod = spark.createDataFrame(products_data, schema=prod_schema)
df_prod.write.mode("append").saveAsTable(f"{DB}.products")
print(f"Inserted {df_prod.count()} products")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 5. Clients

# COMMAND ----------

spark.sql(f"DROP TABLE IF EXISTS {DB}.clients")

spark.sql(f"""
CREATE TABLE {DB}.clients (
  client_id           INT     COMMENT 'Unique client identifier',
  first_name          STRING  COMMENT 'Client first name',
  last_name           STRING  COMMENT 'Client last name',
  email               STRING  COMMENT 'Client email address',
  city                STRING  COMMENT 'Client home city',
  province            STRING  COMMENT 'Client province',
  preferred_store_id  INT     COMMENT 'Preferred store (FK → stores)',
  advisor_id          INT     COMMENT 'Assigned style advisor (FK → advisors)',
  membership_tier     STRING  COMMENT 'Loyalty tier: Classic, Silver, Gold, Platinum',
  is_vip              BOOLEAN COMMENT 'True if lifetime spend > $10K or manually flagged',
  client_segment      STRING  COMMENT 'Segment: Active, At-Risk, New, Dormant, Re-engaged',
  lifetime_spend      DOUBLE  COMMENT 'Total spend since first purchase in CAD',
  last_purchase_date  DATE    COMMENT 'Date of most recent purchase',
  first_purchase_date DATE    COMMENT 'Date of first purchase',
  total_orders        INT     COMMENT 'Total number of transactions',
  avg_order_value     DOUBLE  COMMENT 'Average transaction value in CAD',
  preferred_category  STRING  COMMENT 'Category the client buys most frequently'
)
COMMENT 'Harry Rosen client profiles with loyalty and segmentation data'
""")

import random
from datetime import datetime, timedelta

random.seed(42)

first_names = ["James","William","Oliver","Ethan","Noah","Lucas","Liam","Benjamin","Henry","Sebastian",
               "Alexander","Michael","Daniel","David","Matthew","Andrew","Anthony","Joshua","Ryan","Nathan",
               "Patrick","Christopher","Jonathan","Nicholas","Thomas","Robert","Edward","Charles","George","Arthur",
               "Lawrence","Raymond","Leonard","Harold","Walter","Peter","Francis","Paul","Vincent","Richard"]
last_names  = ["Thompson","MacDonald","Fitzgerald","Chen","Patel","Kumar","Williams","Anderson","Martin","Taylor",
               "Harris","Wilson","Moore","Jackson","Lee","White","Clark","Lewis","Walker","Hall",
               "Young","Allen","King","Wright","Scott","Green","Baker","Adams","Nelson","Hill",
               "Ramirez","Campbell","Mitchell","Roberts","Evans","Turner","Parker","Collins","Edwards","Morris"]

# (city, province, store_id)
city_map = [(1,"Toronto","ON",1),(2,"Toronto","ON",2),(3,"Vancouver","BC",3),
            (4,"Vancouver","BC",4),(5,"Montreal","QC",5),(6,"Calgary","AB",6),
            (7,"Ottawa","ON",7),(8,"London","ON",8)]

# advisor_id → store_id
advisor_store = {1:1,2:1,3:1,14:1, 4:2,5:2,6:2,17:2, 7:3,8:3,15:3,
                 16:4, 9:5,10:5,19:5, 11:6,12:6,20:6, 13:7, 18:8}

categories = ["Suits","Shirts","Shoes","Outerwear","Accessories","Trousers"]
segments   = ["Active","Active","Active","At-Risk","At-Risk","New","Dormant","Re-engaged"]

today = datetime(2026, 3, 17)
clients_rows = []

for i in range(1, 251):
    fn = first_names[i % len(first_names)]
    ln = last_names[(i * 7) % len(last_names)]
    _, city, prov, store_id = city_map[i % len(city_map)]
    store_advisors = [a for a, s in advisor_store.items() if s == store_id]
    advisor_id = store_advisors[i % len(store_advisors)]
    segment = segments[i % len(segments)]
    is_vip = (i % 4 == 0) or (i % 7 == 0)

    if segment == "New":
        lifetime = round(random.uniform(500, 3000), 2);   orders = random.randint(1, 3)
        last_d = random.randint(7, 90);   first_d = random.randint(90, 180)
    elif segment == "Active":
        lifetime = round(random.uniform(5000, 85000), 2); orders = random.randint(5, 40)
        last_d = random.randint(14, 180); first_d = random.randint(365, 1825)
    elif segment == "At-Risk":
        lifetime = round(random.uniform(8000, 60000), 2); orders = random.randint(6, 30)
        last_d = random.randint(180, 365); first_d = random.randint(730, 2190); is_vip = True
    elif segment == "Dormant":
        lifetime = round(random.uniform(1000, 15000), 2); orders = random.randint(2, 10)
        last_d = random.randint(365, 900); first_d = random.randint(900, 2555)
    else:  # Re-engaged
        lifetime = round(random.uniform(3000, 25000), 2); orders = random.randint(3, 15)
        last_d = random.randint(30, 90); first_d = random.randint(900, 2555)

    if lifetime > 10000: is_vip = True
    tier = ("Platinum" if lifetime > 50000 else
            "Gold"     if lifetime > 20000 else
            "Silver"   if lifetime > 8000  else "Classic")
    avg_order   = round(lifetime / orders, 2)
    last_purch  = (today - timedelta(days=last_d)).strftime("%Y-%m-%d")
    first_purch = (today - timedelta(days=first_d)).strftime("%Y-%m-%d")
    pref_cat    = categories[i % len(categories)]
    email       = f"{fn.lower()}.{ln.lower()}{i}@email.com"

    clients_rows.append((
        i, fn, ln, email, city, prov,
        store_id, advisor_id, tier, is_vip, segment,
        lifetime, last_purch, first_purch, orders, avg_order, pref_cat
    ))

cli_schema = StructType([
    StructField("client_id",           IntegerType()),
    StructField("first_name",          StringType()),
    StructField("last_name",           StringType()),
    StructField("email",               StringType()),
    StructField("city",                StringType()),
    StructField("province",            StringType()),
    StructField("preferred_store_id",  IntegerType()),
    StructField("advisor_id",          IntegerType()),
    StructField("membership_tier",     StringType()),
    StructField("is_vip",              BooleanType()),
    StructField("client_segment",      StringType()),
    StructField("lifetime_spend",      DoubleType()),
    StructField("last_purchase_date",  StringType()),
    StructField("first_purchase_date", StringType()),
    StructField("total_orders",        IntegerType()),
    StructField("avg_order_value",     DoubleType()),
    StructField("preferred_category",  StringType()),
])

df_cli = spark.createDataFrame(clients_rows, schema=cli_schema) \
    .withColumn("last_purchase_date",  F.to_date("last_purchase_date")) \
    .withColumn("first_purchase_date", F.to_date("first_purchase_date"))
df_cli.write.mode("append").saveAsTable(f"{DB}.clients")
print(f"Inserted {df_cli.count()} clients")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 6. Transactions

# COMMAND ----------

spark.sql(f"DROP TABLE IF EXISTS {DB}.transactions")

spark.sql(f"""
CREATE TABLE {DB}.transactions (
  transaction_id   STRING  COMMENT 'Unique transaction identifier',
  transaction_date DATE    COMMENT 'Date of purchase',
  client_id        INT     COMMENT 'Client who purchased (FK → clients)',
  store_id         INT     COMMENT 'Store where sale occurred (FK → stores)',
  advisor_id       INT     COMMENT 'Advisor who handled the sale (FK → advisors)',
  product_id       STRING  COMMENT 'Product purchased (FK → products)',
  quantity         INT     COMMENT 'Units purchased',
  unit_price       DOUBLE  COMMENT 'Price per unit at time of sale in CAD',
  discount_pct     DOUBLE  COMMENT 'Discount applied as a percentage (0–30)',
  total_amount     DOUBLE  COMMENT 'Final transaction value in CAD after discount',
  payment_method   STRING  COMMENT 'Payment method: Credit Card, Debit, Wire Transfer',
  is_return        BOOLEAN COMMENT 'True if this is a return/refund transaction'
)
COMMENT 'Harry Rosen point-of-sale transaction history — 2 years'
""")

product_ids    = [p[0] for p in products_data]
product_prices = {p[0]: p[5] for p in products_data}
payments       = ["Credit Card","Credit Card","Credit Card","Debit","Wire Transfer"]

txn_rows = []
txn_id   = 1

for (cid, fn, ln, email, city, prov, store_id, adv_id, tier,
     is_vip, segment, lifetime, last_purch, first_purch, orders, avg_order, pref_cat) in clients_rows:

    first_dt  = datetime.strptime(first_purch, "%Y-%m-%d")
    last_dt   = datetime.strptime(last_purch,  "%Y-%m-%d")
    day_range = max((last_dt - first_dt).days, 1)

    for o in range(orders):
        frac     = o / max(orders - 1, 1)
        raw_date = first_dt + timedelta(days=int(frac * day_range) + random.randint(-5, 5))
        txn_date = min(raw_date, datetime(2026, 3, 17)).strftime("%Y-%m-%d")
        if txn_date < first_purch: txn_date = first_purch

        pid       = random.choice(product_ids)
        uprice    = product_prices[pid]
        qty       = 1 if uprice > 1000 else random.choice([1, 1, 1, 2])
        disc      = float(random.choice([0, 0, 0, 0, 5, 10, 15, 20]))
        total     = round(uprice * qty * (1 - disc / 100), 2)
        payment   = payments[txn_id % len(payments)]
        is_return = (txn_id % 47 == 0)

        txn_rows.append((
            f"TXN-{txn_id:06d}", txn_date,
            cid, store_id, adv_id, pid,
            qty, uprice, disc, total, payment, is_return
        ))
        txn_id += 1

txn_schema = StructType([
    StructField("transaction_id",   StringType()),
    StructField("transaction_date", StringType()),
    StructField("client_id",        IntegerType()),
    StructField("store_id",         IntegerType()),
    StructField("advisor_id",       IntegerType()),
    StructField("product_id",       StringType()),
    StructField("quantity",         IntegerType()),
    StructField("unit_price",       DoubleType()),
    StructField("discount_pct",     DoubleType()),
    StructField("total_amount",     DoubleType()),
    StructField("payment_method",   StringType()),
    StructField("is_return",        BooleanType()),
])

df_txn = spark.createDataFrame(txn_rows, schema=txn_schema) \
    .withColumn("transaction_date", F.to_date("transaction_date"))
df_txn.write.mode("append").saveAsTable(f"{DB}.transactions")
print(f"Inserted {df_txn.count()} transactions")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 7. Verify

# COMMAND ----------

for tbl in ["stores","advisors","products","clients","transactions"]:
    count = spark.sql(f"SELECT COUNT(*) AS n FROM {DB}.{tbl}").collect()[0]["n"]
    print(f"  {DB}.{tbl:15s} → {count:,} rows")

# COMMAND ----------

# MAGIC %md
# MAGIC ## ✅ Setup Complete
# MAGIC
# MAGIC All tables are ready in `ramin_aws_serverless_sandbox.harry_rosen`.
# MAGIC
# MAGIC **Next step:** Run `01_harry_rosen_genie_demo_queries` to explore the data,
# MAGIC then set up the Genie space following `02_harry_rosen_genie_config`.

# COMMAND ----------

!bash <(curl -sL https://raw.githubusercontent.com/databricks-solutions/ai-dev-kit/main/install.sh)


# COMMAND ----------


