data {
  int<lower=0> N;           // number of observations
  int<lower=0> K;           // number of predictors
  matrix[N, K] X;           // predictor matrix
  vector[N] y;              // response vector
}
parameters {
  vector[K] beta;           // coefficients
  real alpha;               // intercept
  real<lower=0> sigma;      // error scale
}
model {
  // Priors
  beta ~ normal(0, 10);
  alpha ~ normal(0, 10);
  sigma ~ cauchy(0, 5);
  
  // Likelihood
  y ~ normal(alpha + X * beta, sigma);
}
generated quantities {
  vector[N] y_rep;          // posterior predictive distribution
  for (i in 1:N) {
    y_rep[i] = normal_rng(alpha + X[i] * beta, sigma);
  }
}