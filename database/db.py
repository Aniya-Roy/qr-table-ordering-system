import os
import mysql.connector
from urllib.parse import urlparse

def get_db_connection():
    db_url = os.environ.get("mysql://root:dGLbvILUaIrkstjmUPvNfHQhvAeyzTUk@mysql.railway.internal:3306/railway")

    if db_url:
        parsed = urlparse(db_url)

        return mysql.connector.connect(
            host=parsed.hostname,
            user=parsed.username,
            password=parsed.password,
            database=parsed.path.lstrip('/'),
            port=parsed.port or 3306,
            ssl_disabled=False
        )

    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="root",
        database="qr_ordering_db"
    )
