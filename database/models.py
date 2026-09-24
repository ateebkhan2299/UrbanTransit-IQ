from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from database.db import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    audit_logs = relationship("AuditLog", back_populates="user")
    reports = relationship("SavedReport", back_populates="user")

class AuditLog(Base):
    __tablename__ = "audit_log"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    action = Column(String, nullable=False)
    details = Column(JSON, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="audit_logs")

class ModelRegistry(Base):
    __tablename__ = "model_registry"
    id = Column(Integer, primary_key=True, index=True)
    model_name = Column(String, nullable=False)
    pipeline = Column(String, nullable=False)  # spark or python
    version = Column(Integer, nullable=False)
    trained_date = Column(DateTime, default=datetime.utcnow)
    metrics = Column(JSON, nullable=True)
    file_path = Column(String, nullable=False)

class Recommendation(Base):
    __tablename__ = "recommendations"
    id = Column(Integer, primary_key=True, index=True)
    route_id = Column(String, index=True, nullable=False)
    action = Column(Text, nullable=False)
    reason = Column(JSON, nullable=False)
    priority = Column(String, nullable=False)
    generated_on = Column(DateTime, default=datetime.utcnow)
    status = Column(String, default="open") # open, acknowledged, implemented

class SavedReport(Base):
    __tablename__ = "saved_reports"
    id = Column(Integer, primary_key=True, index=True)
    report_type = Column(String, nullable=False)
    generated_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    format = Column(String, nullable=False)
    generated_at = Column(DateTime, default=datetime.utcnow)
    file_path = Column(String, nullable=False)
    
    user = relationship("User", back_populates="reports")
