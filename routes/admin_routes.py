from flask import Blueprint, render_template, redirect, session, request, url_for, flash
from database.db import get_db_connection
from datetime import datetime

admin_bp = Blueprint("admin", __name__)


@admin_bp.route("/admin")
def admin_dashboard():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # ---------- STAT CARDS ----------
    cursor.execute("SELECT COUNT(*) AS total FROM orders")
    total_orders = cursor.fetchone()["total"]

    cursor.execute("SELECT IFNULL(SUM(total_price),0) AS revenue FROM orders")
    revenue = cursor.fetchone()["revenue"]

    cursor.execute("SELECT COUNT(*) AS pending FROM orders WHERE status='pending'")
    pending_orders = cursor.fetchone()["pending"]

    cursor.execute("SELECT COUNT(DISTINCT table_number) AS tables FROM orders")
    active_tables = cursor.fetchone()["tables"]

    # ---------- REVENUE LINE CHART ----------
    cursor.execute("""
        SELECT DATE(order_time) AS day, SUM(total_price) AS total
        FROM orders
        GROUP BY DATE(order_time)
        ORDER BY day
    """)
    revenue_data = cursor.fetchall()

    labels = [str(row["day"]) for row in revenue_data]
    values = [float(row["total"]) for row in revenue_data]

    # ---------- ORDER STATUS PIE ----------
    cursor.execute("""
        SELECT status, COUNT(*) AS count
        FROM orders
        GROUP BY status
    """)
    status_data = cursor.fetchall()

    status_labels = [row["status"] for row in status_data]
    status_values = [row["count"] for row in status_data]

    # ---------- MOST ORDERED ITEMS ----------
    cursor.execute("""
    SELECT m.name, SUM(oi.quantity) AS total
    FROM order_items oi
    JOIN menu m ON oi.item_id = m.item_id
    GROUP BY m.name
    ORDER BY total DESC
    LIMIT 5
                   """)
    item_data = cursor.fetchall()
    item_labels = [row["name"] for row in item_data]
    item_values = [row["total"] for row in item_data]

    cursor.close()
    conn.close()

    return render_template(
        "admin_dashboard.html",
        total_orders=total_orders,
        revenue=revenue,
        pending_orders=pending_orders,
        active_tables=active_tables,
        labels=labels,
        values=values,
        status_labels=status_labels,
        status_values=status_values,
        item_labels=item_labels,
        item_values=item_values
    )


@admin_bp.route("/admin/orders")
def admin_orders():
    # Get the selected date from query params (if any)
    selected_date = request.args.get('order_date')

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if selected_date:
        # Filter orders by the selected date
        cursor.execute("""
            SELECT order_id, table_number, total_price, status, order_time
            FROM orders
            WHERE DATE(order_time) = %s
            ORDER BY order_time DESC
        """, (selected_date,))
    else:
        # Default: show today's orders
        today = datetime.today().date()
        cursor.execute("""
            SELECT order_id, table_number, total_price, status, order_time
            FROM orders
            WHERE DATE(order_time) = %s
            ORDER BY order_time DESC
        """, (today,))

    orders = cursor.fetchall()

    cursor.close()
    conn.close()

    # Pass the selected_date to the template to pre-fill the date picker
    return render_template(
        "admin_orders.html",
        orders=orders,
        selected_date=selected_date or datetime.today().strftime("%Y-%m-%d")
    )

