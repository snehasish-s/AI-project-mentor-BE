from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    NVARCHAR,
    text,
)
from sqlalchemy.orm import declarative_base, relationship


Base = declarative_base()


class Project(Base):
    __tablename__ = "Projects"
    __table_args__ = {"schema": "dbo"}

    project_id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    project_name = Column(
        NVARCHAR(150),
        nullable=False,
    )

    description = Column(
        NVARCHAR(None),
        nullable=False,
    )

    technology_stack = Column(
        NVARCHAR(300),
        nullable=False,
    )

    created_at = Column(
        DateTime,
        nullable=False,
        server_default=text("SYSDATETIME()"),
    )

    tasks = relationship(
        "Task",
        back_populates="project",
        cascade="all, delete-orphan",
    )

    ai_interactions = relationship(
        "AIInteraction",
        back_populates="project",
        cascade="all, delete-orphan",
    )


class Task(Base):
    __tablename__ = "Tasks"
    __table_args__ = {"schema": "dbo"}

    task_id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    project_id = Column(
        Integer,
        ForeignKey(
            "dbo.Projects.project_id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    title = Column(
        NVARCHAR(200),
        nullable=False,
    )

    description = Column(
        NVARCHAR(None),
        nullable=False,
    )

    priority = Column(
        NVARCHAR(20),
        nullable=False,
        server_default=text("'Medium'"),
    )

    status = Column(
        NVARCHAR(30),
        nullable=False,
        server_default=text("'Pending'"),
    )

    ai_generated = Column(
        Boolean,
        nullable=False,
        server_default=text("0"),
    )

    created_at = Column(
        DateTime,
        nullable=False,
        server_default=text("SYSDATETIME()"),
    )

    updated_at = Column(
        DateTime,
        nullable=True,
    )

    project = relationship(
        "Project",
        back_populates="tasks",
    )


class AIInteraction(Base):
    __tablename__ = "AIInteractions"
    __table_args__ = {"schema": "dbo"}

    interaction_id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    project_id = Column(
        Integer,
        ForeignKey(
            "dbo.Projects.project_id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    task_type = Column(
        NVARCHAR(100),
        nullable=False,
    )

    prompt = Column(
        NVARCHAR(None),
        nullable=False,
    )

    ai_response = Column(
        NVARCHAR(None),
        nullable=False,
    )

    model_name = Column(
        NVARCHAR(100),
        nullable=True,
    )

    created_at = Column(
        DateTime,
        nullable=False,
        server_default=text("SYSDATETIME()"),
    )

    project = relationship(
        "Project",
        back_populates="ai_interactions",
    )