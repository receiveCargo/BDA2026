import pandas as pd
import stan
import numpy as np

def fit(X_standardized, y_standardized, y):
    # Bayesian regression with stan
    with open('analysis/model.stan', 'r') as f:
        model_code = f.read()

    # Prepare data for Stan
    stan_data = {
        'N': len(y),
        'K': X_standardized.shape[1],
        'X': X_standardized,
        'y': y_standardized
    }
    
    # Fit the model
    posterior = stan.build(model_code, data=stan_data, random_seed=42)
    fit = posterior.sample(num_chains=4, num_samples=1000)
    
    beta_samples = fit['beta']  # coefficients
    alpha_samples = fit['alpha']  # intercept
    sigma_samples = fit['sigma']  # residual standard deviation
    
    print("\nCoefficient Summary (standardized):")
    print(f"Production Date coefficient: {np.mean(beta_samples[:, 0]):.3f} ± {np.std(beta_samples[:, 0]):.3f}")
    print(f"Mileage coefficient: {np.mean(beta_samples[:, 1]):.3f} ± {np.std(beta_samples[:, 1]):.3f}")
    print(f"Intercept: {np.mean(alpha_samples):.3f} ± {np.std(alpha_samples):.3f}")
    print(f"Sigma: {np.mean(sigma_samples):.3f} ± {np.std(sigma_samples):.3f}")
    
    # Calculate R-squared
    y_pred = np.mean(alpha_samples) + X_standardized @ np.mean(beta_samples, axis=1)
    r_squared = 1 - np.var(y_standardized - y_pred) / np.var(y_standardized)
    print(f"R-squared: {r_squared:.3f}")

    return alpha_samples, beta_samples

def detect(X_standardized, y_standardized, y, subset):
    alpha_samples, beta_samples = fit(X_standardized, y_standardized, y)

    beta_mean = np.mean(beta_samples, axis=1)
    y_hat_standardized = np.mean(alpha_samples) + X_standardized @ beta_mean

    # Convert back to original scale
    y_hat = y_hat_standardized * y.std() + y.mean()

    residuals = y - y_hat
    undervalued_indices = residuals.argsort()[:5]
    undervalued = subset.iloc[undervalued_indices]

    print(f"\nTop 5 Undervalued {model} cars:")
    for i, (index, row) in enumerate(undervalued.iterrows()):
        actual_price = row['basePrice']
        predicted_price = y_hat[undervalued_indices[i]]
        discount = predicted_price - actual_price
        discount_percent = (discount / predicted_price) * 100
        
        print(f"  {i+1}. {row['vehicleBrand']} {row['vehicleModel']} ({row['productionDate']})")
        print(f"     Mileage: {row['mileageFromOdometer']:,.0f} km")
        print(f"     Actual price: €{actual_price:,.0f}")
        print(f"     Predicted price: €{predicted_price:,.0f}")
        print(f"     Discount: €{discount:,.0f} ({discount_percent:.1f}% below market)")
        print()

def analyze(car_model):
    subset = df[df.vehicleModel == car_model]
    if len(subset) < 200: return None, None, None
    
    print(f"\n=== Analyzing {car_model} (n={len(subset)}) ===")
    
    # Prepare data
    X = np.column_stack([subset.productionDate, subset.mileageFromOdometer])
    y = subset.basePrice.values
    
    # Standardize features for better convergence
    X_standardized = (X - X.mean(axis=0)) / X.std(axis=0)
    y_standardized = (y - y.mean()) / y.std()

    detect(X_standardized, y_standardized, y, subset)

# Load and prepare data
df = pd.read_csv('data/input/csv/json_data.csv').dropna(subset=['vehicleModel', 'productionDate','mileageFromOdometer','basePrice'])
df = df[df.mileageFromOdometer > 1000]
df = df[df.basePrice > 1000]

for model in df.vehicleModel.unique():
     analyze(model)

print("\n=== Analysis Complete ===")