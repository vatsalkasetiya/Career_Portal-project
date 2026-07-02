import pandas as pd
import joblib

from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier

df = pd.read_csv("dataset/career_dataset.csv")

interest_encoder = LabelEncoder()
career_encoder = LabelEncoder()

df["interest"] = interest_encoder.fit_transform(df["interest"])
df["career"] = career_encoder.fit_transform(df["career"])

X = df.drop("career", axis=1)
y = df["career"]

model = RandomForestClassifier(n_estimators=200, random_state=42)

model.fit(X, y)

joblib.dump(model, "models/career_model.pkl")
joblib.dump(interest_encoder, "models/interest_encoder.pkl")
joblib.dump(career_encoder, "models/career_encoder.pkl")

print("Model Trained Successfully")