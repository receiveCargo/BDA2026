import csv
import json
import os
import re

# TODO: remove duplicates

input_folder = "../data"
output_csv = "data/input/csv/json_data.csv"

fieldnames = [
    "Filename",
    "vehicleBrand",
    "vehicleModel",
    "vehicleVariant",
    "vehicleType",
    "registrationNumber",
    "productionDate",
    "mileageFromOdometer",
    "vehicleTransmission",
    "fuelType",
    "drivetrain",
    "basePrice",
    "fuelConsumptionCombined",
    "emissionsCO2",
    "companyName",
    "companyLocation",
    "sellerType",
    "locationCity",
    "locationRegion",
]

def extract_product_json(html_text):
    """
    Finds and returns the JSON object that starts with {"productInfo": ...}.
    Returns None if not found or invalid.
    """
    match = re.search(r'\{"productInfo":\s*\{.*?\}\}', html_text, re.DOTALL)
    if not match:
        return None
    try:
        json_text = match.group(0)
        return json.loads(json_text)
    except json.JSONDecodeError:
        return None

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
        
        if "Poistettu myynnistä" in html:
            print("{} not for sale anymore".format(filename))
            continue

        if "Myyty Nettiauton kautta" in html:
            print("{} sold".format(filename))
            continue

        data = extract_product_json(html)
        if not data:
            print("{} has no productInfo JSON".format(filename))
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
            print("{} base price less than 1000€".format(filename))
            continue

        count+=1
        writer.writerow(row)
        if count%1000==0:
            print("Parsed {} files".format(count))

print(f"\n{count} rows written to '{output_csv}'")
