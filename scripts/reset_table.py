import sqlite3

# Connect to your database
conn = sqlite3.connect('media_metadata.db')
cursor = conn.cursor()

# Drop the table if it exists
cursor.execute("DROP TABLE IF EXISTS media_metadata")

# Recreate the table with the correct columns
cursor.execute("""
    CREATE TABLE media_metadata (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        filename TEXT,
        file_path TEXT,
        date_taken TEXT,
        date_added TEXT,
        make TEXT,
        model TEXT,
        resolution TEXT,
        iso TEXT,
        f_stop TEXT,
        shutter_speed TEXT,
        camera_model TEXT,
        image_width INTEGER,
        image_height INTEGER,
        file_size INTEGER
    )
""")

# Save changes and close connection
conn.commit()
conn.close()

print("Table 'media_metadata' has been reset successfully.")
