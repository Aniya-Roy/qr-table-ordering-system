from flask import Blueprint, request, render_template, redirect
from database.db import get_db_connection

order_bp = Blueprint("order", __name__)

# -----------------------------
# CUSTOMER: PLACE ORDER
# -----------------------------
@order_bp.route("/order", methods=["GET", "POST"])
def place_order():
    if request.method == "GET":
        return {"message": "Order route is reachable"}

    data = request.get_json()
    table_number = data["table_number"]
    items = data["items"]

    conn = None
    cursor = None

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        total_price = 0
        for item in items:
            cursor.execute(
                "SELECT price FROM menu WHERE item_id = %s",
                (item["item_id"],)
            )
            price = cursor.fetchone()[0]
            total_price += price * item["quantity"]

        cursor.execute(
            "INSERT INTO orders (table_number, total_price) VALUES (%s, %s)",
            (table_number, total_price)
        )
        order_id = cursor.lastrowid

        for item in items:
            cursor.execute(
                "INSERT INTO order_items (order_id, item_id, quantity) VALUES (%s, %s, %s)",
                (order_id, item["item_id"], item["quantity"])
            )

        conn.commit()

        return {
            "message": "Order placed successfully",
            "order_id": order_id
        }

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


# -----------------------------
# CUSTOMER: ORDER STATUS
# -----------------------------
@order_bp.route("/order-status/<int:order_id>", methods=["GET"])
def get_order_status(order_id):
    conn = None
    cursor = None

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT order_id, table_number, status, total_price, order_time
            FROM orders
            WHERE order_id = %s
        """, (order_id,))

        order = cursor.fetchone()

        if order:
            return order
        else:
            return {"message": "Order not found"}, 404

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


# -----------------------------
# KITCHEN DASHBOARD
# -----------------------------
@order_bp.route("/kitchen", methods=["GET"])
def kitchen_dashboard():
    conn = None
    cursor = None

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT 
                o.order_id,
                o.table_number,
                o.status,
                o.total_price,
                o.order_time,
                m.name AS item_name,
                oi.quantity
            FROM orders o
            JOIN order_items oi ON o.order_id = oi.order_id
            JOIN menu m ON oi.item_id = m.item_id
            WHERE o.status != 'Completed'
            ORDER BY o.order_time DESC
        """)

        rows = cursor.fetchall()

        orders = {}
        for row in rows:
            oid = row["order_id"]
            if oid not in orders:
                orders[oid] = {
                    "order_id": oid,
                    "table_number": row["table_number"],
                    "status": row["status"],
                    "total_price": row["total_price"],
                    "order_time": row["order_time"],
                    "order_items": []
                }

            orders[oid]["order_items"].append({
                "name": row["item_name"],
                "quantity": row["quantity"]
            })

        return render_template(
            "kitchen_dashboard.html",
            orders=orders.values()
        )

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


# -----------------------------
# KITCHEN: UPDATE STATUS
# -----------------------------
@order_bp.route("/kitchen/update-status", methods=["POST"])
def kitchen_update_status():
    order_id = request.form["order_id"]
    status = request.form["status"]

    conn = None
    cursor = None

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            "UPDATE orders SET status = %s WHERE order_id = %s",
            (status, order_id)
        )

        conn.commit()
        return redirect("/kitchen")

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


# -----------------------------
# KITCHEN: REMOVE ORDER
# -----------------------------
@order_bp.route("/kitchen/remove-order", methods=["POST"])
def kitchen_remove_order():
    order_id = request.form["order_id"]

    conn = None
    cursor = None

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            "UPDATE orders SET status = 'Completed' WHERE order_id = %s",
            (order_id,)
        )

        conn.commit()
        return redirect("/kitchen")

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
