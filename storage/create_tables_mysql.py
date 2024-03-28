import mysql.connector

# Connect to the MySQL database
conn = mysql.connector.connect(user='user', password='password', host='kafka3855.eastus.cloudapp.azure.com', database='events')

cursor = conn.cursor()

# Creating the physical_activity_log table
cursor.execute('''
CREATE TABLE IF NOT EXISTS physical_activity_log (
    id INT NOT NULL AUTO_INCREMENT,
    user_id VARCHAR(250) NOT NULL,
    activity_type VARCHAR(250) NOT NULL,
    duration INT NOT NULL,
    trace_id VARCHAR(36) NOT NULL,
    timestamp VARCHAR(100) NOT NULL,
    date_created DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    CONSTRAINT physical_activity_pk PRIMARY KEY (id))
''')

# Creating the health_metric_reading table
cursor.execute('''
CREATE TABLE IF NOT EXISTS health_metric_reading (
    id INT NOT NULL AUTO_INCREMENT,
    user_id VARCHAR(250) NOT NULL,
    metric_type VARCHAR(250) NOT NULL,
    value INT NOT NULL,
    trace_id VARCHAR(36) NOT NULL,
    timestamp VARCHAR(100) NOT NULL,
    date_created DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    CONSTRAINT health_metric_pk PRIMARY KEY (id))
''')

conn.commit()
cursor.close()
conn.close()
