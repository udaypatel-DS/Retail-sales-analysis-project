"""
app.py
-------
Streamlit web app - placement prediction ko browser me interactive
form ke through use karne ke liye.

Run: streamlit run app/app.py
"""

import streamlit as st
import joblib
import pandas as pd
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + "/../src")
from recommend import generate_recommendations

MODEL_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "models")
FEATURES = [
    "cgpa", "iq_score", "communication_skill", "internships",
    "projects_completed", "coding_score", "backlogs",
    "extra_curricular", "aptitude_test_score"
]

st.set_page_config(page_title="Placement Prediction", page_icon="🎓", layout="centered")

@st.cache_resource
def load_artifacts():
    model = joblib.load(f"{MODEL_DIR}/placement_model.pkl")
    scaler = joblib.load(f"{MODEL_DIR}/scaler.pkl")
    model_name = joblib.load(f"{MODEL_DIR}/model_name.pkl")
    return model, scaler, model_name

model, scaler, model_name = load_artifacts()

st.title("🎓 Student Placement Prediction")
st.caption(f"Model in use: **{model_name}**")
st.write("Apni academic aur skill details bharo, model batayega placement chances kitne hain.")

col1, col2 = st.columns(2)
with col1:
    cgpa = st.slider("CGPA", 4.0, 10.0, 7.5, 0.1)
    iq_score = st.slider("IQ Score", 70, 145, 100)
    communication_skill = st.slider("Communication Skill (1-10)", 1, 10, 6)
    internships = st.number_input("Number of Internships", 0, 5, 1)
    projects_completed = st.number_input("Projects Completed", 0, 8, 2)

with col2:
    coding_score = st.slider("Coding Test Score (0-100)", 0, 100, 65)
    backlogs = st.number_input("Current Backlogs", 0, 5, 0)
    extra_curricular = st.selectbox("Active in Extra-Curriculars?", ["Yes", "No"])
    aptitude_test_score = st.slider("Aptitude Test Score (0-100)", 0, 100, 60)

if st.button("Predict Placement", type="primary"):
    input_data = pd.DataFrame([{
        "cgpa": cgpa,
        "iq_score": iq_score,
        "communication_skill": communication_skill,
        "internships": internships,
        "projects_completed": projects_completed,
        "coding_score": coding_score,
        "backlogs": backlogs,
        "extra_curricular": 1 if extra_curricular == "Yes" else 0,
        "aptitude_test_score": aptitude_test_score,
    }])[FEATURES]

    if model_name == "Logistic Regression":
        X_input = scaler.transform(input_data)
    else:
        X_input = input_data

    pred = model.predict(X_input)[0]
    prob = model.predict_proba(X_input)[0][1]

    st.divider()
    if pred == 1:
        st.success(f"✅ Likely to be PLACED — {prob*100:.1f}% probability")
        st.progress(float(prob))
    else:
        st.error(f"❌ Likely NOT to be placed — {prob*100:.1f}% probability of placement")
        st.progress(float(prob))

        recs = generate_recommendations(input_data.iloc[0].to_dict())
        if recs:
            st.subheader("📌 In areas par focus karo (priority order me):")
            for i, r in enumerate(recs, 1):
                with st.expander(f"{i}. {r['label']}  —  Aap: {r['student_value']:.1f} | Placed avg: {r['benchmark']:.1f}"):
                    st.write(r["advice"])
        else:
            st.info("Aap already placed students ke average ke aas-paas ho — thodi aur consistency rakho!")
