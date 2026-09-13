"""
generate_data.py
-----------------
Synthetic college placement dataset generate karta hai — jaise ek
college placement cell ke records hote hain: academic performance,
skills, internships, aur final placement outcome.

Realistic banane ke liye, placement probability ko features ke weighted
combination + kuch randomness se derive kiya gaya hai (taaki model ko
seekhne ke liye genuine signal mile, bas noise na ho).
"""

import numpy as np
import pandas as pd
import os

np.random.seed(42)
n = 1000

df = pd.DataFrame({
    "student_id": [f"STU{1000+i}" for i in range(n)],
    "cgpa": np.round(np.random.normal(7.2, 1.0, n).clip(4.5, 10.0), 2),
    "iq_score": np.random.normal(100, 15, n).clip(70, 145).astype(int),
    "communication_skill": np.random.randint(1, 11, n),   # 1-10 rating
    "internships": np.random.poisson(1.1, n).clip(0, 5),
    "projects_completed": np.random.poisson(2.0, n).clip(0, 8),
    "coding_score": np.random.normal(65, 20, n).clip(0, 100).round(1),  # out of 100
    "backlogs": np.random.choice([0, 0, 0, 1, 1, 2], n),
    "extra_curricular": np.random.randint(0, 2, n),  # 0/1
    "aptitude_test_score": np.random.normal(60, 18, n).clip(0, 100).round(1),
})

# Underlying "true" score that drives placement probability
score = (
    0.55 * df["cgpa"]
    + 0.015 * df["iq_score"]
    + 0.35 * df["communication_skill"]
    + 0.6 * df["internships"]
    + 0.25 * df["projects_completed"]
    + 0.025 * df["coding_score"]
    - 1.1 * df["backlogs"]
    + 0.3 * df["extra_curricular"]
    + 0.02 * df["aptitude_test_score"]
)

# Normalize score to a probability via sigmoid (sharper curve = clearer signal, thoda kam noise)
score_norm = (score - score.mean()) / score.std()
prob = 1 / (1 + np.exp(-1.8 * score_norm))
df["placed"] = (np.random.rand(n) < prob).astype(int)

# --- introduce a little real-world messiness ---
# a few missing values
for col, frac in [("communication_skill", 0.02), ("internships", 0.015), ("coding_score", 0.02)]:
    idx = df.sample(frac=frac, random_state=1).index
    df.loc[idx, col] = np.nan

df.to_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "placement_data.csv"), index=False)
print(f"Dataset saved: {len(df)} rows, placement rate = {df['placed'].mean()*100:.1f}%")
