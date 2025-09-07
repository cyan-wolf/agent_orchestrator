from sqlalchemy import Column, Integer, Text, UUID
from database.database import Base
import uuid

# class EventTable(Base):
#     __tablename__ = "events"

#     id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
#     name = Column(Text)
#     start_time = Column(Integer)
#     end_time = Column(Integer)
#     importance = Column(Text)
    