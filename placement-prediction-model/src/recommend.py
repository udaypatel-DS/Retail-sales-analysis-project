"""
recommend.py
-------------
Jab prediction "Not Placed" aaye, ye module student ke weak areas
identify karta hai — placed students ke typical (median) values se
comparison karke — aur unhe priority order me actionable advice deta hai.

Logic:
1. Student ki har value ko placed-students-median se compare karo
2. Jahan gap negative hai (student peeche hai), use ek "improvement area" maano
3. Un areas ko feature importance ke hisaab se sort karo (sabse impactful pehle)
4. Top 3-4 ke liye human-readable, actionable suggestion do
"""

import joblib
import os

MODEL_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "models")

# Har feature ke liye: higher_is_better (ya nahi) aur ek advice template
FEATURE_META = {
    "cgpa": {
        "higher_is_better": True,
        "label": "CGPA",
        "advice": "Aapka CGPA placed students ke average ({benchmark:.2f}) se kam hai. "
                  "Agle semester(s) me focus karo — regular study schedule banao, "
                  "weak subjects pehle target karo, aur professors se doubt-clearing sessions lo.",
    },
    "iq_score": {
        "higher_is_better": True,
        "label": "IQ / Logical Reasoning",
        "advice": "Logical reasoning aur aptitude thoda weak lag raha hai. "
                  "Daily 20-30 min puzzle/reasoning practice (Indiabix, PrepInsta jaise platforms) "
                  "kaafi help karega placement tests ke liye.",
    },
    "communication_skill": {
        "higher_is_better": True,
        "label": "Communication Skills",
        "advice": "Ye sabse important factor hai placement me — aapki communication skill average se kam hai. "
                  "Mock interviews do (Placement cell ya dost ke saath), English speaking practice karo, "
                  "aur group discussions me active participate karo.",
    },
    "internships": {
        "higher_is_better": True,
        "label": "Internship Experience",
        "advice": "Aapke paas internships kam hain. LinkedIn, Internshala jaise platforms par apply karo — "
                  "chahe unpaid ho, real-world experience aur resume dono strong hote hain.",
    },
    "projects_completed": {
        "higher_is_better": True,
        "label": "Projects",
        "advice": "Zyada hands-on projects banao apne domain me (Data Science/Web Dev/etc.) aur "
                  "unhe GitHub par push karo — recruiters isse practical skill dekhte hain.",
    },
    "coding_score": {
        "higher_is_better": True,
        "label": "Coding Skills",
        "advice": "Coding test score average se kam hai. LeetCode/HackerRank par daily 2-3 problems solve karo, "
                  "DSA (Data Structures & Algorithms) par strong focus rakho — ye almost har company test karti hai.",
    },
    "backlogs": {
        "higher_is_better": False,
        "label": "Backlogs",
        "advice": "Aapke active backlogs placement chances kam kar rahe hain — kayi companies backlog-free "
                  "candidates hi shortlist karti hain. In backlogs ko jald clear karne ko priority do.",
    },
    "extra_curricular": {
        "higher_is_better": True,
        "label": "Extra-Curricular Involvement",
        "advice": "Extra-curricular activities me involvement badhao (clubs, hackathons, volunteering) — "
                  "ye leadership aur teamwork dikhata hai jo interviews me kaam aata hai.",
    },
    "aptitude_test_score": {
        "higher_is_better": True,
        "label": "Aptitude Test Score",
        "advice": "Aptitude score improve karna hoga — quantitative aptitude aur verbal ability ki "
                  "daily practice karo, especially placement-specific mock tests.",
    },
}


def load_recommendation_data():
    medians = joblib.load(f"{MODEL_DIR}/placed_medians.pkl")
    importances = joblib.load(f"{MODEL_DIR}/feature_importance.pkl")
    return medians, importances


def generate_recommendations(student_data: dict, top_n: int = 4):
    """
    student_data: dict jisme student ki actual values hain (FEATURES ke keys ke saath)
    Returns: list of dicts, har ek me 'label', 'advice', 'gap_severity'
    """
    medians, importances = load_recommendation_data()

    gaps = []
    for feature, meta in FEATURE_META.items():
        student_val = student_data.get(feature)
        benchmark = medians.get(feature)
        if student_val is None or benchmark is None:
            continue

        higher_is_better = meta["higher_is_better"]
        if higher_is_better:
            gap = benchmark - student_val   # positive = student is behind
        else:
            gap = student_val - benchmark   # positive = student has more than they should (bad)

        if gap > 0:  # student is behind on this feature
            # severity score = gap size (normalized-ish) * feature importance
            severity = gap * importances.get(feature, 0.1)
            gaps.append({
                "feature": feature,
                "label": meta["label"],
                "advice": meta["advice"].format(benchmark=benchmark),
                "student_value": student_val,
                "benchmark": benchmark,
                "severity": severity,
            })

    gaps.sort(key=lambda x: x["severity"], reverse=True)
    return gaps[:top_n]


if __name__ == "__main__":
    # Quick manual test
    sample_student = {
        "cgpa": 6.2, "iq_score": 95, "communication_skill": 4,
        "internships": 0, "projects_completed": 1, "coding_score": 40,
        "backlogs": 2, "extra_curricular": 0, "aptitude_test_score": 45,
    }
    recs = generate_recommendations(sample_student)
    print("\nTop improvement areas:\n")
    for i, r in enumerate(recs, 1):
        print(f"{i}. {r['label']} (You: {r['student_value']}, Placed avg: {r['benchmark']:.1f})")
        print(f"   -> {r['advice']}\n")
