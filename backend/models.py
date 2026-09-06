from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey, Boolean
from .database import Base

class User(Base):
    __tablename__="users"
    id=Column(Integer, primary_key=True)
    name=Column(String, nullable=False)
    email=Column(String, unique=True, index=True, nullable=False)
    password_hash=Column(String, nullable=False)
    is_admin=Column(Boolean, default=False)

class Item(Base):
    __tablename__="items"
    id=Column(Integer, primary_key=True, index=True)
    user_id=Column(Integer, ForeignKey("users.id"), nullable=True)
    item_type=Column(String, nullable=False)
    title=Column(String, nullable=False)
    description=Column(Text, nullable=False)
    location=Column(String, nullable=False)
    category=Column(String, default="Other")
    contact=Column(String)
    image_path=Column(String)
    status=Column(String, default="active")
    ai_summary=Column(Text)
    ai_keywords=Column(Text)
    created_at=Column(DateTime, default=datetime.utcnow)

class Match(Base):
    __tablename__="matches"
    id=Column(Integer, primary_key=True)
    lost_item_id=Column(Integer, ForeignKey("items.id"), nullable=False)
    found_item_id=Column(Integer, ForeignKey("items.id"), nullable=False)
    score=Column(Float, nullable=False)
    explanation=Column(Text)
    notified=Column(Boolean, default=False)
    created_at=Column(DateTime, default=datetime.utcnow)

class Claim(Base):
    __tablename__="claims"
    id=Column(Integer, primary_key=True)
    item_id=Column(Integer, ForeignKey("items.id"), nullable=False)
    claimant_user_id=Column(Integer, ForeignKey("users.id"), nullable=False)
    message=Column(Text)
    status=Column(String, default="pending")
    created_at=Column(DateTime, default=datetime.utcnow)
