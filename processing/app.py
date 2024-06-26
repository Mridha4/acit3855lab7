from apscheduler.schedulers.background import BackgroundScheduler
import requests
from datetime import datetime
import sqlite3, logging.config, yaml
from flask import Flask, jsonify
import sqlalchemy
from sqlalchemy import create_engine, select
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, Float, DateTime
from sqlalchemy.orm import sessionmaker
# from sqlalchemy.orm import declarative_base
from sqlalchemy.ext.declarative import declarative_base
from pytz import timezone as pytztz


from base import Base  # Assuming this defines your SQLAlchemy Base
from stat_class import WorkoutStats  # Assuming this defines your data model
import pytz
import connexion

utc_zone = pytz.utc
# Base = declarative_base()

    
# Load logging configuration
with open('log_conf.yml', 'r') as f:
    log_config = yaml.safe_load(f.read())
logging.config.dictConfig(log_config)

# Create a logger object
logger = logging.getLogger('basicLogger')

# Load application configuration
with open('app_conf.yml', 'r') as f:
    app_config = yaml.safe_load(f.read())

DB_ENGINE = create_engine(f"sqlite:///{app_config['datastore']['filename']}")
Base.metadata.bind = DB_ENGINE
DB_SESSION = sessionmaker(bind=DB_ENGINE)

def populate_stats():
    logger.info("Starting Periodic Processing")
    session = DB_SESSION()

    # Fetch the last update time from the database
    current_stats = session.query(WorkoutStats).order_by(WorkoutStats.last_updated.desc()).first()




    if current_stats:
        if current_stats.last_updated.tzinfo is not None and current_stats.last_updated.tzinfo.utcoffset(current_stats.last_updated) is not None:
            # Convert to UTC if it has a timezone
            last_updated_utc = current_stats.last_updated.astimezone(utc_zone)
        else:
            # Otherwise assume it's UTC and set the timezone
            last_updated_utc = utc_zone.localize(current_stats.last_updated)
        last_updated = last_updated_utc.strftime("%Y-%m-%dT%H:%M:%S")
        
    else: 
        last_updated = datetime.strptime('2023-01-01T00:00:00', '%Y-%m-%dT%H:%M:%S')

    current_datetime = datetime.now(pytz.utc)
    current_datetime_formatted = current_datetime.strftime("%Y-%m-%dT%H:%M:%S") # CONVERTED TO UTC
    # Fetch new event data from the Storage Service
    # logger.debug(f"{last_updated} - fetching with {current_datetime}")
    health_metrics_response = requests.get(
        app_config['eventstore']['url']+'/health/metric',
        params={'start_timestamp': last_updated, 'end_timestamp': current_datetime_formatted})
    print("params", last_updated, current_datetime_formatted)
    activity_logs_response = requests.get(
        app_config['eventstore']['url']+"/activity/log",
        params={'start_timestamp': last_updated, 'end_timestamp': current_datetime_formatted})
    print("status from activitylogs", activity_logs_response.status_code)
    logger.info({activity_logs_response})
    activity_logs = activity_logs_response.json()
    health_metrics = health_metrics_response.json()
    if activity_logs_response.status_code == [] and health_metrics_response.status_code == []:
        print(f'No new events, last update at {last_updated}, current time is {current_datetime_formatted}')
        session.close()
        return
    elif activity_logs_response.status_code != 200 and health_metrics_response.status_code != 200:
        print(f'Error fetching events, status code {activity_logs_response.status_code} and {health_metrics_response.status_code}')
        session.close()
    else:
        num_activity_logs = len(activity_logs)
        num_health_metrics = len(health_metrics)
        acti_log = 0
        for log in activity_logs:
            acti_log += int(log['duration'])
        if acti_log == 0:
            acti_log = 1
        if activity_logs:
            average_duration = acti_log / len(activity_logs)
        else:
            average_duration = 0

        if health_metrics:
            heart_rate_values = [int(metric['value']) for metric in health_metrics if metric['metricType'] == 'Heart Rate']
            if heart_rate_values:
                average_heart_rate = sum(heart_rate_values) / len(heart_rate_values)
            else:
                average_heart_rate = 0
        else:
            average_heart_rate = 0



	# Initialize processed stats for adding to db
        new_stats = WorkoutStats(
            num_activity_logs=num_activity_logs,
            average_duration=average_duration,
            num_health_metrics=num_health_metrics,
            average_heart_rate=average_heart_rate,
            last_updated=current_datetime
        )
        session.add(new_stats)
        session.commit()
        #logger.debug(f'New Values: {id, num_activity_logs, num_health_metrics, average_duration, average_heart_rate, last_updated}')
        session.close()


def get_stats():
    """Retrieves the latest statistics from the SQLite database and returns them as a JSON response."""
    session = DB_SESSION()
    # logger.info("Fetching the latest statistics")
    current_stats = session.query(WorkoutStats).order_by(WorkoutStats.last_updated.desc()).first()
    if current_stats:
        # the following print statements are for debugging purposes, please delete after
        last_updated_utc = current_stats.last_updated.astimezone(utc_zone)
        print(current_stats.num_activity_logs)
        print(current_stats.average_duration)
        print(current_stats.num_health_metrics)
        print(current_stats.average_heart_rate)
        last_updated = last_updated_utc.strftime("%Y-%m-%dT%H:%M:%S")
        stats_dict = {
            "num_activity_logs": current_stats.num_activity_logs,
            "average_duration": current_stats.average_duration,
            "num_health_metrics": current_stats.num_health_metrics,
            "average_heart_rate": current_stats.average_heart_rate,
            "last_updated": last_updated
        }
        session.close()
        return stats_dict, 200
    else:
        # logger.error("No statistics found.")
        session.close()
        return "error No statistics found.", 404


def init_scheduler():
    """Initializes the scheduler to run populate_stats periodically."""
    sched = BackgroundScheduler(daemon=True, timezone=pytz.utc)
    sched.add_job(populate_stats, 'interval', seconds=app_config['scheduler']['period_sec'])
    sched.start()
    # logger.info("Scheduler has been initialized and started.")

app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("openapi.yml", strict_validation=True, validate_responses=True)

if __name__ == '__main__':
    init_scheduler()
    app.run(host='0.0.0.0', port=8100)
