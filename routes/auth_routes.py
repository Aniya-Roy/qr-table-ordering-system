from flask import Blueprint, render_template, request, redirect, url_for, session
from database.db import get_db_connection

auth_bp = Blueprint("auth", __name__)

# ==============================
# LANDING PAGE + LOGIN
# ==============================
@auth_bp.route("/", methods=["GET", "POST"])
def landing():
    error = None

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute(
            "SELECT * FROM users WHERE username=%s AND password=%s",
            (username, password)
        )
        user = cursor.fetchone()

        cursor.close()
        conn.close()

        if user:
            # ✅ Store session values
            session["user_id"] = user["user_id"]
            session["role"] = user["role"]

            # ✅ Redirect based on role
            if user["role"] == "admin":
                return redirect(url_for("admin.admin_dashboard"))
            else:
                return redirect(url_for("kitchen.kitchen_orders"))

        # If login fails
        error = "Invalid credentials. Please sign up if you don’t have an account."

    return render_template("landing.html", error=error)


# ==============================
# SIGNUP
# ==============================
@auth_bp.route("/signup", methods=["GET", "POST"])
def signup():
    error = None
    success = None

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        role = request.form["role"]

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Check if username already exists
        cursor.execute(
            "SELECT * FROM users WHERE username=%s",
            (username,)
        )
        existing_user = cursor.fetchone()

        if existing_user:
            error = "Username already exists. Please login."
        else:
            cursor.execute(
                "INSERT INTO users (username, password, role) VALUES (%s, %s, %s)",
                (username, password, role)
            )
            conn.commit()
            success = "Account created successfully. Please login."

        cursor.close()
        conn.close()

    return render_template("signup.html", error=error, success=success)


# ==============================
# LOGOUT
# ==============================
@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.landing"))
