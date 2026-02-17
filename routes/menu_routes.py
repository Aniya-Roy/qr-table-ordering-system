from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from database.db import get_db_connection
import os
import uuid
from werkzeug.utils import secure_filename

menu_bp = Blueprint("menu", __name__)

# MENU DASHBOARD
@menu_bp.route("/admin/menu")
def menu_dashboard():
    conn = None
    cursor = None

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT item_id, name, price, category, is_available, image
            FROM menu
            ORDER BY name
        """)
        items = cursor.fetchall()
        return render_template("admin_menu.html", items=items)

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


# ADD MENU ITEM
@menu_bp.route("/admin/menu/add", methods=["GET", "POST"])
def add_menu():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        price = request.form.get("price", "").strip()
        category = request.form.get("category", "").strip()
        is_available = 1 if request.form.get("is_available") else 0

        file = request.files.get("image")
        filename = None

        if file and file.filename:
            unique_name = f"{uuid.uuid4()}_{secure_filename(file.filename)}"
            upload_folder = current_app.config["UPLOAD_FOLDER"]
            os.makedirs(upload_folder, exist_ok=True)
            file.save(os.path.join(upload_folder, unique_name))
            filename = unique_name

        if not name or not price or not category:
            flash("All fields are required.", "danger")
            return redirect(url_for("menu.add_menu"))

        try:
            price = float(price)
        except ValueError:
            flash("Price must be a number.", "danger")
            return redirect(url_for("menu.add_menu"))

        conn = None
        cursor = None

        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO menu (name, price, category, is_available, image)
                VALUES (%s, %s, %s, %s, %s)
            """, (name, price, category, is_available, filename))
            conn.commit()

        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

        flash(f"Menu item '{name}' added successfully.", "success")
        return redirect(url_for("menu.menu_dashboard"))

    return render_template("add_menu.html")


# EDIT MENU ITEM
@menu_bp.route("/admin/menu/edit/<int:item_id>")
def edit_menu(item_id):
    conn = None
    cursor = None

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM menu WHERE item_id=%s", (item_id,))
        item = cursor.fetchone()

        if not item:
            flash("Menu item not found.", "danger")
            return redirect(url_for("menu.menu_dashboard"))

        return render_template("edit_menu.html", item=item)

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


# UPDATE MENU ITEM
@menu_bp.route("/admin/menu/update", methods=["POST"])
def update_menu():
    item_id = request.form.get("item_id")
    name = request.form.get("name", "").strip()
    category = request.form.get("category", "").strip()
    price = request.form.get("price", "").strip()
    file = request.files.get("image")

    if not all([item_id, name, category, price]):
        flash("All fields are required.", "danger")
        return redirect(url_for("menu.menu_dashboard"))

    try:
        price = float(price)
    except ValueError:
        flash("Price must be a number.", "danger")
        return redirect(url_for("menu.menu_dashboard"))

    conn = None
    cursor = None

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT image FROM menu WHERE item_id=%s", (item_id,))
        old_item = cursor.fetchone()
        filename = old_item["image"]

        if file and file.filename:
            unique_name = f"{uuid.uuid4()}_{secure_filename(file.filename)}"
            upload_folder = current_app.config["UPLOAD_FOLDER"]
            file.save(os.path.join(upload_folder, unique_name))
            filename = unique_name

        cursor.execute("""
            UPDATE menu
            SET name=%s, category=%s, price=%s, image=%s
            WHERE item_id=%s
        """, (name, category, price, filename, item_id))
        conn.commit()

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    flash(f"Menu item '{name}' updated successfully.", "success")
    return redirect(url_for("menu.menu_dashboard"))


# TOGGLE MENU
@menu_bp.route("/admin/menu/toggle/<int:item_id>")
def toggle_menu(item_id):
    conn = None
    cursor = None

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE menu
            SET is_available = NOT is_available
            WHERE item_id=%s
        """, (item_id,))
        conn.commit()

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    flash("Menu availability updated.", "success")
    return redirect(url_for("menu.menu_dashboard"))


# DELETE MENU
@menu_bp.route("/delete/<int:item_id>", methods=["POST"])
def delete_menu(item_id):
    conn = None
    cursor = None

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM menu WHERE item_id=%s", (item_id,))
        conn.commit()

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    return redirect(url_for("menu.menu_dashboard"))
