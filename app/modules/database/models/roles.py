from sqlalchemy import VARCHAR, Column, Integer

from ..core import Base


class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(VARCHAR(255), unique=True, nullable=False)
