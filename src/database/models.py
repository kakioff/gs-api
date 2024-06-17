from sqlalchemy import Column, ForeignKey, Integer, String, Text, DateTime, func
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Role(Base):
    """
    |id|name|label|
    |--|----|-----|
    | 0|guest|游客|
    | 1|disable|禁用|
    | 2|subscribe|订阅者|
    | 3|user|普通用户|
    | 4|admin|管理员|
    | 5|super|超管|
    """

    __tablename__ = "roles"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), unique=True, nullable=False)
    label = Column(String(200), unique=True, nullable=False)
    users = relationship("User", back_populates="role")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(250))
    email = Column(String(250))
    phone = Column(String(20))
    hashed_password = Column(Text)
    role_id = Column(
        Integer, ForeignKey("roles.id"), nullable=False
    )  # Foreign key to roles table.

    role = relationship("Role", back_populates="users")
    tokens = relationship("Token", back_populates="user")

    def to_resp(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
            "role": (
                self.role.name if self.role else None
            ),  # Get the role name from the related Role object.
            "has_password": bool(self.hashed_password),  # Convert to boolean.
        }


class Token(Base):
    __tablename__ = "tokens"

    id = Column(Integer, primary_key=True, index=True)
    token = Column(Text, nullable=False)
    uid = Column(Integer, ForeignKey("users.id"), nullable=False)
    expires = Column(DateTime, nullable=False, comment="The expiration time.")
    created = Column(
        DateTime, default=func.now(), nullable=False, comment="The creation time"
    )
    ip = Column(String(45), nullable=False, comment="The IP address")
    user_agent = Column(String(250), nullable=False, comment="The user agent string")
    desc = Column(String(250), nullable=True, comment="A description")

    user = relationship("User", back_populates="tokens")  # The related User object.
