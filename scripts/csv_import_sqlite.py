from pathlib import Path
import sqlite3
import pandas as pd
import re

# ------------------------------------------------------
# Paths and database connection
# ------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = BASE_DIR / "db" / "BeautyWiz.db"

DB_PATH.parent.mkdir(exist_ok=True)

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()
cursor.execute("PRAGMA foreign_keys = ON;")

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
    name = name.strip()
    name = re.sub(r"\s+", " ", name)
    return name.lower()

# ------------------------------------------------------
# Load and normalize CSV files
# ------------------------------------------------------
cosmetic = pd.read_csv(DATA_DIR / "cosmetic_p.csv")
beauty = pd.read_csv(DATA_DIR / "BeautyFeeds.csv")
cscp = pd.read_csv(DATA_DIR / "cscpopendata.csv")

cosmetic = normalize_columns(cosmetic)
beauty = normalize_columns(beauty)
cscp = normalize_columns(cscp)

# ------------------------------------------------------
# Insert products
# ------------------------------------------------------
def insert_products():
    for _, row in cosmetic.iterrows():
        cursor.execute("""
            INSERT INTO Products (
                label,
                brand,
                product_name,
                price,
                rank,
                skin_combination,
                skin_dry,
                skin_normal,
                skin_oily,
                skin_sensitive
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
def build_ingredients():
    ingredient_set = set()

    # From cosmetic products
    for ing_list in cosmetic.get("ingredients", []):
        if pd.isna(ing_list):
            continue
        ingredient_set.update(
            normalize_ingredient(i)
            for i in ing_list.split(",")
            if normalize_ingredient(i)
        )

    # From BeautyFeeds
    if "ingredients" in beauty.columns:
        for ing_list in beauty["ingredients"]:
            if pd.isna(ing_list):
                continue
            ingredient_set.update(
                normalize_ingredient(i)
                for i in ing_list.split(",")
                if normalize_ingredient(i)
            )

    # From CSCP chemical names
    if "chemicalname" in cscp.columns:
        ingredient_set.update(
            normalize_ingredient(i)
            for i in cscp["chemicalname"]
            if normalize_ingredient(i)
        )

    for ing in ingredient_set:
        cursor.execute(
            "INSERT OR IGNORE INTO Ingredients (ingredient_name) VALUES (?)",
            (ing,)
        )

    conn.commit()
    print(f"✓ Ingredients loaded ({len(ingredient_set)} total)")

# ------------------------------------------------------
# Link products to ingredients using business keys
# ------------------------------------------------------
def link_product_ingredients():
    cosmetic_lookup = (
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

        if key not in cosmetic_lookup.index:
            continue

        ing_string = cosmetic_lookup.loc[key, "ingredients"]

        for seq, ing in enumerate(ing_string.split(","), start=1):
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
    print(f"✓ Product–ingredient relationships created ({linked} products linked)")

# ------------------------------------------------------
# Load hazard data
# ------------------------------------------------------
def load_hazard_data():
    if "ingredients" not in beauty.columns:
        print("⚠ No ingredient column found in BeautyFeeds; skipping hazard load")
        return

    for _, row in beauty.iterrows():
        ing_norm = normalize_ingredient(row.get("ingredients"))

        ingredient_id = cursor.execute(
            "SELECT ingredient_id FROM Ingredients WHERE ingredient_name = ?",
            (ing_norm,)
        ).fetchone()

        if ingredient_id:
            cursor.execute("""
                INSERT INTO IngredientHazards (
                    ingredient_id,
                    hazard_score,
                    concerns,
                    regulation_status,
                    source_urls
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
def load_cscp_data():
    if "chemicalname" not in cscp.columns:
        print("⚠ No chemicalname column found; skipping chemical reports")
        return

    for _, row in cscp.iterrows():
        ing_norm = normalize_ingredient(row.get("chemicalname"))

        ingredient_id = cursor.execute(
            "SELECT ingredient_id FROM Ingredients WHERE ingredient_name = ?",
            (ing_norm,)
        ).fetchone()

        if ingredient_id:
            cursor.execute("""
                INSERT INTO ChemicalReports (
                    ingredient_id,
                    chemical_id,
                    first_reported,
                    most_recent_report,
                    discontinued_date,
                    report_count
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
    print("✓ Chemical data loaded")

# ------------------------------------------------------
# Run ETL pipeline
# ------------------------------------------------------
insert_products()
build_ingredients()
link_product_ingredients()
load_hazard_data()
load_cscp_data()

conn.close()
print("\nAll data successfully uploaded into BeautyWiz.db!")
