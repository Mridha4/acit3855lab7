from apscheduler.schedulers.background import BackgroundScheduler
import requests
from datetime import datetime, timezone
import sqlite3, logging.config, yaml
from flask import Flask, jsonify
import sqlalchemy
from sqlalchemy import create_engine, select
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, Float, DateTime
from sqlalchemy.orm import sessionmaker
from base import Base  # Assuming this defines your SQLAlchemy Base
from stat_class import WorkoutStats  # Assuming this defines your data model
import pytz
import connexion

Base = declarative_base()

class WorkoutStats(Base):
    __tablename__ = 'statistics'
    id = Column(Integer, primary_key=True)
    num_activity_logs = Column(Integer)
    average_duration = Column(Float)
    num_health_metrics = Column(Integer)
    average_heart_rate = Column(Float)
    last_updated = Column(DateTime)
    
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
        last_updated = current_stats.last_updated.strftime('%Y-%m-%dT%H:%M:%SZ')
        num_activity_logs = current_stats.num_activity_logs
        num_health_metrics = current_stats.num_health_metrics
    else: 
        last_updated = datetime.strptime('2023-01-01T00:00:00Z', '%Y-%m-%dT%H:%M:%SZ')
        num_activity_logs = 0
        num_health_metrics = 0

    current_datetime = datetime.now()
    current_datetime_formatted = current_datetime.strftime('%Y-%m-%dT%H:%M:%SZ')
    # Fetch new event data from the Storage Service
    logger.debug(f"{last_updated} - fetching with {current_datetime}")
    health_metrics_response = requests.get(
        f"{app_config['eventstore']['url']}/health/metric",
        params={'start_timestamp': last_updated, 'end_timestamp': current_datetime_formatted})
    activity_logs_response = requests.get(
        f"{app_config['eventstore']['url']}/activity/log",
        params={'start_timestamp': last_updated, 'end_timestamp': current_datetime_formatted})
    logger.info({activity_logs_response})
    if activity_logs_response.status_code == 200 and health_metrics_response.status_code == 200:
        activity_logs = activity_logs_response.json()
        health_metrics = health_metrics_response.json()

        # Process statistics from responses
        num_activity_logs += len(activity_logs)
        num_health_metrics += len(health_metrics)
        average_duration = sum(log['duration'] for log in activity_logs) / len(activity_logs) if activity_logs else 0
        average_heart_rate = sum(metric['value'] for metric in health_metrics if metric['metricType'] == 'Heart Rate') / len(health_metrics) if health_metrics else 0

        # Initialize processed stats for adding to db
        new_stats = WorkoutStats(
            num_activity_logs=num_activity_logs,
            average_duration=average_duration,
            num_health_metrics=num_health_metrics,
            average_heart_rate=average_heart_rate,
            last_updated=current_datetime
        )
    else:
        logger.error("errors")    
    session.add(new_stats)
    session.commit()
    logger.debug(f'New Values: {id, num_activity_logs, num_health_metrics, average_duration, average_heart_rate, last_updated}')
    session.close()
    logger.info("Database updated with new statistics.")

    logger.info("Periodic Processing Completed")

def get_stats():
    """Retrieves the latest statistics from the SQLite database and returns them as a JSON response."""
    session = DB_SESSION()
    logger.info("Fetching the latest statistics")
    current_stats = session.query(WorkoutStats).order_by(WorkoutStats.last_updated.desc()).first()
    if current_stats:
        stats_dict = {
            "num_activity_logs": current_stats.num_activity_logs,
            "average_duration": current_stats.average_duration,
            "num_health_metrics": current_stats.num_health_metrics,
            "average_heart_rate": current_stats.average_heart_rate,
            "last_updated": current_stats.last_updated.strftime('%Y-%m-%dT%H:%M:%SZ')
        }
        return stats_dict, 200
    else:
        logger.error("No statistics found.")
        return {"error": "No statistics found."}, 404

def init_scheduler():
    """Initializes the scheduler to run populate_stats periodically."""
    sched = BackgroundScheduler(daemon=True, timezone=pytz.utc)
    sched.add_job(populate_stats, 'interval', seconds=app_config['scheduler']['period_sec'])
    sched.start()
    logger.info("Scheduler has been initialized and started.")

app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("openapi.yml", strict_validation=True, validate_responses=True)

if __name__ == '__main__':
    init_scheduler()
    app.run(host='0.0.0.0', port=8100)