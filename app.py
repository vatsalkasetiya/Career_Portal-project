import joblib
import numpy as np
import joblib
import pandas as pd
from werkzeug.utils import secure_filename
import os

model = joblib.load("models/career_model.pkl")
interest_encoder = joblib.load("models/interest_encoder.pkl")
career_encoder = joblib.load("models/career_encoder.pkl")
from flask import Flask, render_template, request, redirect, flash, session
from database.db import get_connection
from flask_bcrypt import Bcrypt

app = Flask(__name__)
app.secret_key = "career_portal_secret_123"

bcrypt = Bcrypt(app)

# Database Connection Test
try:
    connection = get_connection()
    print("✅ Database Connected Successfully")
    connection.close()
except Exception as e:
    print("❌ Database Error:", e)


@app.route("/")
def home():
    return render_template("home.html")


# ---------------- LOGIN ----------------

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute(
            "SELECT * FROM users WHERE email=%s",
            (email,)
        )

        user = cursor.fetchone()

        cursor.close()
        connection.close()

        if user and bcrypt.check_password_hash(user["password"], password):

            session["user_id"] = user["id"]
            session["user_name"] = user["full_name"]

            flash("Login Successful!")
            return redirect("/dashboard")

        flash("Invalid Email or Password")
        return redirect("/login")

    return render_template("login.html")


# ---------------- SIGNUP ----------------

@app.route("/signup", methods=["GET", "POST"])
def signup():

    if request.method == "POST":

        full_name = request.form["full_name"]
        email = request.form["email"]
        phone = request.form["phone"]

        password = request.form["password"]
        confirm_password = request.form["confirm_password"]

        if password != confirm_password:
            flash("Passwords do not match!")
            return redirect("/signup")

        hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")

        try:

            connection = get_connection()
            cursor = connection.cursor()

            cursor.execute(
                "SELECT * FROM users WHERE email=%s",
                (email,)
            )

            user = cursor.fetchone()

            if user:
                flash("Email already exists!")
                cursor.close()
                connection.close()
                return redirect("/signup")

            cursor.execute(
                """
                INSERT INTO users(full_name,email,phone,password)
                VALUES(%s,%s,%s,%s)
                """,
                (full_name, email, phone, hashed_password)
            )

            connection.commit()

            print("Rows affected:", cursor.rowcount)
            print("✅ User Inserted Successfully")

            cursor.close()
            connection.close()

            flash("Account Created Successfully!")

            return redirect("/login")

        except Exception as e:
            print("❌ Database Error:", e)
            flash(str(e))
            return redirect("/signup")

    return render_template("signup.html")


# ---------------- DASHBOARD ----------------

@app.route("/dashboard")
def dashboard():

    if "user_id" not in session:
        return redirect("/login")

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute(
        "SELECT COUNT(*) AS total FROM prediction_history WHERE user_id=%s",
        (session["user_id"],)
    )
    total_predictions = cursor.fetchone()["total"]

    cursor.execute(
        "SELECT COUNT(*) AS total FROM resumes WHERE user_id=%s",
        (session["user_id"],)
    )
    total_resumes = cursor.fetchone()["total"]

    cursor.close()
    connection.close()

    return render_template(
        "dashboard.html",
        user_name=session["user_name"],
        total_predictions=total_predictions,
        total_resumes=total_resumes
    )


# ---------------- LOGOUT ----------------

@app.route("/logout")
def logout():

    session.clear()

    return redirect("/login")


@app.route("/career_prediction", methods=["GET", "POST"])
def career_prediction():

    if "user_id" not in session:
        return redirect("/login")

    if request.method == "POST":

        cgpa = float(request.form["cgpa"])
        python_skill = int(request.form["python"])
        communication = int(request.form["communication"])
        projects = int(request.form["projects"])
        internships = int(request.form["internships"])

        interest = interest_encoder.transform(
            [request.form["interest"]]
        )[0]

        data = pd.DataFrame([[
            cgpa,
            python_skill,
            communication,
            projects,
            internships,
            interest
        ]], columns=[
            "cgpa",
            "python",
            "communication",
            "projects",
            "internships",
            "interest"
        ])

        prediction = model.predict(data)

        career = career_encoder.inverse_transform(prediction)[0]

        # Save Prediction
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute(
            """
            INSERT INTO prediction_history(user_id, predicted_career)
            VALUES(%s,%s)
            """,
            (session["user_id"], career)
        )

        connection.commit()

        cursor.close()
        connection.close()

        return render_template(
            "career_prediction.html",
            result=career
        )

    return render_template("career_prediction.html")

@app.route("/history")
def history():

    if "user_id" not in session:
        return redirect("/login")

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute(
        "SELECT * FROM prediction_history WHERE user_id=%s ORDER BY id DESC",
        (session["user_id"],)
    )

    history = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template("history.html", history=history)

app.config["UPLOAD_FOLDER"] = "uploads"


@app.route("/resume", methods=["GET", "POST"])
def resume():

    if "user_id" not in session:
        return redirect("/login")

    if request.method == "POST":

        if "resume" not in request.files:
            flash("Please Select a File")
            return redirect("/resume")

        file = request.files["resume"]

        if file.filename == "":
            flash("Please Select a File")
            return redirect("/resume")

        filename = secure_filename(file.filename)

        upload_path = os.path.join(
            app.config["UPLOAD_FOLDER"],
            filename
        )

        file.save(upload_path)

        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute(
            """
            INSERT INTO resumes(user_id,file_name)
            VALUES(%s,%s)
            """,
            (session["user_id"], filename)
        )

        connection.commit()

        cursor.close()
        connection.close()

        return render_template(
            "resume.html",
            message="✅ Resume Uploaded Successfully!"
        )

    return render_template("resume.html")

@app.route("/profile")
def profile():

    if "user_id" not in session:
        return redirect("/login")

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute(
        "SELECT * FROM users WHERE id=%s",
        (session["user_id"],)
    )

    user = cursor.fetchone()

    cursor.close()
    connection.close()

    return render_template("profile.html", user=user)

if __name__ == "__main__":
    app.run(debug=True)

