import pandas as pd
import matplotlib.pyplot as plt
import os

# Use this to generate plots from the .csv
# Run this script from the root folder

# Plot price of unique car models with at least n data points
# With respect to given variable ie. productionDate, mileageFromOdometer etc
def plot_price(variable, data_points_required, input, output):
    df = pd.read_csv(input)
    df[variable] = pd.to_numeric(df[variable], errors='coerce')
    df['basePrice'] = pd.to_numeric(df['basePrice'], errors='coerce')
    df_clean = df.dropna(subset=[variable, 'basePrice'])
    grouped = df_clean.groupby(['vehicleBrand', 'vehicleModel', 'vehicleVariant'])

    output_path="{}/price/{}".format(output, variable)

    if not os.path.exists(output_path):
        os.makedirs(output_path)

    for name, group in grouped:
        if len(group) <= data_points_required:
            continue
        plt.figure(figsize=(10, 6))
        plt.scatter(group[variable], group['basePrice'], alpha=0.7, edgecolors='w', s=50)    
        brand, model, variant = name
        
        plt.title(f'{brand} {model} {variant} (n={len(group)})')
        plt.xlabel(variable)
        plt.ylabel("'Base Price (€)'")
        plt.grid(True, linestyle='--', alpha=0.7)
        
        filename = f"{brand}_{model}_{variant}.png".replace('/', '_')
        plt.savefig("{}/{}".format(output_path, filename), dpi=100, bbox_inches='tight')
        plt.close()

# Plots for entire dataset
plot_price("productionDate", 100, 'data/input/csv/json_data.csv', 'data/output/png')
plot_price("mileageFromOdometer", 100, 'data/input/csv/json_data.csv', 'data/output/png')

# Plots for labels
plot_price("productionDate", 10, 'data/input/csv/labels.csv', 'data/output/png/labels')
plot_price("mileageFromOdometer", 10, 'data/input/csv/labels.csv', 'data/output/png/labels')