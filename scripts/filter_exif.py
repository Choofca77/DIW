import sqlite3

# Step 1: Connect to the SQLite database
db_name = "media_metadata.db"  # Change this if your database file has a different name
conn = sqlite3.connect(db_name)
cursor = conn.cursor()

try:
    # Step 2: Verify the table name
    print("Checking available tables in the database...")
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print("Tables found:", tables)

    # Update this if your table name is different
    table_name = "media_metadata"
    if (table_name,) not in tables:
        raise ValueError(f"Table '{table_name}' not found in the database.")

    # Step 3: Verify the table structure
    print(f"Checking columns in the table '{table_name}'...")
    cursor.execute(f"PRAGMA table_info({table_name});")
    columns = cursor.fetchall()
    print("Columns in the table:", columns)

    # Ensure the table has a column for EXIF data
    exif_column = "metadata"  # Update this if your EXIF column has a different name
    if not any(col[1] == exif_column for col in columns):
        raise ValueError(f"Column '{exif_column}' not found in the table '{table_name}'.")

    # Step 4: Count rows with valid EXIF data
    print("Counting rows with valid EXIF data...")
    cursor.execute(f"""
        SELECT COUNT(*) FROM {table_name}
        WHERE {exif_column} IS NOT NULL AND {exif_column} != '' AND {exif_column} != '{{}}';
    """)
    valid_exif_count = cursor.fetchone()[0]
    print(f"Rows with valid EXIF data: {valid_exif_count}")

    # Step 5: Delete rows with no EXIF data
    print("Deleting rows with no EXIF data...")
    cursor.execute(f"""
        DELETE FROM {table_name}
        WHERE {exif_column} IS NULL OR {exif_column} = '' OR {exif_column} = '{{}}';
    """)
    conn.commit()

    # Step 6: Count remaining rows
    print("Counting remaining rows after cleanup...")
    cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
    remaining_rows = cursor.fetchone()[0]
    print(f"Remaining rows: {remaining_rows}")

    # Step 7: Trim the table to 30 rows if necessary
    if remaining_rows > 30:
        print("Trimming the table to keep only the first 30 rows...")
        cursor.execute(f"""
            DELETE FROM {table_name}
            WHERE rowid NOT IN (
                SELECT rowid FROM {table_name} ORDER BY rowid LIMIT 30
            );
        """)
        conn.commit()
        print("Table trimmed to 30 rows.")

    # Final check
    print("Final row count:")
    cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
    final_count = cursor.fetchone()[0]
    print(f"Final row count: {final_count}")

except Exception as e:
    print(f"An error occurred: {e}")

finally:
    # Step 8: Close the database connection
    conn.close()
    print("Database connection closed.")