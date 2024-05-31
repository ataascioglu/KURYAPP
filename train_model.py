import pandas as pd
from sklearn.model_selection import train_test_split, GridSearchCV, cross_val_score
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error
import joblib

# Dataset
data = {
    'Class': list(range(51)),
    'Price_5km': [88.21, 119.37, 124.05, 138.05, 147.74, 160.61, 166.59, 175.63, 191.80, 207.37,
                  216.30, 233.97, 247.79, 256.58, 261.05, 266.34, 274.72, 288.19, 297.57, 308.97,
                  311.01, 327.60, 339.18, 350.71, 360.27, 372.81, 382.36, 391.35, 400.30, 406.78,
                  417.61, 432.35, 444.11, 455.87, 467.63, 479.39, 494.12, 505.88, 517.64, 529.40,
                  541.16, 555.90, 567.66, 579.42, 591.18, 602.94, 617.67, 629.43, 641.19, 652.95, 664.71],
    'Price_5_100km': [126.01, 159.28, 164.42, 184.42, 197.79, 216.19, 224.19, 237.10, 260.20, 282.45,
                      295.21, 318.94, 338.68, 351.24, 357.62, 362.96, 375.54, 394.79, 408.19, 424.47,
                      427.38, 449.57, 466.11, 482.58, 496.24, 514.15, 525.76, 538.60, 551.37, 560.64,
                      576.12, 595.89, 612.69, 629.49, 646.29, 663.09, 682.86, 699.66, 716.46, 733.26,
                      750.06, 769.84, 786.64, 803.44, 820.23, 837.03, 856.81, 873.61, 890.41, 907.21, 924.01]
}

df = pd.DataFrame(data)

# Split the data into features and target variables
X = df[['Class']]
y_5km = df['Price_5km']
y_5_100km = df['Price_5_100km']

# Split the data into training and testing sets
X_train, X_test, y_train_5km, y_test_5km = train_test_split(X, y_5km, test_size=0.2, random_state=42)
X_train, X_test, y_train_5_100km, y_test_5_100km = train_test_split(X, y_5_100km, test_size=0.2, random_state=42)

# Scale the features
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Train the model for <5km pricing
model_5km = RandomForestRegressor()
param_grid = {
    'n_estimators': [50, 100, 200],
    'max_depth': [None, 10, 20, 30],
    'min_samples_split': [2, 5, 10]
}
grid_search_5km = GridSearchCV(model_5km, param_grid, cv=5)
grid_search_5km.fit(X_train_scaled, y_train_5km)

# Train the model for 5-100km pricing
model_5_100km = Ridge(alpha=1.0)
model_5_100km.fit(X_train_scaled, y_train_5_100km)

# Make predictions
predictions_5km = grid_search_5km.predict(X_test_scaled)
predictions_5_100km = model_5_100km.predict(X_test_scaled)

# Calculate Mean Absolute Error
mae_5km = mean_absolute_error(y_test_5km, predictions_5km)
mae_5_100km = mean_absolute_error(y_test_5_100km, predictions_5_100km)

print(f'Mean Absolute Error for <5km: {mae_5km}')
print(f'Mean Absolute Error for 5-100km: {mae_5_100km}')

# Save the models
joblib.dump(grid_search_5km.best_estimator_, 'model_5km.pkl')
joblib.dump(model_5_100km, 'model_5_100km.pkl')

print("Models saved as 'model_5km.pkl' and 'model_5_100km.pkl'")
import matplotlib.pyplot as plt

# Plot for <5km pricing
plt.figure(figsize=(10, 6))
plt.scatter(df['Class'], df['Price_5km'], color='blue')
plt.plot(X_test, predictions_5km, color='red')
plt.title('Price vs Class for <5km')
plt.xlabel('Class')
plt.ylabel('Price')
plt.show()

# Plot for 5-100km pricing
plt.figure(figsize=(10, 6))
plt.scatter(df['Class'], df['Price_5_100km'], color='blue')
plt.plot(X_test, predictions_5_100km, color='red')
plt.title('Price vs Class for 5-100km')
plt.xlabel('Class')
plt.ylabel('Price')
plt.show()