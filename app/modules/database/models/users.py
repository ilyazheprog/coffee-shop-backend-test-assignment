from sqlalchemy import (
    BIGINT,
    BOOLEAN,
    VARCHAR,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    func,
)
from sqlalchemy.orm import relationship

from ..core import Base


class User(Base):
    __tablename__ = "users"

    id = Column(BIGINT, primary_key=True)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False)

    username = Column(VARCHAR(33), unique=True, nullable=True)

    role = relationship("Role")
