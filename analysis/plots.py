import pandas as pd
import matplotlib.pyplot as plt

# Use this to generate plots from the .csv
# Run this script from the root folder

# Limit plotting to only car models with at least n data points
data_points_required=100

df = pd.read_csv('data/input/csv/json_data.csv')
df['productionDate'] = pd.to_numeric(df['productionDate'], errors='coerce')
df['basePrice'] = pd.to_numeric(df['basePrice'], errors='coerce')
df_clean = df.dropna(subset=['productionDate', 'basePrice'])
grouped = df_clean.groupby(['vehicleBrand', 'vehicleModel', 'vehicleVariant'])

for name, group in grouped:
    if len(group) <= data_points_required:
        continue
    plt.figure(figsize=(10, 6))
    plt.scatter(group['productionDate'], group['basePrice'], alpha=0.7, edgecolors='w', s=50)    
    brand, model, variant = name
    
    plt.title(f'{brand} {model} {variant} (n={len(group)})')
    plt.xlabel('Production Year')
    plt.ylabel('Base Price (€)')
    plt.grid(True, linestyle='--', alpha=0.7)
    
    filename = f"{brand}_{model}_{variant}.png".replace('/', '_')
    plt.savefig("data/output/png/price/year/"+filename, dpi=100, bbox_inches='tight')
    plt.close()

print("Plots generated successfully for groups with more than {} data points.".format(data_points_required))

