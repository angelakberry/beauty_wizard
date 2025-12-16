from pathlib import Path
import sqlite3
import pandas as pd
import re

# ------------------------------------------------------
# Resolve project root, data, and DB paths
# ------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
DB_PATH = PROJECT_ROOT / "BeautyWiz.db"

# Sanity checks (safe to keep)
assert DATA_DIR.exists(), f"Data directory not found: {DATA_DIR}"
assert DB_PATH.exists(), f"Database not found: {DB_PATH}"

# ------------------------------------------------------
# Connect to database
# ------------------------------------------------------
conn = sqlite3.connect(DB_PATH)
conn.execute("PRAGMA foreign_keys = ON;")
cursor = conn.cursor()

# ------------------------------------------------------
# Utility functions
# ------------------------------------------------------
def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
    )
    return df


def normalize_ingredient(name):
    if pd.isna(name):
        return None
    return re.sub(r"\s+", " ", name.strip()).lower()

# ------------------------------------------------------
# Load CSV files
# ------------------------------------------------------
cosmetic = normalize_columns(pd.read_csv(DATA_DIR / "cosmetic_p.csv"))
beauty = normalize_columns(pd.read_csv(DATA_DIR / "BeautyFeeds.csv"))
cscp = normalize_columns(pd.read_csv(DATA_DIR / "cscpopendata.csv"))

# ------------------------------------------------------
# Insert products
# ------------------------------------------------------
for _, row in cosmetic.iterrows():
    cursor.execute("""
        INSERT INTO Products (
            label, brand, product_name, price, rank,
            skin_combination, skin_dry, skin_normal,
            skin_oily, skin_sensitive
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        row.get("label"),
        row.get("brand"),
        row.get("name"),
        row.get("price"),
        row.get("rank"),
        row.get("combination"),
        row.get("dry"),
        row.get("normal"),
        row.get("oily"),
        row.get("sensitive"),
    ))

conn.commit()
print("✓ Products loaded")

# ------------------------------------------------------
# Build ingredient master list
# ------------------------------------------------------
ingredient_set = set()

for series in [
    cosmetic.get("ingredients"),
    beauty.get("ingredients"),
    cscp.get("chemicalname")
]:
    if series is None:
        continue
    for cell in series.dropna():
        ingredient_set.update(
            normalize_ingredient(i)
            for i in str(cell).split(",")
            if normalize_ingredient(i)
        )

for ing in ingredient_set:
    cursor.execute(
        "INSERT OR IGNORE INTO Ingredients (ingredient_name) VALUES (?)",
        (ing,)
    )

conn.commit()
print(f"✓ Ingredients loaded ({len(ingredient_set)})")

# ------------------------------------------------------
# Link products to ingredients
# ------------------------------------------------------
product_lookup = (
    cosmetic
    .dropna(subset=["ingredients"])
    .set_index(["brand", "name"])
)

products = cursor.execute("""
    SELECT product_id, brand, product_name
    FROM Products
""").fetchall()

linked = 0

for product_id, brand, product_name in products:
    key = (brand, product_name)
    if key not in product_lookup.index:
        continue

    for seq, ing in enumerate(product_lookup.loc[key, "ingredients"].split(","), start=1):
        ing_norm = normalize_ingredient(ing)
        ingredient_id = cursor.execute(
            "SELECT ingredient_id FROM Ingredients WHERE ingredient_name = ?",
            (ing_norm,)
        ).fetchone()

        if ingredient_id:
            cursor.execute("""
                INSERT OR IGNORE INTO ProductIngredients
                (product_id, ingredient_id, sequence)
                VALUES (?, ?, ?)
            """, (product_id, ingredient_id[0], seq))

    linked += 1

conn.commit()
print(f"✓ Product–ingredient links created ({linked} products)")

# ------------------------------------------------------
# Load hazard data
# ------------------------------------------------------
if "ingredients" in beauty.columns:
    for _, row in beauty.iterrows():
        ing_norm = normalize_ingredient(row.get("ingredients"))
        ingredient_id = cursor.execute(
            "SELECT ingredient_id FROM Ingredients WHERE ingredient_name = ?",
            (ing_norm,)
        ).fetchone()

        if ingredient_id:
            cursor.execute("""
                INSERT INTO IngredientHazards (
                    ingredient_id, hazard_score, concerns,
                    regulation_status, source_urls
                ) VALUES (?, ?, ?, ?, ?)
            """, (
                ingredient_id[0],
                row.get("hazard_score"),
                row.get("concerns"),
                row.get("regulation_status"),
                row.get("source"),
            ))

conn.commit()
print("✓ Hazard data loaded")

# ------------------------------------------------------
# Load chemical reporting data
# ------------------------------------------------------
for _, row in cscp.iterrows():
    ing_norm = normalize_ingredient(row.get("chemicalname"))
    ingredient_id = cursor.execute(
        "SELECT ingredient_id FROM Ingredients WHERE ingredient_name = ?",
        (ing_norm,)
    ).fetchone()

    if ingredient_id:
        cursor.execute("""
            INSERT INTO ChemicalReports (
                ingredient_id, chemical_id,
                first_reported, most_recent_report,
                discontinued_date, report_count
            ) VALUES (?, ?, ?, ?, ?, ?)
        """, (
            ingredient_id[0],
            row.get("chemicalid"),
            row.get("chemicaldatecreated"),
            row.get("mostrecentdatereported"),
            row.get("discontinueddate"),
            row.get("chemicalcount"),
        ))

conn.commit()
conn.close()

print("✓ All data successfully loaded into BeautyWiz.db")