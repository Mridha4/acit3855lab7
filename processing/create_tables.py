import sqlite3
import yaml

with open('app_conf.yml', 'r') as f:
    app_config = yaml.safe_load(f.read())
    
conn = sqlite3.connect(app_config['datastore']['filename'])
cursor = conn.cursor()
cursor.execute('''
CREATE TABLE IF NOT EXISTS statistics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    num_activity_logs INTEGER,
    num_health_metrics INTEGER,
    average_duration INTEGER,
    average_heart_rate INTEGER,
    last_updated DATETIME
)
''')
conn.commit()
conn.close()
