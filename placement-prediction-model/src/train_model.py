"""
train_model.py
---------------
Placement dataset load karta hai, missing values handle karta hai,
do models train karta hai (Logistic Regression aur Random Forest),
dono ko evaluate karta hai, aur jo behtar perform kare use models/
folder me save kar deta hai future predictions ke liye.
"""

import pandas as pd
import numpy as np
import joblib
import os
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, roc_curve, roc_auc_score, classification_report
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "..", "data", "placement_data.csv")
MODEL_DIR = os.path.join(BASE_DIR, "..", "models")
VISUALS_DIR = os.path.join(BASE_DIR, "..", "visuals")

FEATURES = [
    "cgpa", "iq_score", "communication_skill", "internships",
    "projects_completed", "coding_score", "backlogs",
    "extra_curricular", "aptitude_test_score"
]
TARGET = "placed"


def load_and_prepare():
    df = pd.read_csv(DATA_PATH)
    # missing values ko column median se fill karte hain
    for col in FEATURES:
        if df[col].isna().any():
            df[col] = df[col].fillna(df[col].median())
    return df


def train_and_evaluate(df):
    X = df[FEATURES]
    y = df[TARGET]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    models = {
        "Logistic Regression": LogisticRegression(max_iter=1000, random_state=42),
        "Random Forest": RandomForestClassifier(n_estimators=200, max_depth=6, random_state=42),
    }

    results = {}
    for name, model in models.items():
        if name == "Logistic Regression":
            model.fit(X_train_scaled, y_train)
            preds = model.predict(X_test_scaled)
            probs = model.predict_proba(X_test_scaled)[:, 1]
        else:
            model.fit(X_train, y_train)
            preds = model.predict(X_test)
            probs = model.predict_proba(X_test)[:, 1]

        acc = accuracy_score(y_test, preds)
        prec = precision_score(y_test, preds)
        rec = recall_score(y_test, preds)
        f1 = f1_score(y_test, preds)
        auc = roc_auc_score(y_test, probs)

        results[name] = {
            "model": model, "accuracy": acc, "precision": prec,
            "recall": rec, "f1": f1, "auc": auc,
            "preds": preds, "probs": probs
        }

        print(f"\n--- {name} ---")
        print(f"Accuracy : {acc:.3f}")
        print(f"Precision: {prec:.3f}")
        print(f"Recall   : {rec:.3f}")
        print(f"F1 Score : {f1:.3f}")
        print(f"ROC AUC  : {auc:.3f}")
        print(classification_report(y_test, preds, target_names=["Not Placed", "Placed"]))

    # Best model chuno (F1 score ke basis par)
    best_name = max(results, key=lambda k: results[k]["f1"])
    best = results[best_name]
    print(f"\n>>> Best model: {best_name} (F1 = {best['f1']:.3f})")

    # Confusion matrix plot
    fig, ax = plt.subplots(figsize=(5, 4))
    cm = confusion_matrix(y_test, best["preds"])
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues",
                xticklabels=["Not Placed", "Placed"],
                yticklabels=["Not Placed", "Placed"], ax=ax)
    ax.set_title(f"Confusion Matrix - {best_name}")
    ax.set_xlabel("Predicted")
    ax.set_ylabel("Actual")
    plt.tight_layout()
    fig.savefig(f"{VISUALS_DIR}/confusion_matrix.png", dpi=150)
    plt.close(fig)

    # ROC curve plot (both models)
    fig, ax = plt.subplots(figsize=(6, 5))
    for name, res in results.items():
        fpr, tpr, _ = roc_curve(y_test, res["probs"])
        ax.plot(fpr, tpr, label=f"{name} (AUC={res['auc']:.2f})")
    ax.plot([0, 1], [0, 1], "k--", alpha=0.4)
    ax.set_title("ROC Curve Comparison")
    ax.set_xlabel("False Positive Rate")
    ax.set_ylabel("True Positive Rate")
    ax.legend()
    plt.tight_layout()
    fig.savefig(f"{VISUALS_DIR}/roc_curve.png", dpi=150)
    plt.close(fig)

    # Feature importance (Random Forest se, chahe woh best ho ya na ho — interpretability ke liye)
    rf_model = results["Random Forest"]["model"]
    importances = pd.Series(rf_model.feature_importances_, index=FEATURES).sort_values()
    fig, ax = plt.subplots(figsize=(8, 5))
    importances.plot(kind="barh", ax=ax, color="#2E86AB")
    ax.set_title("Feature Importance (Random Forest)")
    ax.set_xlabel("Importance")
    plt.tight_layout()
    fig.savefig(f"{VISUALS_DIR}/feature_importance.png", dpi=150)
    plt.close(fig)

    # Best model + scaler save karo
    joblib.dump(best["model"], f"{MODEL_DIR}/placement_model.pkl")
    joblib.dump(scaler, f"{MODEL_DIR}/scaler.pkl")
    joblib.dump(best_name, f"{MODEL_DIR}/model_name.pkl")

    # --- Recommendation engine ke liye stats save karo ---
    # Placed students ke har feature ka median nikal ke rakhte hain,
    # taaki naye student ka comparison ho sake aur gaps dikhaye ja sakein.
    placed_df = df[df[TARGET] == 1]
    placed_medians = placed_df[FEATURES].median().to_dict()

    # Feature importance (Random Forest se) — recommendations ko priority order dene ke liye
    importance_dict = pd.Series(rf_model.feature_importances_, index=FEATURES).to_dict()

    joblib.dump(placed_medians, f"{MODEL_DIR}/placed_medians.pkl")
    joblib.dump(importance_dict, f"{MODEL_DIR}/feature_importance.pkl")

    print(f"\nSaved best model ({best_name}) to {MODEL_DIR}/placement_model.pkl")
    print(f"Saved placed-student benchmarks for recommendation engine")
    print(f"Charts saved to {VISUALS_DIR}/")

    return results, best_name


if __name__ == "__main__":
    df = load_and_prepare()
    train_and_evaluate(df)
