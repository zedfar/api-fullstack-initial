from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid
from app.database import Base

class Category(Base):
    __tablename__ = "categories"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 🔹 Foreign key ke tabel users
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    # 🔹 Relationship ke model User (pastikan kamu punya model User)
    creator = relationship("User", back_populates="category", lazy="selectin")
    products = relationship("Product", back_populates="category", lazy="selectin")

