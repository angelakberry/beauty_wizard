import sqlite3

# ------------------------------------------------------
# Connect to Database
# ------------------------------------------------------
# Creates BeautyWiz.db in the working directory
conn = sqlite3.connect("BeautyWiz.db")
cursor = conn.cursor()

# Enable foreign key constraints
cursor.execute("PRAGMA foreign_keys = ON;")


# ------------------------------------------------------
# Drop tables if re-running
# ------------------------------------------------------
tables = [
    "ProductIngredients",
    "IngredientHazards",
    "ChemicalReports",
    "Ingredients",
    "Products"
]

for table in tables:
    cursor.execute(f"DROP TABLE IF EXISTS {table};")


# ------------------------------------------------------
# Create tables
# ------------------------------------------------------

# PRODUCTS table
cursor.execute("""
CREATE TABLE Products (
    product_id INTEGER PRIMARY KEY AUTOINCREMENT,
    label TEXT,
    brand TEXT,
    product_name TEXT,
    price REAL,
    rank REAL,
    skin_combination INTEGER,
    skin_dry INTEGER,
    skin_normal INTEGER,
    skin_oily INTEGER,
    skin_sensitive INTEGER
);
""")

# INGREDIENTS table
cursor.execute("""
CREATE TABLE Ingredients (
    ingredient_id INTEGER PRIMARY KEY AUTOINCREMENT,
    ingredient_name TEXT UNIQUE NOT NULL,
    alt_names TEXT
);
""")

# PRODUCT to INGREDIENT (MANY-TO-MANY table)
cursor.execute("""
CREATE TABLE ProductIngredients (
    product_id INTEGER,
    ingredient_id INTEGER,
    sequence INTEGER,
    PRIMARY KEY (product_id, ingredient_id),
    FOREIGN KEY (product_id) REFERENCES Products(product_id) ON DELETE CASCADE,
    FOREIGN KEY (ingredient_id) REFERENCES Ingredients(ingredient_id) ON DELETE CASCADE
);
""")

# HAZARD / SCIENCE FEEDS table
cursor.execute("""
CREATE TABLE IngredientHazards (
    hazard_id INTEGER PRIMARY KEY AUTOINCREMENT,
    ingredient_id INTEGER NOT NULL,
    hazard_score REAL,
    concerns TEXT,
    regulation_status TEXT,
    source_urls TEXT,
    FOREIGN KEY (ingredient_id) REFERENCES Ingredients(ingredient_id) ON DELETE CASCADE
);
""")

# REGULATORY / CHEMICAL REPORTING (cscpopendata.csv)
cursor.execute("""
CREATE TABLE ChemicalReports (
    report_id INTEGER PRIMARY KEY AUTOINCREMENT,
    ingredient_id INTEGER NOT NULL,
    chemical_id TEXT,
    first_reported TEXT,
    most_recent_report TEXT,
    discontinued_date TEXT,
    report_count INTEGER,
    FOREIGN KEY (ingredient_id) REFERENCES Ingredients(ingredient_id) ON DELETE CASCADE
);
""")


# ------------------------------------------------------
# Commit changes
# ------------------------------------------------------
conn.commit()
conn.close()

print("BeautyWiz.db created successfully!")
