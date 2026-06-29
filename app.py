from flask import Flask, render_template, request, redirect, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from database.db import get_db, create_tables
import pdfplumber
import re
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "jobhouse_secret_key"

UPLOAD_FOLDER = "static/uploads/resumes"

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

PHOTO_FOLDER = "static/uploads/photos"

app.config["PHOTO_FOLDER"] = PHOTO_FOLDER

# Create database tables
create_tables()

def calculate_ats_score(resume_path):
    
    score = 0
    extracted_text = ""

    try:

        with pdfplumber.open(resume_path) as pdf:

            for page in pdf.pages:

                text = page.extract_text()

                if text:
                    extracted_text += text.lower()

    except:

        return 0, []

    keywords = {

        "Programming Languages": [
            "python", "java", "c", "c++", "c#", "javascript",
            "typescript", "sql", "kotlin", "go", "rust", "php"
        ],

        "Frontend": [
            "html", "html5", "css", "css3",
            "bootstrap", "tailwind css",
            "react", "angular", "vue", "vue.js",
            "responsive web design",
            "ajax", "json", "xml"
        ],

        "Backend": [
            "node.js", "express", "express.js",
            "flask", "django",
            "spring boot",
            "rest api",
            "restful services"
        ],

        "Database": [
            "mysql",
            "postgresql",
            "sqlite",
            "mongodb",
            "oracle",
            "sql server",
            "firebase",
            "redis",
            "database design",
            "database management",
            "database optimization",
            "crud operations"
        ],

        "Computer Science": [
            "data structures",
            "algorithms",
            "object oriented programming",
            "oop",
            "dbms",
            "operating systems",
            "computer networks",
            "software engineering",
            "design patterns",
            "time complexity",
            "space complexity",
            "problem solving"
        ],

        "Version Control": [
            "git",
            "github",
            "gitlab",
            "bitbucket",
            "branching",
            "merge",
            "pull request"
        ],

        "Development Tools": [
            "visual studio code",
            "vscode",
            "intellij idea",
            "eclipse",
            "pycharm",
            "netbeans",
            "postman",
            "maven",
            "gradle",
            "linux",
            "windows"
        ],

        "Cloud": [
            "aws",
            "amazon web services",
            "microsoft azure",
            "azure",
            "google cloud",
            "google cloud platform",
            "gcp",
            "cloud computing"
        ],

        "Testing": [
            "junit",
            "pytest",
            "unit testing",
            "integration testing",
            "debugging",
            "testing",
            "quality assurance"
        ],

        "DevOps": [
            "docker",
            "kubernetes",
            "ci/cd",
            "github actions",
            "jenkins"
        ],

        "AI / Machine Learning": [
            "machine learning",
            "deep learning",
            "artificial intelligence",
            "tensorflow",
            "pytorch",
            "scikit-learn",
            "pandas",
            "numpy",
            "matplotlib",
            "opencv"
        ],

        "Cyber Security": [
            "cybersecurity",
            "network security",
            "ethical hacking",
            "encryption",
            "authentication",
            "authorization",
            "owasp"
        ],

        "Mobile Development": [
            "android development",
            "flutter",
            "react native",
            "java android"
        ],

        "Soft Skills": [
            "communication",
            "leadership",
            "critical thinking",
            "analytical thinking",
            "collaboration",
            "adaptability",
            "teamwork",
            "time management",
            "decision making"
        ],

        "Resume Sections": [
            "summary",
            "objective",
            "skills",
            "education",
            "experience",
            "projects",
            "internship",
            "certifications",
            "achievements",
            "languages",
            "hobbies"
        ],

        "Action Verbs": [
            "developed",
            "designed",
            "implemented",
            "built",
            "created",
            "engineered",
            "optimized",
            "automated",
            "integrated",
            "configured",
            "deployed",
            "maintained",
            "enhanced",
            "improved",
            "collaborated",
            "resolved",
            "debugged",
            "tested",
            "analyzed",
            "managed",
            "documented",
            "delivered",
            "executed"
        ],

        "ATS Project Keywords": [
            "login system",
            "authentication",
            "authorization",
            "crud",
            "dashboard",
            "admin panel",
            "search",
            "filtering",
            "role based access control",
            "user management",
            "session management",
            "file upload",
            "database integration",
            "api integration",
            "input validation",
            "error handling",
            "performance optimization"
        ],

        "Quantification": [
            "reduced",
            "improved",
            "increased",
            "optimized",
            "enhanced",
            "accelerated",
            "automated",
            "managed",
            "processed",
            "generated",
            "achieved",
            "delivered",
            "supported",
            "maintained"
        ],

        "Certifications": [
            "hackerrank",
            "nptel",
            "cisco",
            "oracle",
            "aws academy",
            "google cloud",
            "microsoft learn",
            "coursera",
            "udemy",
            "infosys springboard"
        ],

        "Job Roles": [
            "software engineer",
            "software developer",
            "java developer",
            "python developer",
            "backend developer",
            "frontend developer",
            "full stack developer",
            "web developer",
            "application developer",
            "associate software engineer",
            "graduate engineer trainee",
            "get",
            "sde",
            "sde-1",
            "intern"
        ]
    }
    weights = {

    "Programming Languages": 20,
    "Frontend": 10,
    "Backend": 15,
    "Database": 10,
    "Computer Science": 15,
    "Version Control": 5,
    "Development Tools": 5,
    "Cloud": 5,
    "Testing": 5,
    "DevOps": 5,
    "AI / Machine Learning": 10,
    "Cyber Security": 5,
    "Mobile Development": 5,
    "Soft Skills": 5,
    "Resume Sections": 5,
    "Action Verbs": 10,
    "ATS Project Keywords": 10,
    "Quantification": 5,
    "Certifications": 5,
    "Job Roles": 5

}


    found = {}
    score = 0

    for category, words in keywords.items():

        found[category] = []

        matched = 0

        for word in words:

            if word.lower() in extracted_text:

                found[category].append(word)
                matched += 1

        if len(words) > 0:

            category_score = (matched / len(words)) * weights[category]

            score += category_score

    score = round(score)

    if score > 100:
        score = 100

    all_found = []

    for values in found.values():
        all_found.extend(values)

    return score, all_found

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

    if session["role"] != "Employer":
            flash("Access Denied!", "danger")
            return redirect("/dashboard")

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
# Find Jobs

