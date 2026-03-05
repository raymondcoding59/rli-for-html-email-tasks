from sqlalchemy import Column, Integer, Text, DateTime
from datetime import datetime
from database import Base

class EmailSample(Base):
    __tablename__ = "email_samples"

    id = Column(Integer, primary_key=True, index=True)
    html_code = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    
    
    
class DeveloperStyle(Base):
    __tablename__ = "developer_styles"

    id = Column(Integer, primary_key=True, index=True)
    style_json = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    
    
class EmailEmbedding(Base):
    __tablename__ = "email_embeddings"

    id = Column(Integer, primary_key=True, index=True)
    embedding = Column(Text)
    html_code = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)