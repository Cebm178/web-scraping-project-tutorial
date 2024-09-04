from bs4 import BeautifulSoup
import sqlite3
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import requests
import time

# Step 2: Download HTML 
url = 'https://ycharts.com/companies/TSLA/revenues'
headers = {'User-Agent': 'Mozilla/5.0'}

response = requests.get(url, headers=headers)
if response.status_code == 200:
    soup = BeautifulSoup(response.text, 'html.parser')
else:
    print(f"Error: {response.status_code}")
    exit()

# Step 3: Transform the HTML

# Find all the tables
tables = soup.find_all('table')
print(f"Number of tables found: {len(tables)}")  # Print the number of tables

# Adjust the table index if necessary
quarterly_table = tables[0]  # You may need to adjust this index based on the webpage structure

data = []
headers = []

# Extract headers
for th in quarterly_table.find_all('th'):
    headers.append(th.text.strip())

print(f"Extracted headers: {headers}")  # Print the extracted headers

# Extract rows
for row in quarterly_table.find_all('tr'):
    cols = row.find_all('td')
    cols = [col.text.strip() for col in cols]
    if cols:
        data.append(cols)

# Create DataFrame
df = pd.DataFrame(data, columns=headers)  # Store in DataFrame

#df['Date'] = pd.to_datetime(df['Date'])

print("Initial DataFrame:")

df = df.sort_values(by='Date').reset_index(drop=True) # Sort by date

print(df)

# Create a connection to the SQLite database (or create a new one)
connection = sqlite3.connect("Tesla.db")
cursor = connection.cursor()

# Create a table in the database
cursor.execute("""CREATE TABLE IF NOT EXISTS revenue (
                    Date TEXT,
                    Revenue REAL
                    )""")

# Convert DataFrame to list of tuples
tesla_tuples = list(df[['Date', 'Value']].itertuples(index=False, name=None))
print(f"First 5 tuples: {tesla_tuples[:5]}")  # Print the first 5 tuples

# Insert the data into the table
cursor.executemany("INSERT INTO revenue (Date, Revenue) VALUES (?, ?)", tesla_tuples)
connection.commit()

# Verify that the data was inserted correctly
print("Data from database:")
for row in cursor.execute("SELECT * FROM revenue"):
    print(row)

connection.close()  # Close the connection

# Data Cleaning
df['Date'] = pd.to_datetime(df['Date'])
df = df.sort_values(by='Date').reset_index(drop=True) # Sort by date

df['Value'] = df['Value'].str.replace('B', '', regex=False).astype(float)
df

# Connect to the database (or create it if it doesn't exist) 
conn = sqlite3.connect('Tesla.db') 
cursor = conn.cursor() 
# Execute your query 
cursor.execute("SELECT * FROM revenue") 
# Fetch all results from the query 
rows = cursor.fetchall() 
# Print each row
for row in rows: 
    print(row)

# Step 6: Visualize the data (3 plots)

# Plot 1: Revenue over Time
plt.figure(figsize=(10, 6))
plt.plot(df['Date'], df['Value'], marker='o', linestyle='-')
plt.title('Tesla Quarterly Revenue Over Time')
plt.xlabel('Date')
plt.ylabel('Revenue')
plt.grid(True)
plt.show()

# Plot 2: Revenue Distribution
plt.figure(figsize=(10, 6))
sns.histplot(df['Value'], kde=True)
plt.title('Distribution of Tesla Quarterly Revenue')
plt.xlabel('Revenue')
plt.ylabel('Frequency')
plt.show()

# Plot 3: Percentage Change in Revenue Over Time
df['Revenue Change (%)'] = df['Value'].pct_change(fill_method=None) * 100
plt.figure(figsize=(10, 6))
plt.plot(df['Date'], df['Revenue Change (%)'], marker='o', linestyle='-', color='orange')
plt.title('Percentage Change in Tesla Quarterly Revenue Over Time')
plt.xlabel('Date')
plt.ylabel('Revenue Change (%)')
plt.grid(True)
plt.show()