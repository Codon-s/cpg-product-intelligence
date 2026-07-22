''' Data Extraction Script from OpenFoodFacts JSONL data dump '''
import gzip
import json
import pandas as pd

# 1. Specify the path to your downloaded OFF JSONL dump
file_path = "openfoodfacts-products.jsonl.gz" #pylint: disable=invalid-name

items = ['topo chico', 'fairlife']


for item in items:

    coca_cola_products = []
    rows_processed = 0

    print("Starting data extraction. This may take a while depending on your CPU...")

    # 2. Open the compressed file and read it line-by-line
    with gzip.open(file_path, 'rt', encoding='utf-8') as f:
        for line in f:
            rows_processed += 1

            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                continue

            # 3. Extract strings for matching and convert to lowercase for case-insensitive search
            product_name = str(record.get('product_name', '')).lower()
            brands = str(record.get('brands', '')).lower()
            brands_tags = record.get('brands_tags', [])

            if not isinstance(brands_tags, list):
                brands_tags = []

            # 4. UPDATED FILTER LOGIC: Check product_name, brands, or brands_tags
            is_cocacola = (
                item in product_name or
                item in product_name or
                item in brands or
                item in brands or
                any(item in str(tag).lower() for tag in brands_tags)
            )

            # 5. Extract data if it matches our criteria
            if is_cocacola:
                nutriments = record.get("nutriments", {})

                extracted_data = {
                    "code": record.get("code") or record.get("_id"),
                    "product_name": record.get("product_name"),
                    "brands": record.get("brands"),
                    "categories_tags": ", ".join(record.get("categories_tags", [])) if isinstance(record.get("categories_tags"), list) else "", #pylint: disable=line-too-long
                    "countries_tags": ", ".join(record.get("countries_tags", [])) if isinstance(record.get("countries_tags"), list) else "", #pylint: disable=line-too-long
                    "packaging_tags": ", ".join(record.get("packaging_tags", [])) if isinstance(record.get("packaging_tags"), list) else "", #pylint: disable=line-too-long
                    "stores": record.get("stores"),
                    "purchase_places": record.get("purchase_places"),
                    "nutriscore_grade": record.get("nutriscore_grade"),
                    "nova_group": record.get("nova_group"),
                    "ecoscore_grade": record.get("ecoscore_grade"),
                    "ingredients_text": record.get("ingredients_text"),
                    "nutriments.sugars_100g": nutriments.get("sugars_100g"),
                    "nutriments.energy-kcal_100g": nutriments.get("energy-kcal_100g")
                }
                coca_cola_products.append(extracted_data)

            # 6. Progress tracker
            if rows_processed % 500000 == 0:
                print(f"Processed {rows_processed:,} products... Found {len(coca_cola_products)} {item} items so far.") #pylint: disable=line-too-long

    print(f"\nExtraction complete! Total {item} products found: {len(coca_cola_products)}")

    # 7. Convert to DataFrame and clean tags
    df = pd.DataFrame(coca_cola_products)

    for col in ['categories_tags', 'countries_tags', 'packaging_tags']:
        if col in df.columns:
            df[col] = df[col].str.replace(r'en:|fr:|es:', '', regex=True)

    # 8. Save to CSV
    df.to_csv(f"{item}_from_dump.csv", index=False, encoding='utf-8')
    print(f"Data successfully saved to '{item}_from_dump.csv'!")
    