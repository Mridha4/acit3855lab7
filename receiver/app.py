import connexion
from connexion import NoContent
import json
from datetime import datetime
import yaml
import uuid
import logging.config
from pykafka import KafkaClient

# Load application configuration
with open('app_conf.yml', 'r') as f:
    app_config = yaml.safe_load(f.read())

# Load logging configuration
with open('log_conf.yml', 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

# Create logger from configuration
logger = logging.getLogger('basicLogger')

event_data = {
    "activity_log_count": 0,
    "health_metric_count": 0,
    "last_five_activity_logs": [],
    "last_five_health_metrics": []
}

def produce_message(topic_name, message):
    """Produce message to Kafka topic"""
    client = KafkaClient(hosts=f"{app_config['events']['hostname']}:{app_config['events']['port']}")
    topic = client.topics[str.encode(topic_name)]
    producer = topic.get_sync_producer()
    producer.produce(message.encode('utf-8'))

def log_physical_activity(body):
    trace_id = str(uuid.uuid4())
    logger.info(f"Received event physical_activity request with a trace id of {trace_id}")
    global event_data
    event_data["activity_log_count"] += 1
    event_data["last_five_activity_logs"].insert(0, {
        "received_timestamp": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        "msg_data": body
    })
    event_data["last_five_activity_logs"] = event_data["last_five_activity_logs"][:5]

    # Produce message to Kafka
    msg = {
        "type": "physical_activity",
        "datetime": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        "payload": body,
        "trace_id": trace_id
    }
    produce_message(app_config['events']['topic'], json.dumps(msg))

    logger.info(f"Produced physical_activity event to Kafka with trace id {trace_id}")
    return NoContent, 201

def update_health_metric(body):
    trace_id = str(uuid.uuid4())
    logger.info(f"Received event health_metric request with a trace id of {trace_id}")
    global event_data
    body['trace_id'] = trace_id
    event_data["health_metric_count"] += 1
    event_data["last_five_health_metrics"].insert(0, {
        "received_timestamp": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        "msg_data": body
    })
    event_data["last_five_health_metrics"] = event_data["last_five_health_metrics"][:5]

    # Produce message to Kafkas
    msg = {
        "type": "health_metric",
        "datetime": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        "payload": body,
        "trace_id": trace_id
    }
    produce_message(app_config['events']['topic'], json.dumps(msg))

    logger.info(f"Produced health_metric event to Kafka with trace id {trace_id}")
    return NoContent, 201

app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("openapi.yml", strict_validation=True, validate_responses=True)

if __name__ == "__main__":
    app.run(port=8080)
