import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "documind.db"

connection = sqlite3.connect(DB_PATH)

try:
    cursor = connection.cursor()

    cursor.execute("PRAGMA table_info(document_analyses)")
    columns = [row[1] for row in cursor.fetchall()]

    if "document_type" not in columns:
        cursor.execute(
            """
            ALTER TABLE document_analyses
            ADD COLUMN document_type VARCHAR(100) NOT NULL DEFAULT 'Other'
            """
        )

        connection.commit()

        print("✅ document_type column added successfully.")
    else:
        print("✅ document_type column already exists.")

finally:
    connection.close()