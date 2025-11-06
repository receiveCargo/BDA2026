data {
    int<lower=0> N;
    vector[N] age;
    vector[N] mileage;
    vector[N] log_price;
}

parameters {
    real alpha;
    real beta_age;
    real beta_mileage;
    real<lower=0> sigma;
}

model {
    alpha ~ normal(10, 2);
    beta_age ~ normal(-0.1, 0.05);
    beta_mileage ~ normal(-0.0001, 0.00005);
    sigma ~ exponential(1);
    
    log_price ~ normal(alpha + beta_age * age + beta_mileage * mileage, sigma);
}

generated quantities {
    vector[N] log_price_rep;
    vector[N] log_lik;
    
    for (i in 1:N) {
        real mu = alpha + beta_age * age[i] + beta_mileage * mileage[i];
        log_price_rep[i] = normal_rng(mu, sigma);
        log_lik[i] = normal_lpdf(log_price[i] | mu, sigma);
    }
}