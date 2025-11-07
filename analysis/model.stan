data {
  int<lower=0> N;
  vector[N] date;
  vector[N] mileage;
  vector[N] price;
  int<lower=0> K;
}
parameters {
  real alpha;
  vector[K] beta;
  real<lower=0> sigma;
}
model {
  price ~ normal(alpha + beta[1] * date + beta[2] * mileage + 
                beta[3] * date .* mileage + beta[4] * square(date) + 
                beta[5] * square(mileage), sigma);
}