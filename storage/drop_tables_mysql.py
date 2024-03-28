import mysql.connector
# Connect to the MySQL database
conn = mysql.connector.connect(user='user', password='password', host='kafka3855.eastus.cloudapp.azure.com', database='events')

cursor = conn.cursor()

# Drop the tables
cursor.execute('DROP TABLE IF EXISTS physical_activity_log')
cursor.execute('DROP TABLE IF EXISTS health_metric_reading')

conn.commit()
cursor.close()
conn.close()
