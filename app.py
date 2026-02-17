from flask import Flask, render_template
from flask_cors import CORS

from routes.menu_routes import menu_bp
from routes.order_routes import order_bp
from routes.auth_routes import auth_bp
from routes.kitchen_routes import kitchen_bp
from routes.admin_routes import admin_bp
from routes.staff_routes import staff_bp
from routes.user_routes import user_bp

# Image upload
import os
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = 'static/images'

app = Flask(__name__)
app.secret_key = "restaurant_secret_key"
CORS(app)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# ✅ REGISTER BLUEPRINTS
app.register_blueprint(menu_bp)
app.register_blueprint(order_bp)
app.register_blueprint(auth_bp)      # Landing + Login handled here
app.register_blueprint(kitchen_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(staff_bp)
app.register_blueprint(user_bp)


# ✅ Only keep non-auth standalone routes here

@app.route("/menu/<int:table_no>")
def menu_page(table_no):
    return render_template("menu.html", table_no=table_no)


@app.route("/order-status-page/<int:order_id>")
def order_status_page(order_id):
    return render_template("order_status.html", order_id=order_id)


if __name__ == "__main__":
    app.run() # Add debug=True
