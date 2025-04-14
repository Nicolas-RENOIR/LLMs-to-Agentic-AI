from sqlalchemy import Column, Integer, String, Text
from database import Base

class Publication(Base):
    __tablename__ = "publications"

    id = Column(Integer, primary_key=True, index=True)
    id_campaign = Column(String(255))
    id_publication = Column(String(255))
    image_prompt = Column(Text)
    caption = Column(Text)
    image = Column(Text)  # stocké en base64