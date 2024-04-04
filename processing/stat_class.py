from sqlalchemy import Column, Integer, String, DateTime
from base import Base
import datetime

class WorkoutStats(Base):
    __tablename__ = "statistics"
    id = Column(Integer, primary_key=True)
    num_activity_logs = Column(Integer, nullable=False)
    num_health_metrics = Column(Integer, nullable=False)
    average_duration = Column(Integer, nullable=False)
    average_heart_rate = Column(Integer, nullable=False)
    last_updated = Column(DateTime, nullable=False)

    def __init__(self, num_activity_logs, average_duration, num_health_metrics, average_heart_rate,last_updated):
        self.num_activity_logs=num_activity_logs
        self.average_duration=average_duration
        self.num_health_metrics=num_health_metrics
        self.average_heart_rate=average_heart_rate
        self.last_updated=last_updated

    def to_dict(self):    
        return {
            "id": self.id,
            "num_activity_logs": self.num_activity_logs,
            "average_duration": self.average_duration,
            "num_health_metrics":self.num_health_metrics,
            "average_heart_rate":self.average_heart_rate,
            "last_updated":self.last_updated.strftime('%Y-%m-%dT%H:%M:%S')
        }