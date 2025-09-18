import sqlite3
import pandas as pd

# Load CSV
df = pd.read_csv("revenue.csv")

# Save to SQLite
conn = sqlite3.connect("revenue.db")
df.to_sql("revenue", conn, if_exists="replace", index=False)
conn.close()
print("Database created successfully!")
