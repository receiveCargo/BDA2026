import pandas as pd
import numpy as np
import stan
import webbrowser

with open("analysis/model.stan", "r") as f:
    simple_model_code = f.read()

def optimized_bayesian_workflow(csv_file, sample_size=5000):
    """
    Optimized workflow for large datasets
    """
    # Load data
    df = pd.read_csv(csv_file)
    
    # Prepare data efficiently
    df_clean = df.dropna(subset=['basePrice', 'productionDate', 'mileageFromOdometer'])
    df_clean = df_clean[df_clean['basePrice'] > 0]
    
    # Sample if dataset is large
    if len(df_clean) > sample_size:
        df_clean = df_clean.sample(n=sample_size, random_state=42)
    
    current_year = 2024
    df_clean['age'] = current_year - df_clean['productionDate']
    
    stan_data = {
        'N': len(df_clean),
        'age': df_clean['age'].values.astype(float),
        'mileage': df_clean['mileageFromOdometer'].values.astype(float),
        'log_price': np.log(df_clean['basePrice'].values.astype(float))
    }
    
    # Fit with optimized settings
    print("Fitting simplified model...")
    posterior = stan.build(simple_model_code, data=stan_data)
    fit = posterior.sample(num_chains=2, num_samples=800, num_warmup=300)
    
    return fit, df_clean

def detect_undervalued_fast(fit, df_clean, threshold=0.9):
    """
    Fast detection of undervalued cars
    """
    samples = fit.to_frame()
    
    # Extract posterior predictive samples
    log_price_rep_columns = [col for col in samples.columns if 'log_price_rep' in col]
    log_price_rep = samples[log_price_rep_columns].values
    expected_prices = np.exp(log_price_rep)
    
    # Calculate probability of being undervalued
    actual_prices = df_clean['basePrice'].values
    undervalued_probs = []
    
    for i in range(len(actual_prices)):
        prob_undervalued = np.mean(expected_prices[:, i] > actual_prices[i])
        undervalued_probs.append(prob_undervalued)
    
    df_clean = df_clean.copy()
    df_clean['undervalued_prob'] = undervalued_probs
    df_clean['expected_price_mean'] = np.mean(expected_prices, axis=0)
    df_clean['is_undervalued'] = df_clean['undervalued_prob'] > threshold
    
    return df_clean

def fast_undervalued_detection(csv_file, sample_size=3000):
    """
    Fast workflow for undervalued car detection
    """
    print("Loading data...")
    print("Using sampled data for speed...")
    fit, df_clean = optimized_bayesian_workflow(csv_file, sample_size)

    print("Detecting undervalued cars...")
    results = detect_undervalued_fast(fit, df_clean)
    
    undervalued = results[results['is_undervalued']]
    print(f"Found {len(undervalued)} potentially undervalued cars")
    
    return results, undervalued

# Usage
if __name__ == "__main__":
    # For quick results
    results, undervalued = fast_undervalued_detection('data/input/csv/json_data.csv', sample_size=2000)
    
    if undervalued is not None:
        print("\nTop undervalued cars:")
        for _, car in undervalued.head(10).iterrows():
            discount = ((car['expected_price_mean'] - car['basePrice']) / car['expected_price_mean']) * 100
            id=car["Filename"][:-5]
            link="https://www.nettiauto.com/{}".format(id)
            print(f"Expected {car['expected_price_mean']}, price {car['basePrice']}")
            print(f"- {car['vehicleBrand']} {car['vehicleModel']}: {discount:.1f}% below expected. Link: {link}")
            webbrowser.open(link)