@app.route("/find-jobs")
def find_jobs():

    if "user_id" not in session:

        return redirect("/login")
    if session["role"] != "Job Seeker":
        flash("Access Denied!", "danger")
        return redirect("/dashboard")

    conn = get_db()

    jobs = conn.execute("""
SELECT
    jobs.*,
    applications.id AS applied

FROM jobs

LEFT JOIN applications
ON jobs.id = applications.job_id
AND applications.user_id = ?

ORDER BY jobs.created_at DESC
""", (session["user_id"],)).fetchall()

    conn.close()

    return render_template(

        "find_jobs.html",

        jobs=jobs

    )
   # Apply Job

@app.route("/apply-job/<int:job_id>")
def apply_job(job_id):
    

    if "user_id" not in session:
        return redirect("/login")
    
    if session["role"] != "Job Seeker":
        flash("Access Denied!", "danger")
        return redirect("/dashboard")
    

    conn = get_db()

    already_applied = conn.execute(
        """
        SELECT *
        FROM applications
        WHERE user_id=? AND job_id=?
        """,
        (
            session["user_id"],
            job_id
        )
    ).fetchone()

    if already_applied:

        flash("You have already applied for this job!", "warning")

        conn.close()

        return redirect("/find-jobs")

    conn.execute(
        """
        INSERT INTO applications(user_id,job_id)
        VALUES(?,?)
        """,
        (
            session["user_id"],
            job_id
        )
    )

    conn.commit()

    conn.close()

    flash("Application Submitted Successfully!", "success")

    return redirect("/find-jobs")
    # Applicants

@app.route("/applicants")
def applicants():

    if "user_id" not in session:
        return redirect("/login")
    
    if session["role"] != "Employer":
        flash("Access Denied!", "danger")
        return redirect("/dashboard")

    conn = get_db()

    applicants = conn.execute("""

        SELECT

            users.full_name,
            users.email,
            jobs.job_title,
            applications.applied_at

        FROM applications

        JOIN users
        ON applications.user_id = users.id

        JOIN jobs
        ON applications.job_id = jobs.id

        WHERE jobs.posted_by = ?

        ORDER BY applications.applied_at DESC

    """, (session["user_id"],)).fetchall()

    conn.close()

    return render_template(
        "applicants.html",
        applicants=applicants
    )


# Applied Jobs

@app.route("/applied-jobs")
def applied_jobs():

    if "user_id" not in session:
        return redirect("/login")
    
    if session["role"] != "Job Seeker":
        flash("Access Denied!", "danger")
        return redirect("/dashboard")

    conn = get_db()

    jobs = conn.execute("""
        SELECT
            jobs.job_title,
            jobs.company_name,
            jobs.location,
            jobs.salary,
            applications.applied_at

        FROM applications

        JOIN jobs
        ON applications.job_id = jobs.id

        WHERE applications.user_id = ?

        ORDER BY applications.applied_at DESC

    """, (session["user_id"],)).fetchall()

    conn.close()

    return render_template(
        "applied_jobs.html",
        jobs=jobs
    )
