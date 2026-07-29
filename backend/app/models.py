from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
import datetime
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    analyses = relationship("Analysis", back_populates="user", cascade="all, delete-orphan")


class Analysis(Base):
    __tablename__ = "analyses"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=False)
    url = Column(String, nullable=True)
    text = Column(String, nullable=False)
    summary = Column(String, nullable=False)
    
    # Original Bias Scores
    original_left = Column(Float, nullable=False)
    original_center = Column(Float, nullable=False)
    original_right = Column(Float, nullable=False)
    
    # Debiased Content
    debiased_text = Column(String, nullable=False)
    
    # Debiased Bias Scores
    debiased_left = Column(Float, nullable=False)
    debiased_center = Column(Float, nullable=False)
    debiased_right = Column(Float, nullable=False)
    
    bias_reduction = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", back_populates="analyses")
