import sqlite3
import pandas as pd

db_name = "media_metadata.db"
excel_file = "media_metadata.xlsx"

# Connect to the database
conn = sqlite3.connect(db_name)

# Read the table into a pandas DataFrame
df = pd.read_sql_query("SELECT * FROM media_metadata", conn)

# Export to Excel
df.to_excel(excel_file, index=False)
print(f"Data exported to {excel_file}")

# Close the connection
conn.close()