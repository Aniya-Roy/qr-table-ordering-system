from flask import Blueprint, render_template, request, session
from database.db import get_db_connection

kitchen_bp = Blueprint("kitchen", __name__)

# ---------------- KITCHEN DASHBOARD ----------------
@kitchen_bp.route("/kitchen/orders")
def kitchen_orders():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # ---------------------------
    # LIVE ORDERS
    # ---------------------------
    cursor.execute("""
        SELECT * FROM orders
        WHERE status IN ('pending','preparing')
        AND DATE(order_time) = CURDATE()
        ORDER BY order_time DESC
    """)
    orders = cursor.fetchall()
    live_orders = []

    for order in orders:
        cursor.execute("""
            SELECT m.name, oi.quantity, oi.status
            FROM order_items oi
            JOIN menu m ON oi.item_id = m.item_id
            WHERE oi.order_id = %s
        """, (order["order_id"],))
        items = cursor.fetchall()

        live_orders.append({
            "order_id": order["order_id"],
            "table_number": order["table_number"],
            "status": order["status"],
            "order_time": order["order_time"],
            "items": items
        })

    # ---------------------------
    # COMPLETED ORDERS
    # ---------------------------
    cursor.execute("""
        SELECT * FROM orders
        WHERE status = 'completed'
        AND DATE(order_time) = CURDATE()
        ORDER BY order_time DESC
    """)
    completed = cursor.fetchall()
    completed_orders = []

    for order in completed:
        cursor.execute("""
            SELECT m.name, oi.quantity
            FROM order_items oi
            JOIN menu m ON oi.item_id = m.item_id
            WHERE oi.order_id = %s
        """, (order["order_id"],))
        items = cursor.fetchall()

        completed_orders.append({
            "order_id": order["order_id"],
            "table_number": order["table_number"],
            "items": items
        })

    cursor.close()
    conn.close()

    role = session.get("role", "staff")

    return render_template(
        "kitchen_dashboard.html",
        live_orders=live_orders,
        completed_orders=completed_orders,
        role=role
    )


# ---------------------------
# UPDATE ORDER STATUS
# ---------------------------
@kitchen_bp.route("/kitchen/order/update", methods=["POST"])
def update_order_status():
    order_id = request.form.get("order_id")
    status = request.form.get("status")

    if not order_id or not status:
        return "Bad Request", 400

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE orders SET status=%s WHERE order_id=%s",
        (status, order_id)
    )

    conn.commit()
    cursor.close()
    conn.close()

    return "OK", 200
