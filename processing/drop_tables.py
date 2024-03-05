import sqlite3
import yaml

with open('app_conf.yml', 'r') as f:
    app_config = yaml.safe_load(f.read())

conn = sqlite3.connect(app_config['datastore']['filename'])
cursor = conn.cursor()

# Drop the tables
cursor.execute('DROP TABLE IF EXISTS statistics')

conn.commit()
cursor.close()
conn.close()
