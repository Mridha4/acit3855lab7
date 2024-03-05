import sqlite3

conn = sqlite3.connect('readings.sqlite')

c = conn.cursor()

# Update for physical_activity_log table
c.execute('''
CREATE TABLE physical_activity_log
(id INTEGER PRIMARY KEY ASC, 
user_id VARCHAR(250) NOT NULL,
activity_type VARCHAR(250) NOT NULL,
duration INTEGER NOT NULL,
timestamp VARCHAR(100) NOT NULL,
trace_id VARCHAR(36) NOT NULL,  # Add trace_id column
date_created VARCHAR(100) NOT NULL)
''')

# Update for health_metric_reading table
c.execute('''
CREATE TABLE health_metric_reading
(id INTEGER PRIMARY KEY ASC, 
user_id VARCHAR(250) NOT NULL,
metric_type VARCHAR(250) NOT NULL,
value INTEGER NOT NULL,
timestamp VARCHAR(100) NOT NULL,
trace_id VARCHAR(36) NOT NULL,  # Add trace_id column
date_created VARCHAR(100) NOT NULL)
''')

conn.commit()
conn.close()