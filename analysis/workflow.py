import pandas as pd
import stan
import numpy as np
import webbrowser

# TODO: create dataset of sold cars with scripts/parse_json.py and utilize it in analysis
# TODO: fix broken filters (basePrice sometimes less than 1000€, sold listing appear in outputs)

# Load and prepare data
df = pd.read_csv('data/input/csv/json_data.csv').dropna(subset=['vehicleModel', 'productionDate','mileageFromOdometer','basePrice'])
df = df[df.mileageFromOdometer > 1000]
df = df[df.basePrice > 1000]

# Analyze each vehicle model with more than 200 entries
for model in df.vehicleModel.unique():
    subset = df[df.vehicleModel == model]
    if len(subset) < 200: continue
    
    # Prepare data
    X = np.column_stack([subset.productionDate, subset.mileageFromOdometer])
    y = subset.basePrice.values
    
    # Bayesian regression with stan
    with open('analysis/model.stan', 'r') as f:
        model_code = f.read()
    
    fit = stan.build(model_code, data={
        'N': len(X), 'date': X[:,0], 'mileage': X[:,1], 
        'price': y, 'K': 5
    })
    samples = fit.sample(num_chains=3, num_samples=50)
    
    # Extract posterior means
    alpha_mean = np.mean(samples['alpha'])
    beta_mean = np.mean(samples['beta'], axis=1)
    
 
    # Find undervalued cars (negative residuals)
    y_hat = alpha_mean + np.dot(X, beta_mean[:2])
    residuals = y - y_hat
    undervalued_indices = residuals.argsort()[:2]
    undervalued = subset.iloc[undervalued_indices]
    
    print(f"\nUndervalued {model}:")
    for i, (index, row) in enumerate(undervalued.iterrows()):
        actual_price = row['basePrice']
        predicted_price = y_hat[undervalued_indices[i]]
        discount = predicted_price - actual_price
        discount_percent = (discount / predicted_price) * 100
        
        print(f"  {row['vehicleBrand']} {row['vehicleModel']} ({row['productionDate']})")
        print(f"    Mileage: {row['mileageFromOdometer']} km")
        print(f"    Actual price: €{actual_price:.0f}")
        print(f"    Predicted price: €{predicted_price:.0f}")
        print(f"    Discount: €{discount:.0f} ({discount_percent:.1f}% below market)")
        print()

    '''
    for id in undervalued['Filename']:
            url=f"https://nettiauto.com/{id[:-5]}"
            webbrowser.open(url)
    '''