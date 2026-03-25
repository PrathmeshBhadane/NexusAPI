import pandas as pd
import numpy as np
import joblib
import os
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.tree import DecisionTreeClassifier
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import accuracy_score, r2_score, mean_squared_error
from sklearn.pipeline import Pipeline
from app.core.config import settings

SUPPORTED_MODELS = {
    "linear_regression": LinearRegression,
    "logistic_regression": LogisticRegression,
    "random_forest_classifier": RandomForestClassifier,
    "random_forest_regressor": RandomForestRegressor,
    "decision_tree": DecisionTreeClassifier,
}

def train_model(data: list[dict], target_column: str, model_type: str, model_id: str):
    if model_type not in SUPPORTED_MODELS:
        raise ValueError(f"Unsupported model type: {model_type}")

    df = pd.DataFrame(data)

    if target_column not in df.columns:
        raise ValueError(f"Target column '{target_column}' not found in data")

    X = df.drop(columns=[target_column])
    y = df[target_column]

    # encode categorical columns
    encoders = {}
    for col in X.select_dtypes(include=["object"]).columns:
        le = LabelEncoder()
        X[col] = le.fit_transform(X[col].astype(str))
        encoders[col] = le

    if y.dtype == object:
        le = LabelEncoder()
        y = le.fit_transform(y.astype(str))
        encoders[target_column] = le

    features = list(X.columns)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    model_class = SUPPORTED_MODELS[model_type]
    pipeline = Pipeline([
        ("scaler", StandardScaler()),
        ("model", model_class())
    ])

    pipeline.fit(X_train, y_train)
    y_pred = pipeline.predict(X_test)

    # calculate metrics
    metrics = {}
    accuracy = None

    if model_type in ["logistic_regression", "random_forest_classifier", "decision_tree"]:
        accuracy = float(accuracy_score(y_test, y_pred))
        metrics["accuracy"] = accuracy
    else:
        r2 = float(r2_score(y_test, y_pred))
        mse = float(mean_squared_error(y_test, y_pred))
        accuracy = r2
        metrics["r2_score"] = r2
        metrics["mse"] = mse
        metrics["rmse"] = float(np.sqrt(mse))

    # save model
    os.makedirs(settings.MODELS_DIR, exist_ok=True)
    file_path = os.path.join(settings.MODELS_DIR, f"{model_id}.pkl")
    joblib.dump({"pipeline": pipeline, "encoders": encoders, "features": features}, file_path)

    return {
        "file_path": file_path,
        "features": features,
        "accuracy": accuracy,
        "metrics": metrics
    }

def predict(model_id: str, data: list[dict]):
    file_path = os.path.join(settings.MODELS_DIR, f"{model_id}.pkl")

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Model file not found: {model_id}")

    model_data = joblib.load(file_path)
    pipeline = model_data["pipeline"]
    encoders = model_data["encoders"]
    features = model_data["features"]

    df = pd.DataFrame(data)

    for col in features:
        if col not in df.columns:
            df[col] = 0

    df = df[features]

    for col, encoder in encoders.items():
        if col in df.columns:
            df[col] = encoder.transform(df[col].astype(str))

    predictions = pipeline.predict(df)
    return predictions.tolist()