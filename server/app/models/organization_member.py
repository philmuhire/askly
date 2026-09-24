from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.base import Base


class OrganizationMember(Base):
    __tablename__ = "organization_members"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True)
    organization_id = Column(
        UUID(as_uuid=True), ForeignKey("organizations.id"), primary_key=True
    )
    role = Column(String, default="member", nullable=False)
    joined_at = Column(DateTime, default=datetime.now, nullable=False)

    user = relationship("User", back_populates="memberships")
    organization = relationship("Organization", back_populates="memberships")