from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import (
    Column,
    String,
    Boolean,
    Integer,
    Text,
    DateTime,
    UUID,
    ForeignKey,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
import uuid
import os

# Database URL - using asyncpg for async operations
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://expert_user:expert_password123@localhost:5432/expert_sure",
)

# Create async engine
engine = create_async_engine(DATABASE_URL, echo=True)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

Base = declarative_base()


class Project(Base):
    __tablename__ = "projects"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    auto_mode = Column(Boolean, default=False)
    status = Column(String(50), default="initialized")
    data_source_path = Column(Text)
    schema_path = Column(Text)
    template_path = Column(Text)
    available_fields = Column(JSONB)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class Slide(Base):
    __tablename__ = "slides"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(
        UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
    )
    slide_number = Column(Integer, nullable=False)
    slide_title = Column(String(255), nullable=False)
    status = Column(String(50), default="pending")
    agent_selected_fields = Column(JSONB)
    user_modified_fields = Column(JSONB)
    final_fields = Column(JSONB)
    analysis_result = Column(JSONB)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    __table_args__ = (
        UniqueConstraint("project_id", "slide_number", name="unique_project_slide"),
    )


class ProjectOutput(Base):
    __tablename__ = "project_outputs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(
        UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
    )
    output_type = Column(String(50), nullable=False)
    file_path = Column(Text)
    content = Column(JSONB)
    generated_at = Column(DateTime(timezone=True), server_default=func.now())


class WebSocketSession(Base):
    __tablename__ = "websocket_sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(
        UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
    )
    session_id = Column(String(255), unique=True, nullable=False)
    is_active = Column(Boolean, default=True)
    connected_at = Column(DateTime(timezone=True), server_default=func.now())
    disconnected_at = Column(DateTime(timezone=True))


# Database dependency
async def get_db():
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()


# Initialize database
async def init_database():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
