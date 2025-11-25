import csv
import os
from parse_json import input_folder, fieldnames, extract_product_json

output_csv = "data/input/csv/labels.csv"

def parse_labels():
    with open(output_csv, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        count=0

        for filename in os.listdir(input_folder):
            if not filename.endswith(".html"):
                continue

            filepath = os.path.join(input_folder, filename)
            with open(filepath, "r", encoding="utf-8") as f:
                html = f.read()
            
            if "Myyty Nettiauton kautta" in html:
                data = extract_product_json(html)
                if not data:
                    continue

                product = data.get("productInfo", {})
                row = {field: "" for field in fieldnames}
                row["Filename"] = filename

                for key in fieldnames:
                    if key in product:
                        row[key] = product[key]

                if "fuelConsumption" in product:
                    row["fuelConsumptionCombined"] = product["fuelConsumption"].get("fuelConsumptionCombined", "")

                if int(row["basePrice"]) < 1000:
                    continue

                count+=1
                writer.writerow(row)
                if count%1000==0:
                    print("Parsed {} files".format(count))

    print(f"\n{count} rows written to '{output_csv}'")

parse_labels()