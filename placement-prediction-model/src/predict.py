"""
predict.py
-----------
Trained model use karke ek naye student ke placement chances predict
karta hai. Command line se chalao aur apne values enter karo.

Usage:
    python src/predict.py
"""

import joblib
import numpy as np
import pandas as pd
import os
from recommend import generate_recommendations

MODEL_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "models")

FEATURES = [
    "cgpa", "iq_score", "communication_skill", "internships",
    "projects_completed", "coding_score", "backlogs",
    "extra_curricular", "aptitude_test_score"
]


def load_artifacts():
    model = joblib.load(f"{MODEL_DIR}/placement_model.pkl")
    scaler = joblib.load(f"{MODEL_DIR}/scaler.pkl")
    model_name = joblib.load(f"{MODEL_DIR}/model_name.pkl")
    return model, scaler, model_name


def predict_single(model, scaler, model_name, student_data: dict):
    """student_data: dict with keys matching FEATURES"""
    X = pd.DataFrame([student_data])[FEATURES]

    if model_name == "Logistic Regression":
        X_input = scaler.transform(X)
    else:
        X_input = X

    pred = model.predict(X_input)[0]
    prob = model.predict_proba(X_input)[0][1]
    return pred, prob


def get_user_input():
    print("\nApni details enter karo:\n")
    data = {
        "cgpa": float(input("CGPA (0-10): ")),
        "iq_score": float(input("IQ Score (approx 70-145): ")),
        "communication_skill": float(input("Communication Skill rating (1-10): ")),
        "internships": float(input("Number of internships done: ")),
        "projects_completed": float(input("Number of projects completed: ")),
        "coding_score": float(input("Coding test score (0-100): ")),
        "backlogs": float(input("Number of current backlogs: ")),
        "extra_curricular": float(input("Active in extra-curriculars? (1=Yes, 0=No): ")),
        "aptitude_test_score": float(input("Aptitude test score (0-100): ")),
    }
    return data


if __name__ == "__main__":
    model, scaler, model_name = load_artifacts()
    print(f"Loaded model: {model_name}")

    student_data = get_user_input()
    pred, prob = predict_single(model, scaler, model_name, student_data)

    print("\n" + "=" * 40)
    if pred == 1:
        print(f"Prediction: LIKELY TO BE PLACED ✅")
        print(f"Placement Probability: {prob*100:.1f}%")
        print("=" * 40)
    else:
        print(f"Prediction: LIKELY NOT TO BE PLACED ❌")
        print(f"Placement Probability: {prob*100:.1f}%")
        print("=" * 40)

        recs = generate_recommendations(student_data)
        if recs:
            print("\n📌 Improve karne ke liye sabse important areas (priority order me):\n")
            for i, r in enumerate(recs, 1):
                print(f"{i}. {r['label']}")
                print(f"   Aapka value: {r['student_value']} | Placed students ka average: {r['benchmark']:.1f}")
                print(f"   Suggestion: {r['advice']}\n")
        else:
            print("\nAap already placed students ke average ke aas-paas ho — thoda aur consistency rakho!")
