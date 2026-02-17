from flask import Blueprint, render_template, request, redirect, flash
from database.db import get_db_connection

staff_bp = Blueprint("staff", __name__)

# Allowed roles
ALLOWED_ROLES = ["Admin", "Kitchen", "Waiter"]

# 🔹 VIEW STAFF
@staff_bp.route("/admin/staff")
def staff_dashboard():
    search = request.args.get("q", "")

    conn = None
    cursor = None

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        if search:
            cursor.execute("""
                SELECT * FROM staff
                WHERE LOWER(name) LIKE LOWER(%s)
                   OR phone LIKE %s
                   OR LOWER(role) LIKE LOWER(%s)
            """, (f"%{search}%", f"%{search}%", f"%{search}%"))
        else:
            cursor.execute("SELECT * FROM staff")

        staff = cursor.fetchall()
        return render_template("staff_dashboard.html", staff=staff, search=search)

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


# 🔹 ADD STAFF
@staff_bp.route("/admin/staff/add", methods=["POST"])
def add_staff():
    name = request.form.get("name")
    phone = request.form.get("phone")
    role = request.form.get("role").capitalize()

    # Validation
    if not all([name, phone, role]):
        flash("All fields are required.", "danger")
        return redirect("/admin/staff")

    if role not in ALLOWED_ROLES:
        flash("Invalid role selected.", "danger")
        return redirect("/admin/staff")

    if not phone.isdigit():
        flash("Phone number must be numeric.", "danger")
        return redirect("/admin/staff")

    conn = None
    cursor = None

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO staff (name, phone, role, is_active, status)
            VALUES (%s, %s, %s, 1, 'active')
        """, (name, phone, role))

        conn.commit()

        flash("Staff added successfully.", "success")
        return redirect("/admin/staff")

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


# 🔹 EDIT STAFF
@staff_bp.route("/admin/staff/edit/<int:staff_id>", methods=["GET", "POST"])
def edit_staff(staff_id):
    conn = None
    cursor = None

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        if request.method == "POST":
            name = request.form["name"]
            phone = request.form["phone"]
            role = request.form["role"].capitalize()
            status = request.form["status"].lower()

            if role not in ALLOWED_ROLES:
                flash("Invalid role selected.", "danger")
                return redirect(f"/admin/staff/edit/{staff_id}")

            if not phone.isdigit():
                flash("Phone number must be numeric.", "danger")
                return redirect(f"/admin/staff/edit/{staff_id}")

            cursor.execute("""
                UPDATE staff
                SET name=%s, phone=%s, role=%s, status=%s
                WHERE staff_id=%s
            """, (name, phone, role, status, staff_id))

            conn.commit()

            flash("Staff updated successfully.", "success")
            return redirect("/admin/staff")

        cursor.execute("SELECT * FROM staff WHERE staff_id=%s", (staff_id,))
        staff = cursor.fetchone()

        return render_template("edit_staff.html", staff=staff)

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


# 🔹 TOGGLE ACTIVE / INACTIVE
@staff_bp.route("/admin/staff/toggle/<int:staff_id>")
def toggle_staff(staff_id):
    conn = None
    cursor = None

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE staff
            SET is_active = NOT is_active,
                status = CASE
                            WHEN LOWER(status)='active' THEN 'inactive'
                            ELSE 'active'
                         END
            WHERE staff_id = %s
        """, (staff_id,))

        conn.commit()
        return redirect("/admin/staff")

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


# 🔹 DELETE STAFF
@staff_bp.route("/admin/staff/delete/<int:staff_id>")
def delete_staff(staff_id):
    conn = None
    cursor = None

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("DELETE FROM staff WHERE staff_id = %s", (staff_id,))
        conn.commit()

        flash("Staff deleted successfully.", "success")
        return redirect("/admin/staff")

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