@app.route("/profile", methods=["GET", "POST"])
def profile():

    if "user_id" not in session:
        return redirect("/login")

    if session["role"] != "Job Seeker":
        flash("Access Denied!", "danger")
        return redirect("/dashboard")

    conn = get_db()

    user = conn.execute(
        """
        SELECT *
        FROM users
        WHERE id=?
        """,
        (session["user_id"],)
    ).fetchone()

    if request.method == "POST":

        phone = request.form["phone"]
        city = request.form["city"]

        resume = request.files.get("resume")
        photo = request.files.get("photo")

        resume_name = user["resume"]
        photo_name = user["photo"]

        # Resume Upload
        if resume and resume.filename != "":

            resume_name = secure_filename(resume.filename)

            resume.save(
                os.path.join(
                    app.config["UPLOAD_FOLDER"],
                    resume_name
                )
            )

        # Photo Upload
        if photo and photo.filename != "":

            photo_name = secure_filename(photo.filename)

            photo.save(
                os.path.join(
                    app.config["PHOTO_FOLDER"],
                    photo_name
                )
            )

        conn.execute(
            """
            UPDATE users

            SET

            phone=?,
            city=?,
            resume=?,
            photo=?

            WHERE id=?
            """,
            (
                phone,
                city,
                resume_name,
                photo_name,
                session["user_id"]
            )
        )

        conn.commit()

        flash("Profile Updated Successfully!", "success")

        user = conn.execute(
            """
            SELECT *
            FROM users
            WHERE id=?
            """,
            (session["user_id"],)
        ).fetchone()

    conn.close()

    ats_score = 0
    found_keywords = []

    if user["resume"]:

        resume_path = os.path.join(
            app.config["UPLOAD_FOLDER"],
            user["resume"]
        )

        ats_score, found_keywords = calculate_ats_score(resume_path)


    return render_template(
    "profile.html",
    user=user,
    ats_score=ats_score,
    found_keywords=found_keywords
    )
    
# My Jobs

@app.route("/my-jobs")
def my_jobs():

    if "user_id" not in session:
        return redirect("/login")
    
    if session["role"] != "Employer":
        flash("Access Denied!", "danger")
        return redirect("/dashboard")

    conn = get_db()

    jobs = conn.execute(
        """
        SELECT *
        FROM jobs
        WHERE posted_by=?
        ORDER BY created_at DESC
        """,
        (session["user_id"],)
    ).fetchall()

    conn.close()

    return render_template(
        "my_jobs.html",
        jobs=jobs
    )
    # Edit Job

@app.route("/edit-job/<int:job_id>", methods=["GET", "POST"])
def edit_job(job_id):

    if "user_id" not in session:
        return redirect("/login")
    
    if session["role"] != "Employer":
        flash("Access Denied!", "danger")
        return redirect("/dashboard")

    conn = get_db()

    job = conn.execute(
        """
        SELECT *
        FROM jobs
        WHERE id=? AND posted_by=?
        """,
        (
            job_id,
            session["user_id"]
        )
    ).fetchone()

    if job is None:

        conn.close()

        flash("Job not found!", "danger")

        return redirect("/my-jobs")

    if request.method == "POST":

        company_name = request.form["company_name"]
        job_title = request.form["job_title"]
        location = request.form["location"]
        job_type = request.form["job_type"]
        salary = request.form["salary"]
        description = request.form["description"]

        conn.execute(
            """
            UPDATE jobs

            SET

            company_name=?,
            job_title=?,
            location=?,
            job_type=?,
            salary=?,
            description=?

            WHERE id=?
            """,
            (
                company_name,
                job_title,
                location,
                job_type,
                salary,
                description,
                job_id
            )
        )

        conn.commit()

        conn.close()

        flash("Job Updated Successfully!", "success")

        return redirect("/my-jobs")

    conn.close()

    return render_template(
        "edit_job.html",
        job=job
    )
    # Delete Job

@app.route("/delete-job/<int:job_id>")
def delete_job(job_id):

    if "user_id" not in session:
        return redirect("/login")
    
    if session["role"] != "Employer":
        flash("Access Denied!", "danger")
        return redirect("/dashboard")

    conn = get_db()

    conn.execute(
        """
        DELETE FROM jobs
        WHERE id=? AND posted_by=?
        """,
        (
            job_id,
            session["user_id"]
        )
    )

    conn.commit()
    conn.close()

    flash("Job Deleted Successfully!", "success")

    return redirect("/my-jobs")
if __name__ == "__main__":
    app.run(debug=True)