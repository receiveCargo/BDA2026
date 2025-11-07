import pandas as pd
import numpy as np
import stan
from sklearn.preprocessing import LabelEncoder
import webbrowser

def prepare_optimized_data(df, sample_fraction=0.5, min_samples_per_brand=5):
    """
    Prepare optimized data for faster sampling
    """
    # Clean data
    df_clean = df.dropna(subset=['basePrice', 'productionDate', 'mileageFromOdometer'])
    df_clean = df_clean[df_clean['basePrice'] > 0]
    
    # Sample data if too large
    if len(df_clean) > 10000:
        df_clean = df_clean.sample(frac=sample_fraction, random_state=42)
        print(f"Sampled {len(df_clean)} observations for faster processing")
    
    # Filter brands with too few observations
    brand_counts = df_clean['vehicleBrand'].value_counts()
    valid_brands = brand_counts[brand_counts >= min_samples_per_brand].index
    df_clean = df_clean[df_clean['vehicleBrand'].isin(valid_brands)]
    
    # Calculate car age
    current_year = 2024
    df_clean['age'] = current_year - df_clean['productionDate']
    
    # Use LabelEncoder for more efficient encoding
    brand_encoder = LabelEncoder()
    brands_encoded = brand_encoder.fit_transform(df_clean['vehicleBrand']) + 1
    
    # Prepare Stan data
    stan_data = {
        'N': len(df_clean),
        'N_brands': len(brand_encoder.classes_),
        'brand_id': brands_encoded.astype(int),
        'age': df_clean['age'].values.astype(float),
        'mileage': df_clean['mileageFromOdometer'].values.astype(float),
        'log_price': np.log(df_clean['basePrice'].values.astype(float))
    }
    
    return stan_data, df_clean, brand_encoder

def fit_fast_model(stan_data, model_code, iterations=1000, warmup=500, chains=2):
    """
    Fit model with optimized settings
    """
    print("Compiling optimized Stan model...")
    posterior = stan.build(model_code, data=stan_data)
    
    print(f"Fitting with {chains} chains, {iterations} iterations...")
    fit = posterior.sample(
        num_chains=chains, 
        num_samples=iterations, 
        num_warmup=warmup,
        max_depth=10,  # Reduce tree depth for speed
        delta=0.9      # Less strict convergence criterion
    )
    
    return fit

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

def process_in_batches(csv_file, batch_size=10000, samples_per_batch=500):
    """
    Process very large files in batches
    """
    results = []
    
    # Read CSV in chunks
    for i, chunk in enumerate(pd.read_csv(csv_file, chunksize=batch_size)):
        print(f"Processing batch {i+1}...")
        
        try:
            fit, df_batch = optimized_bayesian_workflow_chunk(chunk, samples_per_batch)
            batch_results = detect_undervalued_fast(fit, df_batch)
            results.append(batch_results)
        except Exception as e:
            print(f"Error processing batch {i+1}: {e}")
            continue
    
    # Combine results
    if results:
        final_results = pd.concat(results, ignore_index=True)
        return final_results
    else:
        return pd.DataFrame()

def optimized_bayesian_workflow_chunk(df_chunk, sample_size=500):
    """
    Process a single chunk of data
    """
    # Clean and prepare the chunk
    df_clean = df_chunk.dropna(subset=['basePrice', 'productionDate', 'mileageFromOdometer'])
    df_clean = df_clean[df_clean['basePrice'] >= 1000]
    
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
    
    # Quick fit with minimal iterations
    posterior = stan.build(simple_model_code, data=stan_data)
    fit = posterior.sample(num_chains=1, num_samples=400, num_warmup=200)
    
    return fit, df_clean

def fast_undervalued_detection(csv_file, use_sampling=True, sample_size=3000):
    """
    Fast workflow for undervalued car detection
    """
    print("Loading data...")
    df = pd.read_csv(csv_file)
    
    if use_sampling:
        print("Using sampled data for speed...")
        fit, df_clean = optimized_bayesian_workflow(csv_file, sample_size)
    else:
        print("Using batch processing...")
        df_clean = process_in_batches(csv_file)
        # For batch processing, we might use a simpler statistical approach
        # since we already have the data processed in batches
    
    if use_sampling:
        print("Detecting undervalued cars...")
        results = detect_undervalued_fast(fit, df_clean)
        
        undervalued = results[results['is_undervalued']]
        print(f"Found {len(undervalued)} potentially undervalued cars")
        
        return results, undervalued
    else:
        return df_clean, None

# Usage
if __name__ == "__main__":
    # For quick results
    results, undervalued = fast_undervalued_detection('data/input/csv/json_data.csv', use_sampling=True, sample_size=2000)
    
    if undervalued is not None:
        print("\nTop undervalued cars:")
        for _, car in undervalued.head(10).iterrows():
            discount = ((car['expected_price_mean'] - car['basePrice']) / car['expected_price_mean']) * 100
            id=car["Filename"][:-5]
            link="https://www.nettiauto.com/{}".format(id)
            print(f"- {car['vehicleBrand']} {car['vehicleModel']}: {discount:.1f}% below expected. Link: {link}")
            webbrowser.open(link)