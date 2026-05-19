import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error

import joblib

# =========================
# LOAD DATA
# =========================

df = pd.read_csv("hcm_osrm_dataset.csv")

# =========================
# ENCODE TEXT
# =========================

origin_encoder = LabelEncoder()
destination_encoder = LabelEncoder()

df["origin"] = origin_encoder.fit_transform(df["origin"])
df["destination"] = destination_encoder.fit_transform(df["destination"])

# =========================
# FEATURES + LABEL
# =========================

X = df[[
    "origin",
    "destination",
    "distance_m"
]]

y = df["duration_s"]

# =========================
# TRAIN TEST SPLIT
# =========================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42
)

# =========================
# MODEL
# =========================

model = RandomForestRegressor(
    n_estimators=100,
    random_state=42
)

print("TRAINING...")

model.fit(X_train, y_train)

# =========================
# EVALUATE
# =========================

predictions = model.predict(X_test)

mae = mean_absolute_error(y_test, predictions)

print("\nMAE:", mae, "seconds")

# =========================
# SAVE MODEL
# =========================

joblib.dump(model, "traffic_regression.pkl")

print("\nMODEL SAVED")