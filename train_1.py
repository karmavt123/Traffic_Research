"""
Duration Prediction - ML Pipeline
Dataset: HCMC routing data (origin, destination, distance_m, duration_s)
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import warnings
warnings.filterwarnings("ignore")

# ── Try importing XGBoost (optional) ──────────────────────────────────────────
try:
    from xgboost import XGBRegressor
    HAS_XGB = True
except ImportError:
    HAS_XGB = False
    print("[!] XGBoost not installed. Skipping. Run: pip install xgboost")

# ══════════════════════════════════════════════════════════════════════════════
# 1. LOAD DATA
# ══════════════════════════════════════════════════════════════════════════════
CSV_PATH = "hcm_osrm_dataset.csv"   

df = pd.read_csv(CSV_PATH)
print(f"✅ Loaded {len(df):,} rows")
print(df.dtypes)
print(df.head(3))

# ══════════════════════════════════════════════════════════════════════════════
# 2. FEATURE ENGINEERING
# ══════════════════════════════════════════════════════════════════════════════
df["timestamp"] = pd.to_datetime(df["timestamp"])
df["hour"]       = df["timestamp"].dt.hour
df["dayofweek"]  = df["timestamp"].dt.dayofweek   # 0=Mon, 6=Sun
df["is_weekend"] = (df["dayofweek"] >= 5).astype(int)
df["is_rush"]    = df["hour"].isin([7, 8, 9, 17, 18, 19]).astype(int)

# Label encode origin & destination
le_origin = LabelEncoder()
le_dest   = LabelEncoder()
df["origin_enc"]      = le_origin.fit_transform(df["origin"])
df["destination_enc"] = le_dest.fit_transform(df["destination"])

# Speed proxy (avg speed = dist/time, useful as sanity check but leaks target)
# → NOT used as feature to avoid leakage

# Feature set
FEATURES = [
    "distance_m",
    "hour", "dayofweek", "is_weekend", "is_rush",
    "origin_enc", "destination_enc",
]
TARGET = "duration_s"

X = df[FEATURES]
y = df[TARGET]

print(f"\n📐 Features: {FEATURES}")
print(f"   Shape: {X.shape}")

# ══════════════════════════════════════════════════════════════════════════════
# 3. TRAIN/TEST SPLIT
# ══════════════════════════════════════════════════════════════════════════════
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)
print(f"\n🔀 Train: {len(X_train):,} | Test: {len(X_test):,}")

# ══════════════════════════════════════════════════════════════════════════════
# 4. MODEL DEFINITIONS
# ══════════════════════════════════════════════════════════════════════════════
models = {
    "Linear Regression":    LinearRegression(),
    "Ridge (α=1)":          Ridge(alpha=1.0),
    "Lasso (α=1)":          Lasso(alpha=1.0),
    "Random Forest":        RandomForestRegressor(n_estimators=200, n_jobs=-1, random_state=42),
    "Gradient Boosting":    GradientBoostingRegressor(n_estimators=200, learning_rate=0.1, random_state=42),
}

if HAS_XGB:
    models["XGBoost"] = XGBRegressor(
        n_estimators=300, learning_rate=0.05,
        max_depth=6, subsample=0.8,
        colsample_bytree=0.8, random_state=42,
        verbosity=0
    )

# ══════════════════════════════════════════════════════════════════════════════
# 5. TRAIN & EVALUATE
# ══════════════════════════════════════════════════════════════════════════════
results = []

print("\n" + "="*65)
print(f"{'Model':<25} {'MAE':>8} {'RMSE':>8} {'R²':>7} {'CV-R²':>10}")
print("="*65)

for name, model in models.items():
    model.fit(X_train, y_train)
    preds = model.predict(X_test)

    mae  = mean_absolute_error(y_test, preds)
    rmse = np.sqrt(mean_squared_error(y_test, preds))
    r2   = r2_score(y_test, preds)

    # 5-fold CV on full data
    cv_scores = cross_val_score(model, X, y, cv=5, scoring="r2", n_jobs=-1)
    cv_r2 = cv_scores.mean()

    results.append({"Model": name, "MAE": mae, "RMSE": rmse, "R²": r2, "CV-R²": cv_r2})
    print(f"{name:<25} {mae:>8.1f} {rmse:>8.1f} {r2:>7.4f} {cv_r2:>10.4f}")

print("="*65)

# ── Best model ────────────────────────────────────────────────────────────────
results_df = pd.DataFrame(results).sort_values("R²", ascending=False)
best = results_df.iloc[0]
print(f"\n🏆 Best: {best['Model']}  |  R²={best['R²']:.4f}  |  MAE={best['MAE']:.1f}s")

# ══════════════════════════════════════════════════════════════════════════════
# 6. FEATURE IMPORTANCE (tree-based models)
# ══════════════════════════════════════════════════════════════════════════════
print("\n📊 Feature Importance (Random Forest):")
rf = models["Random Forest"]
importances = pd.Series(rf.feature_importances_, index=FEATURES).sort_values(ascending=False)
for feat, val in importances.items():
    bar = "█" * int(val * 50)
    print(f"  {feat:<20} {val:.4f}  {bar}")

# ══════════════════════════════════════════════════════════════════════════════
# 7. QUICK SANITY CHECK — predict a single trip
# ══════════════════════════════════════════════════════════════════════════════
print("\n🧪 Sanity check — Ben Thanh → Thu Duc, 12775m, rush hour:")
sample = pd.DataFrame([{
    "distance_m":       12775,
    "hour":             8,         # rush hour sáng
    "dayofweek":        1,         # Tuesday
    "is_weekend":       0,
    "is_rush":          1,
    "origin_enc":       le_origin.transform(["Ben Thanh Market"])[0]
                        if "Ben Thanh Market" in le_origin.classes_ else 0,
    "destination_enc":  le_dest.transform(["Thu Duc"])[0]
                        if "Thu Duc" in le_dest.classes_ else 0,
}])

best_model = models[best["Model"]]
pred_s = best_model.predict(sample)[0]
print(f"  → Predicted duration: {pred_s:.0f}s  ({pred_s/60:.1f} min)")
print(f"     (Actual in dataset: 850.4s = 14.2 min)")