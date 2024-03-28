import connexion
from connexion import NoContent
from sqlalchemy import create_engine, and_
from sqlalchemy.orm import sessionmaker
from base import Base
# from sqlalchemy.orm import DB_SESSION
from physical_activity import PhysicalActivityLog
from health_metric import HealthMetricReading
from dateutil import parser
import yaml
import logging.config
import logging
import json
from pykafka import KafkaClient
from threading import Thread
from pykafka.common import OffsetType
from datetime import datetime, timezone



# Load and configure logging
with open('log_conf.yml', 'r') as f:
    log_config = yaml.safe_load(f.read())
logging.config.dictConfig(log_config)
logger = logging.getLogger('basicLogger')

# Load database configuration from app_conf.yml
with open('app_conf.yml', 'r') as f:
    app_config = yaml.safe_load(f.read())
db_config = app_config['datastore']

logger.info(f"Connecting to MySQL database at {db_config['hostname']} on port {db_config['port']}")

# Construct the MySQL connection string
db_connection_string = f"mysql+pymysql://{db_config['user']}:{db_config['password']}@{db_config['hostname']}:{db_config['port']}/{db_config['db']}"
DB_ENGINE = create_engine(db_connection_string)
Base.metadata.bind = DB_ENGINE
DB_SESSION = sessionmaker(bind=DB_ENGINE)


def log_physical_activity(body):
    """Receives a physical activity log"""
    session = DB_SESSION()
    processed_time = parser.parse(body['timestamp'])
    pa = PhysicalActivityLog(
        user_id=body['userId'],
        activity_type=body['activityType'],
        duration=body['duration'],
        trace_id=body['trace_id'],
        timestamp=processed_time.strftime("%Y-%m-%dT%H:%M:%S"))
    session.add(pa)
    session.commit()
    session.close()
    logger.debug(f"Stored physical activity event for user {body['trace_id']}")
    return NoContent, 201


def update_health_metric(body):
    """Receives a health metric update"""
    session = DB_SESSION()
    processed_time = parser.parse(body['timestamp'])
    hm = HealthMetricReading(
        user_id=body['userId'],
        metric_type=body['metricType'],
        value=body['value'],
        trace_id=body['trace_id'],
        timestamp=processed_time.strftime("%Y-%m-%dT%H:%M:%S")
    )
    session.add(hm)
    session.commit()
    session.close()
    logger.debug(f"Stored health metric event for user {body['trace_id']}")
    return NoContent, 201


def get_physical_activity_logs(start_timestamp, end_timestamp):
    """Gets physical activity logs between the start and end timestamps"""
    session = DB_SESSION()
    start_timestamp_datetime = datetime.strptime(start_timestamp,"%Y-%m-%dT%H:%M:%S")
    end_timestamp_datetime = datetime.strptime(end_timestamp,"%Y-%m-%dT%H:%M:%S")
    try:
        # Parse the string timestamps into datetime objects
        # start_datetime = parser.parse(start_timestamp)
        # end_datetime = parser.parse(end_timestamp)
        logger.debug(f"{start_datetime}, {end_datetime}")
        results = session.query(PhysicalActivityLog).filter(
            and_(
                PhysicalActivityLog.date_created >= start_datetime_datetime, 
                PhysicalActivityLog.date_created <= end_datetime_datetime)
        )
        results_list = []
        for reading in results:
            results_list.append(reading.to_dict())
        session.close()

        logger.info(f"Query for Physical Activity Logs between {start_timestamp} and {end_timestamp} returns {len(results_list)} results")
        return results_list, 200
    except Exception as e:
        logger.error("Error fetching physical activity logs", exc_info=True)
        session.close()
        return {"error": "Invalid datetime format"}, 400

def get_health_metric_readings(start_timestamp, end_timestamp):
    """Gets health metric readings between the start and end timestamps"""
    session = DB_SESSION()
    try:
        # start_datetime = parser.parse(start_timestamp)
        # end_datetime = parser.parse(end_timestamp)
        start_timestamp_datetime = datetime.strptime(start_timestamp,"%Y-%m-%dT%H:%M:%S")
        end_timestamp_datetime = datetime.strptime(end_timestamp,"%Y-%m-%dT%H:%M:%S")
        
        logger.debug(f'Start time: {start_datetime_datetime}, end time: {end_datetime_datetime}')
        results = session.query(HealthMetricReading).filter(
            and_(HealthMetricReading.date_created >= start_datetime_datetime,
                HealthMetricReading.date_created <= end_datetime_datetime))
        results_list = []
        for reading in results:
            results_list.append(reading.to_dict())
        session.close()
        logger.info(f"Query for Health Metric Readings between {start_timestamp_datetime} and {end_timestamp_datetime} returns {len(results_list)} results")
        return results_list, 200
    except Exception as e:
        logger.error("Error fetching health metric readings", exc_info=True)
        session.close()
        return {"error": "Invalid datetime format"}, 400
    
def process_messages():
    """ Process event messages """
    hostname = f"{app_config['events']['hostname']}:{app_config['events']['port']}"
    client = KafkaClient(hosts=hostname)
    topic = client.topics[str.encode(app_config['events']['topic'])]
    # Create a consumer on a consumer group, that only reads new messages
    # (uncommitted messages) when the service restarts.
    consumer = topic.get_simple_consumer(consumer_group=b'event_group',
                                        reset_offset_on_start=False,
                                        auto_offset_reset=OffsetType.LATEST)

    for msg in consumer:
        if msg is not None:
            msg_str = msg.value.decode('utf-8')
            msg = json.loads(msg_str)
            logger.info(f"Message: {msg}")
            payload = msg["payload"]
            if msg["type"] == "physical_activity":  
                log_physical_activity(payload)
            elif msg["type"] == "health_metric":  
                update_health_metric(payload)
            consumer.commit_offsets()


app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("openapi.yml", strict_validation=True, validate_responses=True)

if __name__ == "__main__":
    
    t1 = Thread(target=process_messages, daemon=True)
    # t1.setDaemon(True)
    t1.start()
    
    app.run(host='0.0.0.0', port=8090)
