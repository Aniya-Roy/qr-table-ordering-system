import os
import mysql.connector
from urllib.parse import urlparse

def get_db_connection():
    db_url = os.environ.get("DATABASE_URL")

    # If this is missing, the app will stop and tell you why in the Render logs
    if not db_url:
        raise ConnectionError("Missing DATABASE_URL! Go to Render Dashboard -> Environment.")

    parsed = urlparse(db_url)

    return mysql.connector.connect(
        host=parsed.hostname,
        user=parsed.username,
        password=parsed.password,
        database=parsed.path.lstrip('/'),
        port=parsed.port or 3306
    )
