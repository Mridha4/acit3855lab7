from sqlalchemy import Column, Integer, String, DateTime
from base import Base
import datetime

class HealthMetricReading(Base):
    """ Health Metric Reading """

    __tablename__ = "health_metric_reading"

    id = Column(Integer, primary_key=True)
    user_id = Column(String(250), nullable=False)
    metric_type = Column(String(250), nullable=False)
    value = Column(Integer, nullable=False)
    timestamp = date_created = Column(DateTime, nullable=False)
    trace_id = Column(String(36), nullable=False)
    date_created = Column(DateTime, default=datetime.datetime.now(timezone('PST')))

    def __init__(self, user_id, metric_type, value, trace_id, timestamp):
        """ Initializes a health metric reading """
        self.user_id = user_id
        self.metric_type = metric_type
        self.value = value
        self.trace_id = trace_id
        self.timestamp = timestamp

    def to_dict(self):
        """ Dictionary Representation of a health metric reading """
        return {
            'id': self.id,
            'userId': self.user_id,
            'metricType': self.metric_type,
            'value': self.value,
            'timestamp': self.timestamp,
            'trace_id': self.trace_id,
            'dateCreated': self.date_created.strftime('%Y-%m-%dT%H:%M:%SZ') if self.date_created else None
        }
        return dict_representation
