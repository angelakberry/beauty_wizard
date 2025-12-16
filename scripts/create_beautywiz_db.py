from pathlib import Path
import sqlite3

# ------------------------------------------------------
# Resolve project root and database path
# ------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = PROJECT_ROOT / "BeautyWiz.db"

# ------------------------------------------------------
# Connect to the database (creates it if missing)
# ------------------------------------------------------
conn = sqlite3.connect(DB_PATH)
conn.execute("PRAGMA foreign_keys = ON;")
cursor = conn.cursor()

# ------------------------------------------------------
# Drop tables if re-running (order matters)
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

cursor.execute("""
CREATE TABLE Ingredients (
    ingredient_id INTEGER PRIMARY KEY AUTOINCREMENT,
    ingredient_name TEXT UNIQUE NOT NULL,
    alt_names TEXT
);
""")

cursor.execute("""
CREATE TABLE ProductIngredients (
    product_id INTEGER NOT NULL,
    ingredient_id INTEGER NOT NULL,
    sequence INTEGER,
    PRIMARY KEY (product_id, ingredient_id),
    FOREIGN KEY (product_id) REFERENCES Products(product_id) ON DELETE CASCADE,
    FOREIGN KEY (ingredient_id) REFERENCES Ingredients(ingredient_id) ON DELETE CASCADE
);
""")

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
# Indexes (performance)
# ------------------------------------------------------
cursor.executescript("""
CREATE INDEX IF NOT EXISTS idx_ingredients_name
    ON Ingredients(ingredient_name);

CREATE INDEX IF NOT EXISTS idx_pi_product
    ON ProductIngredients(product_id);

CREATE INDEX IF NOT EXISTS idx_pi_ingredient
    ON ProductIngredients(ingredient_id);

CREATE INDEX IF NOT EXISTS idx_cr_ingredient
    ON ChemicalReports(ingredient_id);
""")

conn.commit()
conn.close()

print(f"BeautyWiz.db created successfully at: {DB_PATH}")