import sqlite3

# ------------------------------------------------------
# Connect to the database
# ------------------------------------------------------
# Creates BeautyWiz.db in /db
conn = sqlite3.connect("db/BeautyWiz.db")
cursor = conn.cursor()

# Enable foreign key enforcement in SQLite
cursor.execute("PRAGMA foreign_keys = ON;")

# ------------------------------------------------------
# Drop tables if the script is re-run
# The order matters because of foreign key dependencies
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

# Products table
# Core identifying fields are required to prevent incomplete product records
cursor.execute("""
CREATE TABLE Products (
    product_id INTEGER PRIMARY KEY AUTOINCREMENT,
    label TEXT NOT NULL,
    brand TEXT NOT NULL,
    product_name TEXT NOT NULL,
    price REAL,
    rank REAL,
    skin_combination INTEGER,
    skin_dry INTEGER,
    skin_normal INTEGER,
    skin_oily INTEGER,
    skin_sensitive INTEGER
);
""")

# Ingredients table
# Ingredient names are unique and required to support reliable joins
cursor.execute("""
CREATE TABLE Ingredients (
    ingredient_id INTEGER PRIMARY KEY AUTOINCREMENT,
    ingredient_name TEXT UNIQUE NOT NULL,
    alt_names TEXT
);
""")

# Product to ingredient relationship table
# This table models the many to many relationship between products and ingredients
cursor.execute("""
CREATE TABLE ProductIngredients (
    product_id INTEGER NOT NULL,
    ingredient_id INTEGER NOT NULL,
    sequence INTEGER,
    PRIMARY KEY (product_id, ingredient_id),
    FOREIGN KEY (product_id)
        REFERENCES Products(product_id)
        ON DELETE CASCADE,
    FOREIGN KEY (ingredient_id)
        REFERENCES Ingredients(ingredient_id)
        ON DELETE CASCADE
);
""")

# Ingredient hazard information
# This table stores risk and regulatory metadata for ingredients
cursor.execute("""
CREATE TABLE IngredientHazards (
    hazard_id INTEGER PRIMARY KEY AUTOINCREMENT,
    ingredient_id INTEGER NOT NULL,
    hazard_score REAL,
    concerns TEXT,
    regulation_status TEXT,
    source_urls TEXT,
    FOREIGN KEY (ingredient_id)
        REFERENCES Ingredients(ingredient_id)
        ON DELETE CASCADE
);
""")

# Chemical reporting data
# This table captures reporting timelines and counts from regulatory sources
cursor.execute("""
CREATE TABLE ChemicalReports (
    report_id INTEGER PRIMARY KEY AUTOINCREMENT,
    ingredient_id INTEGER NOT NULL,
    chemical_id TEXT,
    first_reported TEXT,
    most_recent_report TEXT,
    discontinued_date TEXT,
    report_count INTEGER,
    FOREIGN KEY (ingredient_id)
        REFERENCES Ingredients(ingredient_id)
        ON DELETE CASCADE
);
""")

# ------------------------------------------------------
# Create indexes to support query performance
# ------------------------------------------------------

# Speeds up ingredient name lookups during loading and analysis
cursor.execute("""
CREATE INDEX idx_ingredients_name
ON Ingredients(ingredient_name);
""")

# Improves join performance from products to ingredients
cursor.execute("""
CREATE INDEX idx_productingredients_product
ON ProductIngredients(product_id);
""")

# Improves join performance from ingredients to products
cursor.execute("""
CREATE INDEX idx_productingredients_ingredient
ON ProductIngredients(ingredient_id);
""")

# Supports faster aggregation of hazard data by ingredient
cursor.execute("""
CREATE INDEX idx_hazards_ingredient
ON IngredientHazards(ingredient_id);
""")

# ------------------------------------------------------
# Commit changes and close the connection
# ------------------------------------------------------
conn.commit()
conn.close()

print("BeautyWiz.db created successfully!")
