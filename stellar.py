# self_ml_modify.py
# run this in Colab with: !python self_ml_modify.py

import random
import pickle
import re
from sklearn.linear_model import SGDRegressor
from sklearn.datasets import make_regression

# === hyperparameter ===
# learning_rate: 0.01

# Load or generate data
X, y = make_regression(n_samples=100, n_features=1, noise=10)

# Extract learning rate from this file
import re
with open(__file__, 'r') as f:
    content = f.read()
lr = float(re.search(r'learning_rate: ([0-9.]+)', content).group(1))

# Train model
model = SGDRegressor(eta0=lr, learning_rate='constant', max_iter=1000)
model.fit(X, y)
print(f"Trained with learning_rate = {lr}, score = {model.score(X, y)}")

# Modify hyperparameter for next run
new_lr = round(random.uniform(0.001, 0.1), 4)
new_content = re.sub(r'(learning_rate: )([0-9.]+)', f'\\1{new_lr}', content)

# Save modified script
with open(__file__, 'w') as f:
    f.write(new_content)
print(f"Updated learning_rate to {new_lr} for next run.")
