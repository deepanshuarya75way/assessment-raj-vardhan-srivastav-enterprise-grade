import uuid
from datetime import datetime, timezone
from sqlalchemy import DateTime, String, Text, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from ..database import Base

class AuditLog(Base):
  __tablename__ = "audit_logs"

  id:Mapped[uuid.UUID] = mapped_column(
    UUID(as_uuid=True), primary_key = True, default=uuid.uuid4
  )
  actor_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
  actor: Mapped[str]= mapped_column(String(255), nullable=False)
  action: Mapped[str]= mapped_column(String(length=255), nullable=False)
  resource: Mapped[str]= mapped_column(String(length=100), nullable=False)
  resource_id: Mapped[str]= mapped_column(
    String(255), nullable=False, default="info"
    )
  severity:Mapped[str] = mapped_column(
    String(20),
    nullable=False,
    default="info"
  )
  ip_address: Mapped[str | None] = mapped_column(String(45), nullable=True)
  details: Mapped[str | None] = mapped_column(Text, nullable=True)
  created_at: Mapped[datetime]= mapped_column(
    DateTime(timezone=True),
    nullable=False,
    default=lambda: datetime.now(timezone.utc),
    index=True
  )

  __table_args__ = (
      Index("ix_audit_logs_severity_created_at", "severity", "created_at")
  )





