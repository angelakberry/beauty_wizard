import json, uuid, re

# --- Define your tables and relationships ---
tables = {
    "beauty_feeds": [
        ("uniq_id", "varchar"),
        ("type", "varchar"),
        ("brand", "varchar"),
        ("name", "varchar"),
        ("price", "varchar"),
        ("ingredients", "text"),
    ],
    "cosmetic_p": [
        ("Label", "varchar"),
        ("brand", "varchar"),
        ("name", "varchar"),
        ("price", "varchar"),
        ("rank", "varchar"),
        ("ingredients", "text"),
        ("Combination", "varchar"),
        ("Dry", "varchar"),
        ("Normal", "varchar"),
        ("Oily", "varchar"),
        ("Sensitive", "varchar"),
    ],
    "cscpopendata": [
        ("CDPHId", "varchar"),
        ("ProductName", "varchar"),
        ("CompanyName", "varchar"),
        ("CasNumber", "varchar"),
    ],
}

relationships = [
    ("cosmetic_p", "brand", "beauty_feeds", "brand"),
    ("cosmetic_p", "name", "beauty_feeds", "name"),
    ("cscpopendata", "CompanyName", "beauty_feeds", "brand"),
    ("cscpopendata", "ProductName", "beauty_feeds", "name"),
]

# --- Utility: detect primary key column names ---
def is_primary_key(name):
    return bool(re.search(r"(^id$|_id$|uniq_id|CDPHId|ProductId)", name, re.IGNORECASE))

# --- Initialize base schema ---
schema = {
    "$schema": "https://raw.githubusercontent.com/dineug/erd-editor/main/json-schema/schema.json",
    "version": "3.0.0",
    "settings": {
        "width": 2000,
        "height": 2000,
        "scrollTop": 0,
        "scrollLeft": 0,
        "zoomLevel": 1,
        "show": 431,
        "database": 4,
        "databaseName": "",
        "canvasType": "ERD",
        "language": 1,
        "tableNameCase": 4,
        "columnNameCase": 2,
        "bracketType": 1,
        "relationshipDataTypeSync": True,
        "relationshipOptimization": False,
        "columnOrder": [1, 2, 4, 8, 16, 32, 64],
        "maxWidthComment": -1,
        "ignoreSaveSettings": 0,
    },
    "doc": {"tableIds": [], "relationshipIds": [], "indexIds": [], "memoIds": []},
    "collections": {
        "tableEntities": {},
        "tableColumnEntities": {},
        "relationshipEntities": {},
        "indexEntities": {},
        "indexColumnEntities": {},
        "memoEntities": {},
    },
}

# --- Build tables ---
table_ids = {}
column_ids = {}

x_offset = 100
for i, (tname, cols) in enumerate(tables.items()):
    tid = str(uuid.uuid4())
    table_ids[tname] = tid
    schema["doc"]["tableIds"].append(tid)
    schema["collections"]["tableEntities"][tid] = {
        "id": tid,
        "name": tname,
        "comment": "",
        "color": None,
        "x": x_offset,
        "y": 100,
        "widthName": 120,
        "widthComment": 120,
        "visible": True,
    }
    x_offset += 300

    for cname, dtype in cols:
        cid = str(uuid.uuid4())
        column_ids[(tname, cname)] = cid
        schema["collections"]["tableColumnEntities"][cid] = {
            "id": cid,
            "tableId": tid,
            "name": cname,
            "dataType": dtype,
            "comment": "",
            "option": {
                "autoIncrement": False,
                "primaryKey": is_primary_key(cname),
                "unique": False,
                "notNull": is_primary_key(cname),
                "default": "",
            },
        }

# --- Build relationships ---
for (from_t, from_c, to_t, to_c) in relationships:
    rid = str(uuid.uuid4())
    schema["doc"]["relationshipIds"].append(rid)
    schema["collections"]["relationshipEntities"][rid] = {
        "id": rid,
        "identification": False,
        "endpoint": {
            "start": column_ids[(from_t, from_c)],
            "end": column_ids[(to_t, to_c)],
            "startType": "1",
            "endType": "n",
        },
    }

# --- Save output ---
with open("database.vuerd.json", "w", encoding="utf-8") as f:
    json.dump(schema, f, indent=2)

print("✅ database.vuerd.json created — includes primary keys and valid schema!")
