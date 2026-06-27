from flask import Flask, render_template, request, redirect, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from database.db import get_db, create_tables

app = Flask(__name__)
app.secret_key = "jobhouse_secret_key"

# Create database tables
create_tables()

# Home Page
@app.route("/")
def home():
    return render_template("index.html")


# Login Page
@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        conn = get_db()

        user = conn.execute(
            "SELECT * FROM users WHERE email=?",
            (email,)
        ).fetchone()

        conn.close()

        if user is None:

            flash("Email not found!", "danger")
            return redirect("/login")

        if not check_password_hash(user["password"], password):

            flash("Incorrect password!", "danger")
            return redirect("/login")

        session["user_id"] = user["id"]
        session["full_name"] = user["full_name"]
        session["role"] = user["role"]

        flash("Login Successful!", "success")

        return redirect("/dashboard")

    return render_template("login.html")


# Register Page
@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        full_name = request.form["full_name"]
        email = request.form["email"]
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]
        role = request.form["role"]

        if password != confirm_password:

            flash("Passwords do not match!", "danger")
            return redirect("/register")

        conn = get_db()

        user = conn.execute(
            "SELECT * FROM users WHERE email=?",
            (email,)
        ).fetchone()

        if user:

            flash("Email already registered!", "warning")
            conn.close()
            return redirect("/register")

        hashed_password = generate_password_hash(password)

        conn.execute(
            """
            INSERT INTO users
            (full_name,email,password,role)
            VALUES (?,?,?,?)
            """,
            (
                full_name,
                email,
                hashed_password,
                role
            )
        )

        conn.commit()
        conn.close()

        flash("Registration Successful!", "success")

        return redirect("/login")

    return render_template("register.html")

# Dashboard
@app.route("/dashboard")
def dashboard():

    if "user_id" not in session:

        return redirect("/login")

    return render_template(
        "dashboard.html",
        name=session["full_name"],
        role=session["role"]
    )

# Post Job

@app.route("/post-job", methods=["GET", "POST"])
def post_job():

    if "user_id" not in session:

        return redirect("/login")

    if request.method == "POST":

        company_name = request.form["company_name"]
        job_title = request.form["job_title"]
        location = request.form["location"]
        job_type = request.form["job_type"]
        salary = request.form["salary"]
        description = request.form["description"]

        conn = get_db()

        conn.execute(
            """
            INSERT INTO jobs
            (
                company_name,
                job_title,
                location,
                job_type,
                salary,
                description,
                posted_by
            )
            VALUES(?,?,?,?,?,?,?)
            """,
            (
                company_name,
                job_title,
                location,
                job_type,
                salary,
                description,
                session["user_id"]
            )
        )

        conn.commit()
        conn.close()

        flash("Job Posted Successfully!", "success")

        return redirect("/post-job")

    return render_template("post_job.html")
if __name__ == "__main__":
    app.run(debug=True)