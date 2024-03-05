import connexion
from connexion import NoContent
import yaml
import logging.config
import json
from pykafka import KafkaClient

# Load configuration files
with open('app_conf.yml', 'r') as f:
    app_config = yaml.safe_load(f)

with open('log_conf.yml', 'r') as f:
    log_config = yaml.safe_load(f)
    logging.config.dictConfig(log_config)

logger = logging.getLogger('basicLogger')

def get_activity_log(index):
    """Retrieve a specific activity log event by its index."""
    hostname = f"{app_config['events']['hostname']}:{app_config['events']['port']}"
    client = KafkaClient(hosts=hostname)
    topic = client.topics[str.encode(app_config['events']['topic'])]
    consumer = topic.get_simple_consumer(reset_offset_on_start=True, consumer_timeout_ms=1000)

    logger.info(f"Retrieving activity log at index {index}")
    count = 0
    for msg in consumer:
        if msg is not None:
            message = json.loads(msg.value.decode('utf-8'))
            # Ensure the message type matches and we're at the correct index
            if message['type'] == 'physical_activity':
                if count == index:
                    # Extract payload if your Kafka message contains one, or adjust as necessary
                    payload = message.get('payload', {})
                    # Validate or transform the payload as needed to match the OpenAPI spec
                    if 'activityType' not in payload:
                        logger.error("ActivityType missing in the message payload")
                        continue  # Skip to the next message or handle as needed
                    return payload, 200
                count += 1

    logger.error(f"Could not find activity log at index {index}")
    return {"message": "Not Found"}, 404

def get_health_metric_reading(index):
    """Retrieve a specific health metric event by its index."""
    hostname = f"{app_config['events']['hostname']}:{app_config['events']['port']}"
    client = KafkaClient(hosts=hostname)
    topic = client.topics[str.encode(app_config['events']['topic'])]
    consumer = topic.get_simple_consumer(reset_offset_on_start=True, consumer_timeout_ms=1000)

    logger.info(f"Retrieving health metric at index {index}")
    count = 0
    for msg in consumer:
        if msg is not None:
            message = json.loads(msg.value.decode('utf-8'))
            # Ensure the message type matches and we're at the correct index
            if message['type'] == 'health_metric':
                if count == index:
                    # Extract payload if your Kafka message contains one, or adjust as necessary
                    payload = message.get('payload', {})
                    # Validate or transform the payload as needed to match the OpenAPI spec
                    if 'metricType' not in payload or 'timestamp' not in payload or 'userId' not in payload or 'value' not in payload or 'trace_id' not in payload:
                        logger.error("Necessary fields missing in the message payload")
                        continue  # Skip to the next message or handle as needed
                    return payload, 200
                count += 1

    logger.error(f"Could not find health metric at index {index}")
    return {"message": "Not Found"}, 404

# Setup Connexion and add the API definition
app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("openapi.yml", strict_validation=True, validate_responses=True)

if __name__ == "__main__":
    app.run(port=8110)
