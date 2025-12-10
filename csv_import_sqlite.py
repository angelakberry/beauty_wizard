import sqlite3
import pandas as pd
import re

# ------------------------------------------------------
# Connect to database
# ------------------------------------------------------
conn = sqlite3.connect("BeautyWiz.db")
cursor = conn.cursor()
cursor.execute("PRAGMA foreign_keys = ON;")

# ------------------------------------------------------
# Normalize ingredient names
# ------------------------------------------------------
def normalize(name):
    if pd.isna(name):
        return None
    name = name.strip()
    name = re.sub(r"\s+", " ", name)
    return name.lower()  # normalize to lowercase for matching consistency

# ------------------------------------------------------
# Load CSV files
# ------------------------------------------------------
cosmetic = pd.read_csv("cosmetic_p.csv")
beauty = pd.read_csv("BeautyFeeds.csv")
cscp = pd.read_csv("cscpopendata.csv")

# ------------------------------------------------------
# Insert products
# ------------------------------------------------------
def insert_products():
    for _, row in cosmetic.iterrows():
        cursor.execute("""
            INSERT INTO Products (
                label, brand, product_name, price, rank,
                skin_combination, skin_dry, skin_normal, skin_oily, skin_sensitive
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            row["Label"],
            row["brand"],
            row["name"],
            row["price"],
            row["rank"],
            row["Combination"],
            row["Dry"],
            row["Normal"],
            row["Oily"],
            row["Sensitive"],
        ))

    conn.commit()
    print("✓ Products loaded")

# ------------------------------------------------------
# Build ingredient master list
# ------------------------------------------------------
def build_ingredients():

    # Collect ingredients from product file
    ingredient_set = set()

    for ing_list in cosmetic["ingredients"]:
        if pd.isna(ing_list):
            continue
        ingredients = [normalize(i) for i in ing_list.split(",")]
        ingredient_set.update(ingredients)

    # Collect ingredients from hazard and chemical data
    ingredient_set.update([normalize(i) for i in beauty["ingredient"]])
    ingredient_set.update([normalize(i) for i in cscp["ChemicalName"]])

    # Remove Nones
    ingredient_set = {i for i in ingredient_set if i}

    # Insert all unique ingredients
    for ing in ingredient_set:
        cursor.execute(
            "INSERT OR IGNORE INTO Ingredients (ingredient_name) VALUES (?)",
            (ing,)
        )

    conn.commit()
    print(f"✓ Ingredients loaded ({len(ingredient_set)} total)")

# ------------------------------------------------------
# Link products and ingredients
# ------------------------------------------------------
def link_product_ingredients():
    products = cursor.execute("SELECT product_id, product_name FROM Products").fetchall()

    for product_id, _ in products:
        # Get ingredient list from CSV
        ing_string = cosmetic.loc[product_id - 1, "ingredients"]

        if pd.isna(ing_string):
            continue

        ingredients = [normalize(i) for i in ing_string.split(",")]

        for sequence, ing in enumerate(ingredients, start=1):
            ingredient_id = cursor.execute(
                "SELECT ingredient_id FROM Ingredients WHERE ingredient_name = ?",
                (ing,)
            ).fetchone()

            if ingredient_id:
                cursor.execute("""
                    INSERT OR IGNORE INTO ProductIngredients (product_id, ingredient_id, sequence)
                    VALUES (?, ?, ?)
                """, (product_id, ingredient_id[0], sequence))

    conn.commit()
    print("✓ Product–ingredient relationships created")

# ------------------------------------------------------
# Load hazard data
# ------------------------------------------------------
def load_hazard_data():
    for _, row in beauty.iterrows():
        ing_norm = normalize(row["ingredient"])

        ingredient_id = cursor.execute(
            "SELECT ingredient_id FROM Ingredients WHERE ingredient_name = ?",
            (ing_norm,)
        ).fetchone()

        if ingredient_id:
            cursor.execute("""
                INSERT INTO IngredientHazards (ingredient_id, hazard_score, concerns, regulation_status, source_urls)
                VALUES (?, ?, ?, ?, ?)
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
    for _, row in cscp.iterrows():
        ing_norm = normalize(row["ChemicalName"])

        ingredient_id = cursor.execute(
            "SELECT ingredient_id FROM Ingredients WHERE ingredient_name = ?",
            (ing_norm,)
        ).fetchone()

        if ingredient_id:
            cursor.execute("""
                INSERT INTO ChemicalReports (
                    ingredient_id, chemical_id, first_reported, most_recent_report,
                    discontinued_date, report_count
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, (
                ingredient_id[0],
                row["ChemicalID"],
                row["ChemicalDateCreated"],
                row["MostRecentDateReported"],
                row["DiscontinuedDate"],
                row["ChemicalCount"]
            ))

    conn.commit()
    print("✓ Chemical data loaded")

# ------------------------------------------------------
# Run the steps
# ------------------------------------------------------
insert_products()
build_ingredients()
link_product_ingredients()
load_hazard_data()
load_cscp_data()

print("\n All data successfully uploaded into BeautyWiz.db!")
