import sqlite3

# Connect to your SQLite database
conn = sqlite3.connect('media_metadata.db')
cursor = conn.cursor()

# Add the missing column
cursor.execute("ALTER TABLE media_metadata ADD COLUMN date_taken TEXT")

# Save and close
conn.commit()
conn.close()

print("Column 'date_taken' added successfully.")
