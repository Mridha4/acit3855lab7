from sqlalchemy import Column, Integer, String, DateTime
from base import Base
import datetime
from pytz import timezone

class PhysicalActivityLog(Base):
    """ Physical Activity Log """

    __tablename__ = "physical_activity_log"

    id = Column(Integer, primary_key=True)
    user_id = Column(String(250), nullable=False)
    activity_type = Column(String(250), nullable=False)
    duration = Column(Integer, nullable=False)
    timestamp = Column(DateTime, nullable=False)
    trace_id = Column(String(36), nullable=False)
    date_created = Column(DateTime, default=datetime.datetime.now(timezone('PST')))

    def __init__(self, user_id, activity_type, duration, trace_id, timestamp):
        """ Initializes a physical activity log """
        self.user_id = user_id
        self.activity_type = activity_type
        self.duration = duration
        self.trace_id = trace_id
        self.timestamp = timestamp

    def to_dict(self):
        """ Dictionary Representation of a physical activity log """
        return {
            'id': self.id,
            'userId': self.user_id,
            'activityType': self.activity_type,
            'duration': self.duration,
            'timestamp': self.timestamp,
            'trace_id': self.trace_id,
            'dateCreated': self.date_created.strftime('%Y-%m-%dT%H:%M:%SZ') if self.date_created else None
        }
        return dict_representation