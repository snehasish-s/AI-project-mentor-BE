from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


PriorityValue = Literal[
    "Low",
    "Medium",
    "High",
]

StatusValue = Literal[
    "Pending",
    "In Progress",
    "Completed",
]
AITaskType = Literal[
    "Generate Project Plan",
    "Break Requirement into Tasks",
    "Recommend Next Task",
    "Identify Project Blockers",
    "Explain Implementation",
    "Generate Testing Checklist",
]

# ---------------------------------------------------------
# Project schemas
# ---------------------------------------------------------

class ProjectBase(BaseModel):
    project_name: str = Field(
        min_length=2,
        max_length=150,
    )

    description: str = Field(
        min_length=5,
    )

    technology_stack: str = Field(
        min_length=2,
        max_length=300,
    )


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(ProjectBase):
    pass


class ProjectResponse(ProjectBase):
    model_config = ConfigDict(from_attributes=True)

    project_id: int
    created_at: datetime


# ---------------------------------------------------------
# Task schemas
# ---------------------------------------------------------

class TaskBase(BaseModel):
    project_id: int = Field(gt=0)

    title: str = Field(
        min_length=2,
        max_length=200,
    )

    description: str = Field(
        min_length=5,
    )

    priority: PriorityValue = "Medium"
    status: StatusValue = "Pending"
    ai_generated: bool = False


class TaskCreate(TaskBase):
    pass


class TaskUpdate(TaskBase):
    pass


class TaskStatusUpdate(BaseModel):
    status: StatusValue


class TaskResponse(TaskBase):
    model_config = ConfigDict(from_attributes=True)

    task_id: int
    created_at: datetime
    updated_at: datetime | None = None


# ---------------------------------------------------------
# AI interaction schemas
# ---------------------------------------------------------

class AIPlanRequest(BaseModel):
    project_id: int = Field(gt=0)

    task_type: AITaskType

    prompt: str = Field(
        min_length=5,
        max_length=5000,
    )

    prompt: str = Field(
        min_length=5,
    )


class AIInteractionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    interaction_id: int
    project_id: int
    task_type: str
    prompt: str
    ai_response: str
    model_name: str | None = None
    created_at: datetime