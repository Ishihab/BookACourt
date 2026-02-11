from src.core.db import Base
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Integer, UniqueConstraint, Index, CheckConstraint, and_, or_, TIME, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID, JSONB
import uuid
from datetime import time, datetime
from sqlalchemy.orm import relationship
from datetime import datetime, timezone, timedelta


class Users(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True )
    full_name: Mapped[str | None] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(default=True)
    is_superuser: Mapped[bool] = mapped_column(default=False)
    hashed_password: Mapped[str] = mapped_column(String(255))
    refresh_tokens: Mapped[list["refreshTokens"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index('ix_is_active_email', 'is_active', 'email'),
    )


class Facilities(Base):
    __tablename__ = "facilities"

    id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True)
    name: Mapped[str | None] = mapped_column(String(255))
    state: Mapped[str] = mapped_column(String(100))
    city: Mapped[str] = mapped_column(String(100))
    address: Mapped[str] = mapped_column(String(255))
    open_at: Mapped[ time | None] = mapped_column(TIME)
    close_at: Mapped[ time | None] = mapped_column(TIME)
    amenities: Mapped[dict | None] = mapped_column(JSONB)

    __table_args__ = (
        UniqueConstraint('name', 'address', name='uix_name_address'),
        CheckConstraint(
        or_(
            and_(open_at.is_(None), close_at.is_(None)),
            and_(open_at.isnot(None), close_at.isnot(None))
        ),
        name="open_close_both_or_none" )
    )


class refreshTokens(Base):
    __tablename__ = "refresh_tokens"

    id: Mapped[UUID] = mapped_column(UUID, default=uuid.uuid4, primary_key=True)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), index=True)
    hashed_token: Mapped[str] = mapped_column(String, unique=True)
    expire_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc) + timedelta(days=7)) 
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    user: Mapped["Users"] = relationship(
        back_populates="refresh_tokens"
    )


