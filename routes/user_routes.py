from flask import Blueprint, render_template, request, redirect, url_for
from database.db import get_db_connection
import json
from datetime import datetime

user_bp = Blueprint("user", __name__)

# ================= USER MENU PAGE =================
@user_bp.route("/menu/<int:table_id>")
def show_menu(table_id):
    conn = None
    cursor = None

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # -----------------------
        # 1️⃣ Fetch Menu Items
        # -----------------------
        cursor.execute("SELECT * FROM menu")
        menu_items = cursor.fetchall()

        # Group menu by category
        menu_by_category = {}
        for item in menu_items:
            category = item["category"]
            if category not in menu_by_category:
                menu_by_category[category] = []
            menu_by_category[category].append(item)

        # -----------------------
        # 2️⃣ Check Active Order
        # -----------------------
        cursor.execute("""
            SELECT * FROM orders
            WHERE table_number = %s
            AND status IN ('pending', 'preparing')
            ORDER BY order_time DESC
            LIMIT 1
        """, (table_id,))

        active_order = cursor.fetchone()
        active_items = []

        if active_order:
            cursor.execute("""
                SELECT oi.*, m.name, m.price
                FROM order_items oi
                JOIN menu m ON oi.item_id = m.item_id
                WHERE oi.order_id = %s
            """, (active_order["order_id"],))
            active_items = cursor.fetchall()

        return render_template(
            "user_menu.html",
            table_id=table_id,
            menu_by_category=menu_by_category,
            active_order=active_order,
            active_items=active_items
        )

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


# ================= PLACE ORDER =================
@user_bp.route("/place-order", methods=["POST"])
def place_order():
    table_id = request.form.get("table_id")
    cart_data = request.form.get("cart_data")

    if not cart_data:
        return redirect(url_for("user.show_menu", table_id=table_id))

    try:
        cart = json.loads(cart_data)
    except json.JSONDecodeError:
        return redirect(url_for("user.show_menu", table_id=table_id))

    # Remove invalid items
    cart = [item for item in cart if item.get("quantity", 0) > 0]

    if not cart:
        return redirect(url_for("user.show_menu", table_id=table_id))

    total_price = sum(item["price"] * item["quantity"] for item in cart)

    conn = None
    cursor = None

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Check existing active order
        cursor.execute("""
            SELECT order_id FROM orders
            WHERE table_number = %s
            AND status IN ('pending', 'preparing')
            ORDER BY order_time DESC
            LIMIT 1
        """, (table_id,))

        existing_order = cursor.fetchone()

        if existing_order:
            order_id = existing_order["order_id"]
        else:
            cursor.execute("""
                INSERT INTO orders (table_number, total_price, status, order_time)
                VALUES (%s, %s, %s, %s)
            """, (table_id, total_price, "pending", datetime.now()))
            conn.commit()
            order_id = cursor.lastrowid

        # Insert order items
        for item in cart:
            cursor.execute("""
                INSERT INTO order_items (order_id, item_id, quantity)
                VALUES (%s, %s, %s)
            """, (
                order_id,
                item["item_id"],
                item["quantity"]
            ))

        conn.commit()

        return redirect(url_for("user.show_menu", table_id=table_id))

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


# ================= CANCEL ITEM =================
@user_bp.route("/cancel_item/<int:item_id>", methods=["POST"])
def cancel_item(item_id):
    conn = None
    cursor = None

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE order_items
            SET status = 'cancelled'
            WHERE id = %s
            AND status = 'pending'
        """, (item_id,))

        conn.commit()
        return redirect(request.referrer)

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
