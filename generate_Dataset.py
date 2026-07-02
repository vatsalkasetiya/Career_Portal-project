import pandas as pd
import random

careers = [
    "AI Engineer",
    "Data Scientist",
    "Web Developer",
    "Cyber Security",
    "Cloud Engineer"
]

interests = [
    "AI",
    "Data Science",
    "Web",
    "Cyber",
    "Cloud"
]

rows = []

for i in range(5000):

    cgpa = round(random.uniform(5.5, 10), 2)
    python = random.randint(1,10)
    communication = random.randint(1,10)
    projects = random.randint(0,10)
    internships = random.randint(0,5)

    interest = random.choice(interests)

    if interest == "AI":
        career = "AI Engineer"
    elif interest == "Data Science":
        career = "Data Scientist"
    elif interest == "Web":
        career = "Web Developer"
    elif interest == "Cyber":
        career = "Cyber Security"
    else:
        career = "Cloud Engineer"

    rows.append([
        cgpa,
        python,
        communication,
        projects,
        internships,
        interest,
        career
    ])

df = pd.DataFrame(rows, columns=[
    "cgpa",
    "python",
    "communication",
    "projects",
    "internships",
    "interest",
    "career"
])

df.to_csv("dataset/career_dataset.csv", index=False)

print("Dataset Created Successfully")