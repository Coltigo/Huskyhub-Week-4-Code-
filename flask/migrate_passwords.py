import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

import bcrypt
import mysql.connector

DB_HOST = os.environ.get("DB_HOST", "huskyhub-db")
DB_USER = os.environ.get("DB_USER", "user")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "supersecretpw")
DB_NAME = os.environ.get("DB_NAME", "huskyhub")

conn = mysql.connector.connect(
    host=DB_HOST,
    user=DB_USER,
    password=DB_PASSWORD,
    database=DB_NAME,
)
cursor = conn.cursor(dictionary=True)

cursor.execute("SELECT user_id, username, password FROM users")
users = cursor.fetchall()

updated = 0
skipped = 0

for user in users:
    plaintext = user["password"]

    # Skip rows that are already bcrypt hashes
    if plaintext.startswith("$2b$") or plaintext.startswith("$2a$"):
        print(f"  SKIP  {user['username']} (already hashed)")
        skipped += 1
        continue

    hashed = bcrypt.hashpw(plaintext.encode(), bcrypt.gensalt()).decode()

    update_cursor = conn.cursor()
    update_cursor.execute(
        "UPDATE users SET password = %s WHERE user_id = %s",
        (hashed, user["user_id"]),
    )
    update_cursor.close()

    print(f"  OK    {user['username']}")
    updated += 1

conn.commit()
conn.close()

print(f"\nDone. {updated} password(s) hashed, {skipped} already hashed and skipped.")
