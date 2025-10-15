from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Numeric, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid
from app.database import Base

class Product(Base):
    __tablename__ = "products"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(String(255), nullable=True)
    image_url = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
    
    price = Column(Numeric(10, 2), nullable=False, default=0.00)  # 🔹 Harga dengan 2 desimal
    stock = Column(Integer, nullable=False, default=0)            # 🔹 Jumlah stok
    low_stock_threshold = Column(Integer, nullable=False, default=10) # 🔹 Batas stok rendah
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 🔹 Relasi ke User
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    creator = relationship("User", back_populates="products", lazy="selectin")
    
    # 🔹 Relasi ke Category
    category_id = Column(UUID(as_uuid=True), ForeignKey("categories.id"), nullable=False)
    category = relationship("Category", back_populates="products", lazy="selectin")
    
