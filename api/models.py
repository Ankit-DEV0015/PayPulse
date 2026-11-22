
from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import (
    String,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    JSON,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from api.database import Base


# --------------------------------------------------
# Utility Functions
# --------------------------------------------------

def utc_now():
    return datetime.now(timezone.utc)


# --------------------------------------------------
# User Model
# --------------------------------------------------

class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
    )

    full_name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    business_name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False,
    )

    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=False,
    )

    sessions: Mapped[list["LoginSession"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )


# --------------------------------------------------
# Login Session Model
# --------------------------------------------------

class LoginSession(Base):
    __tablename__ = "login_sessions"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
    )

    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    token_hash: Mapped[str] = mapped_column(
        String(64),
        unique=True,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=False,
    )

    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    user: Mapped["User"] = relationship(
        back_populates="sessions",
    )


Index(
    "ix_login_sessions_user_id",
    LoginSession.user_id,
)


# --------------------------------------------------
# Uploaded Dataset Model
# --------------------------------------------------

class UploadedDataset(Base):
    __tablename__ = "uploaded_datasets"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
    )

    # The user who uploaded the dataset
    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Original uploaded filename
    filename: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    # File format: csv, xlsx, or xls
    file_type: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
    )

    # Number of rows in the uploaded dataset
    row_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    # Detected column names
    columns: Mapped[list] = mapped_column(
        JSON,
        nullable=False,
        default=list,
    )

    # Upload timestamp
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=False,
    )

    user: Mapped["User"] = relationship()


# --------------------------------------------------
# Database Indexes
# --------------------------------------------------

Index(
    "ix_uploaded_datasets_created_at",
    UploadedDataset.created_at,
)
