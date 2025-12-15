```mermaid
erDiagram
  Products ||--o{ ProductIngredients : contains
  Ingredients ||--o{ ProductIngredients : used_in
  Ingredients ||--o{ ChemicalReports : reported_as

  Products {
    int product_id PK
    text label
    text brand
    text product_name
    real price
    real rank
    int skin_combination
    int skin_dry
    int skin_normal
    int skin_oily
    int skin_sensitive
    text bf_type
    real bf_price
    text match_quality
  }

  Ingredients {
    int ingredient_id PK
    text ingredient_name
  }

  ProductIngredients {
    int product_id FK
    int ingredient_id FK
    int sequence
  }

  ChemicalReports {
    int report_id PK
    int ingredient_id FK
    text chemical_id
    text first_reported
    text most_recent_report
    text discontinued_date
    int report_count
    text cas_number
  }
