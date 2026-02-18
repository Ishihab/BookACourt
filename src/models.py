from src.core.db import Base
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Float, String, Integer, UniqueConstraint, Index, CheckConstraint, and_, or_, TIME, ForeignKey, DateTime, Boolean, func, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID, JSONB
import uuid
from datetime import time, datetime
from sqlalchemy.orm import relationship
from datetime import datetime, timezone, timedelta


class Users(Base):
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(UUID, default=uuid.uuid4, primary_key=True)
    full_name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(100), unique=True)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)
    phone_number: Mapped[str | None] = mapped_column(String, unique=True, index=True)
    profile_image_key: Mapped[str | None] = mapped_column(String)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))   
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    bookings: Mapped[list["Bookings"]] = relationship("Bookings", back_populates="user")





class Facilities(Base):
    __tablename__ = "facilities"

    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
    name: Mapped[str | None] = mapped_column(String(255))
    state: Mapped[str] = mapped_column(String(100))
    city: Mapped[str] = mapped_column(String(100))
    address: Mapped[str] = mapped_column(String(255))
    open_at: Mapped[ time | None] = mapped_column(TIME)
    close_at: Mapped[ time | None] = mapped_column(TIME)
    amenities: Mapped[dict | None] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True), onupdate=func.now())
    resources: Mapped[list["Resources"]] = relationship("Resources", back_populates="facility")


    __table_args__ = (
        UniqueConstraint('name', 'city', name='uix_facility_name_city'),
        Index('ix_facility_name_city_state', 'name', 'city', 'state'),
        UniqueConstraint('name', 'address', name='uix_name_address'),
        CheckConstraint(
        or_(
            and_(open_at.is_(None), close_at.is_(None)),
            and_(open_at.isnot(None), close_at.isnot(None))
        ),
        name="open_close_both_or_none" )
    )

class Resources(Base):
    __tablename__ = "resources"

    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
    facility_id: Mapped[uuid.UUID] = mapped_column(UUID, ForeignKey("facilities.id", ondelete="CASCADE"))
    name: Mapped[str] = mapped_column(String(100))
    description: Mapped[str | None] = mapped_column(String(255))
    price_per_hour: Mapped[int] = mapped_column(Integer)
    description: Mapped[str | None] = mapped_column(String(500))
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True), onupdate=func.now())
    bookings: Mapped[list["Bookings"]] = relationship("Bookings", back_populates="resource")
    facility = relationship("Facilities", back_populates="resources")
    __table_args__ = (
        UniqueConstraint('facility_id', 'name', name='uix_resource_facility_name'),
        Index('ix_resource_facility_name', 'facility_id', 'name'),
    )



class Bookings(Base):
    __tablename__ = "bookings"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    resource_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("resources.id"), index=True)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), index=True)
    start_time: Mapped[datetime] = mapped_column(DateTime, index=True)
    end_time: Mapped[datetime] = mapped_column(DateTime, index=True)
    total_price: Mapped[float] = mapped_column(Float)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True), onupdate=func.now())
    resource: Mapped["Resources"] = relationship("Resources", back_populates="bookings")
    user: Mapped["Users"] = relationship("Users", back_populates="bookings")
    __table_args__ = (
        Index('ix_booking_resource_start_end', 'resource_id', 'start_time', 'end_time'),
    )






