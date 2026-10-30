
import pandas as pd
import numpy as np
import joblib
import json
import os

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report
)

# 1. Dataset load karo
df = pd.read_csv("data/heart.csv")

print("Dataset loaded successfully!")
print("Dataset shape:", df.shape)

# 2. Input aur output alag karo
X = df.drop("target", axis=1)
y = df["target"]

# 3. Training aur testing data split karo
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

# 4. Data scaling
scaler = StandardScaler()

X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# 5. Random Forest model banao
model = RandomForestClassifier(
    n_estimators=100,
    random_state=42
)

# 6. Model train karo
model.fit(X_train_scaled, y_train)

# 7. Prediction karo
y_pred = model.predict(X_test_scaled)

# 8. Model evaluation
accuracy = accuracy_score(y_test, y_pred)
precision = precision_score(y_test, y_pred, zero_division=0)
recall = recall_score(y_test, y_pred, zero_division=0)
f1 = f1_score(y_test, y_pred, zero_division=0)

print("\nMODEL PERFORMANCE")
print("Accuracy:", round(accuracy * 100, 2), "%")
print("Precision:", round(precision, 2))
print("Recall:", round(recall, 2))
print("F1 Score:", round(f1, 2))

print("\nClassification Report:")
print(classification_report(y_test, y_pred))

# 9. Model aur scaler save karo
os.makedirs("model", exist_ok=True)

joblib.dump(model, "model/heart_model.pkl")
joblib.dump(scaler, "model/scaler.pkl")

# 10. Metrics save karo
metrics = {
    "accuracy": float(accuracy),
    "precision": float(precision),
    "recall": float(recall),
    "f1_score": float(f1),
    "confusion_matrix": confusion_matrix(
        y_test, y_pred
    ).tolist(),
    "feature_names": X.columns.tolist()
}

with open("model/metrics.json", "w") as file:
    json.dump(metrics, file, indent=4)

print("\nModel training completed successfully!")
print("Model saved in model/heart_model.pkl")
print("Scaler saved in model/scaler.pkl")
print("Metrics saved in model/metrics.json")
