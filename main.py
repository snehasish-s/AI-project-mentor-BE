import os
from datetime import datetime

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, Response, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import case, func, select, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from database import engine, get_db
from models import AIInteraction, Project, Task
from ollama_service import OllamaServiceError, generate_ai_response
from schemas import (
    AIInteractionCreate,
    AIInteractionResponse,
    AIPlanRequest,
    ProjectCreate,
    ProjectResponse,
    ProjectUpdate,
    TaskCreate,
    TaskResponse,
    TaskStatusUpdate,
    TaskUpdate,
)


# ---------------------------------------------------------
# Environment configuration
# ---------------------------------------------------------

load_dotenv()


# ---------------------------------------------------------
# FastAPI application
# ---------------------------------------------------------

app = FastAPI(
    title="AI Project Mentor API",
    description=(
        "FastAPI backend for managing projects, tasks, "
        "dashboard statistics and AI mentor interactions."
    ),
    version="1.0.0",
)


# ---------------------------------------------------------
# CORS configuration
# ---------------------------------------------------------

frontend_origins = os.getenv(
    "FRONTEND_ORIGINS",
    "http://localhost:5173,http://127.0.0.1:5173",
)

allowed_origins = [
    origin.strip()
    for origin in frontend_origins.split(",")
    if origin.strip()
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------
# General endpoints
# ---------------------------------------------------------

@app.get(
    "/",
    tags=["General"],
)
def root():
    return {
        "message": "Welcome to AI Project Mentor API",
        "version": "1.0.0",
        "documentation": "/docs",
        "health": "/api/health",
    }


@app.get(
    "/api/health",
    tags=["Health"],
)
def health_check():
    try:
        with engine.connect() as connection:
            database_name = connection.execute(
                text("SELECT DB_NAME()")
            ).scalar()

        return {
            "status": "healthy",
            "backend": "connected",
            "database": "connected",
            "database_name": database_name,
        }

    except SQLAlchemyError as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                "Backend is running, "
                "but SQL Server is unavailable."
            ),
        ) from error


# ---------------------------------------------------------
# Dashboard endpoint
# ---------------------------------------------------------

# @app.get(
#     "/api/dashboard",
#     response_model=DashboardResponse,
#     tags=["Dashboard"],
# )
# def get_dashboard(
#     db: Session = Depends(get_db),
# ):
#     try:
#         total_projects = db.scalar(
#             select(
#                 func.count(Project.project_id)
#             )
#         ) or 0

#         total_tasks = db.scalar(
#             select(
#                 func.count(Task.task_id)
#             )
#         ) or 0

#         pending_tasks = db.scalar(
#             select(
#                 func.count(Task.task_id)
#             ).where(
#                 Task.status == "Pending"
#             )
#         ) or 0

#         in_progress_tasks = db.scalar(
#             select(
#                 func.count(Task.task_id)
#             ).where(
#                 Task.status == "In Progress"
#             )
#         ) or 0

#         completed_tasks = db.scalar(
#             select(
#                 func.count(Task.task_id)
#             ).where(
#                 Task.status == "Completed"
#             )
#         ) or 0

#         progress_statement = (
#             select(
#                 Project.project_id,
#                 Project.project_name,
#                 Project.technology_stack,
#                 func.count(
#                     Task.task_id
#                 ).label("total_tasks"),
#                 func.sum(
#                     case(
#                         (
#                             Task.status == "Completed",
#                             1,
#                         ),
#                         else_=0,
#                     )
#                 ).label("completed_tasks"),
#             )
#             .outerjoin(
#                 Task,
#                 Project.project_id == Task.project_id,
#             )
#             .group_by(
#                 Project.project_id,
#                 Project.project_name,
#                 Project.technology_stack,
#             )
#             .order_by(
#                 Project.project_id
#             )
#         )

#         progress_rows = db.execute(
#             progress_statement
#         ).all()

#         project_progress = []

#         for row in progress_rows:
#             project_total = row.total_tasks or 0
#             project_completed = row.completed_tasks or 0

#             if project_total == 0:
#                 progress_percentage = 0.0

#             else:
#                 progress_percentage = round(
#                     (
#                         project_completed
#                         / project_total
#                     )
#                     * 100,
#                     2,
#                 )

#             project_progress.append(
#                 {
#                     "project_id": row.project_id,
#                     "project_name": row.project_name,
#                     "technology_stack": (
#                         row.technology_stack
#                     ),
#                     "total_tasks": project_total,
#                     "completed_tasks": project_completed,
#                     "progress_percentage": (
#                         progress_percentage
#                     ),
#                 }
#             )

#         recent_tasks_statement = (
#             select(
#                 Task.task_id,
#                 Task.title,
#                 Task.project_id,
#                 Project.project_name,
#                 Task.priority,
#                 Task.status,
#                 Task.updated_at,
#                 Task.created_at,
#             )
#             .join(
#                 Project,
#                 Task.project_id == Project.project_id,
#             )
#             .order_by(
#                 func.coalesce(
#                     Task.updated_at,
#                     Task.created_at,
#                 ).desc()
#             )
#             .limit(5)
#         )

#         recent_task_rows = db.execute(
#             recent_tasks_statement
#         ).all()

#         recent_tasks = []

#         for row in recent_task_rows:
#             recent_tasks.append(
#                 {
#                     "task_id": row.task_id,
#                     "title": row.title,
#                     "project_id": row.project_id,
#                     "project_name": row.project_name,
#                     "priority": row.priority,
#                     "status": row.status,
#                     "updated_at": (
#                         row.updated_at
#                         or row.created_at
#                     ),
#                 }
#             )

#         return {
#             "total_projects": total_projects,
#             "total_tasks": total_tasks,
#             "pending_tasks": pending_tasks,
#             "in_progress_tasks": in_progress_tasks,
#             "completed_tasks": completed_tasks,
#             "project_progress": project_progress,
#             "recent_tasks": recent_tasks,
#         }

#     except SQLAlchemyError as error:
#         raise HTTPException(
#             status_code=(
#                 status.HTTP_500_INTERNAL_SERVER_ERROR
#             ),
#             detail=(
#                 "Dashboard data could not be retrieved."
#             ),
#         ) from error


# ---------------------------------------------------------
# Project endpoints
# ---------------------------------------------------------

@app.post(
    "/api/projects",
    response_model=ProjectResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Projects"],
)
def create_project(
    project_data: ProjectCreate,
    db: Session = Depends(get_db),
):
    new_project = Project(
        project_name=project_data.project_name,
        description=project_data.description,
        technology_stack=(
            project_data.technology_stack
        ),
    )

    try:
        db.add(new_project)
        db.commit()
        db.refresh(new_project)

        return new_project

    except SQLAlchemyError as error:
        db.rollback()

        raise HTTPException(
            status_code=(
                status.HTTP_500_INTERNAL_SERVER_ERROR
            ),
            detail="Project could not be created.",
        ) from error


@app.get(
    "/api/projects",
    response_model=list[ProjectResponse],
    tags=["Projects"],
)
def get_projects(
    db: Session = Depends(get_db),
):
    try:
        statement = select(
            Project
        ).order_by(
            Project.project_id
        )

        projects = db.scalars(
            statement
        ).all()

        return projects

    except SQLAlchemyError as error:
        raise HTTPException(
            status_code=(
                status.HTTP_500_INTERNAL_SERVER_ERROR
            ),
            detail="Projects could not be retrieved.",
        ) from error


@app.get(
    "/api/projects/{project_id}",
    response_model=ProjectResponse,
    tags=["Projects"],
)
def get_project(
    project_id: int,
    db: Session = Depends(get_db),
):
    project = db.get(
        Project,
        project_id,
    )

    if project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(
                f"Project with ID {project_id} "
                "was not found."
            ),
        )

    return project


@app.put(
    "/api/projects/{project_id}",
    response_model=ProjectResponse,
    tags=["Projects"],
)
def update_project(
    project_id: int,
    project_data: ProjectUpdate,
    db: Session = Depends(get_db),
):
    project = db.get(
        Project,
        project_id,
    )

    if project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(
                f"Project with ID {project_id} "
                "was not found."
            ),
        )

    project.project_name = (
        project_data.project_name
    )

    project.description = (
        project_data.description
    )

    project.technology_stack = (
        project_data.technology_stack
    )

    try:
        db.commit()
        db.refresh(project)

        return project

    except SQLAlchemyError as error:
        db.rollback()

        raise HTTPException(
            status_code=(
                status.HTTP_500_INTERNAL_SERVER_ERROR
            ),
            detail="Project could not be updated.",
        ) from error


@app.delete(
    "/api/projects/{project_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Projects"],
)
def delete_project(
    project_id: int,
    db: Session = Depends(get_db),
):
    project = db.get(
        Project,
        project_id,
    )

    if project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(
                f"Project with ID {project_id} "
                "was not found."
            ),
        )

    try:
        db.delete(project)
        db.commit()

        return Response(
            status_code=(
                status.HTTP_204_NO_CONTENT
            )
        )

    except SQLAlchemyError as error:
        db.rollback()

        raise HTTPException(
            status_code=(
                status.HTTP_500_INTERNAL_SERVER_ERROR
            ),
            detail="Project could not be deleted.",
        ) from error


# ---------------------------------------------------------
# Task endpoints
# ---------------------------------------------------------

@app.post(
    "/api/tasks",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Tasks"],
)
def create_task(
    task_data: TaskCreate,
    db: Session = Depends(get_db),
):
    project = db.get(
        Project,
        task_data.project_id,
    )

    if project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(
                f"Project with ID "
                f"{task_data.project_id} "
                "was not found."
            ),
        )

    new_task = Task(
        project_id=task_data.project_id,
        title=task_data.title,
        description=task_data.description,
        priority=task_data.priority,
        status=task_data.status,
        ai_generated=task_data.ai_generated,
    )

    try:
        db.add(new_task)
        db.commit()
        db.refresh(new_task)

        return new_task

    except SQLAlchemyError as error:
        db.rollback()

        raise HTTPException(
            status_code=(
                status.HTTP_500_INTERNAL_SERVER_ERROR
            ),
            detail="Task could not be created.",
        ) from error


@app.get(
    "/api/tasks",
    response_model=list[TaskResponse],
    tags=["Tasks"],
)
def get_tasks(
    db: Session = Depends(get_db),
):
    try:
        statement = select(
            Task
        ).order_by(
            Task.task_id
        )

        tasks = db.scalars(
            statement
        ).all()

        return tasks

    except SQLAlchemyError as error:
        raise HTTPException(
            status_code=(
                status.HTTP_500_INTERNAL_SERVER_ERROR
            ),
            detail="Tasks could not be retrieved.",
        ) from error


@app.get(
    "/api/tasks/{task_id}",
    response_model=TaskResponse,
    tags=["Tasks"],
)
def get_task(
    task_id: int,
    db: Session = Depends(get_db),
):
    task = db.get(
        Task,
        task_id,
    )

    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(
                f"Task with ID {task_id} "
                "was not found."
            ),
        )

    return task


@app.put(
    "/api/tasks/{task_id}",
    response_model=TaskResponse,
    tags=["Tasks"],
)
def update_task(
    task_id: int,
    task_data: TaskUpdate,
    db: Session = Depends(get_db),
):
    task = db.get(
        Task,
        task_id,
    )

    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(
                f"Task with ID {task_id} "
                "was not found."
            ),
        )

    project = db.get(
        Project,
        task_data.project_id,
    )

    if project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(
                f"Project with ID "
                f"{task_data.project_id} "
                "was not found."
            ),
        )

    task.project_id = task_data.project_id
    task.title = task_data.title
    task.description = task_data.description
    task.priority = task_data.priority
    task.status = task_data.status
    task.ai_generated = task_data.ai_generated
    task.updated_at = datetime.now()

    try:
        db.commit()
        db.refresh(task)

        return task

    except SQLAlchemyError as error:
        db.rollback()

        raise HTTPException(
            status_code=(
                status.HTTP_500_INTERNAL_SERVER_ERROR
            ),
            detail="Task could not be updated.",
        ) from error


@app.patch(
    "/api/tasks/{task_id}/status",
    response_model=TaskResponse,
    tags=["Tasks"],
)
def update_task_status(
    task_id: int,
    status_data: TaskStatusUpdate,
    db: Session = Depends(get_db),
):
    task = db.get(
        Task,
        task_id,
    )

    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(
                f"Task with ID {task_id} "
                "was not found."
            ),
        )

    task.status = status_data.status
    task.updated_at = datetime.now()

    try:
        db.commit()
        db.refresh(task)

        return task

    except SQLAlchemyError as error:
        db.rollback()

        raise HTTPException(
            status_code=(
                status.HTTP_500_INTERNAL_SERVER_ERROR
            ),
            detail=(
                "Task status could not be updated."
            ),
        ) from error


@app.delete(
    "/api/tasks/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Tasks"],
)
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
):
    task = db.get(
        Task,
        task_id,
    )

    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(
                f"Task with ID {task_id} "
                "was not found."
            ),
        )

    try:
        db.delete(task)
        db.commit()

        return Response(
            status_code=(
                status.HTTP_204_NO_CONTENT
            )
        )

    except SQLAlchemyError as error:
        db.rollback()

        raise HTTPException(
            status_code=(
                status.HTTP_500_INTERNAL_SERVER_ERROR
            ),
            detail="Task could not be deleted.",
        ) from error


# ---------------------------------------------------------
# AI Mentor endpoints
# ---------------------------------------------------------

@app.get(
    "/api/ai/history",
    response_model=list[AIInteractionResponse],
    tags=["AI Mentor"],
)
def get_all_ai_history(
    db: Session = Depends(get_db),
):
    try:
        history_statement = (
            select(AIInteraction)
            .order_by(AIInteraction.created_at.desc())
        )
        return db.scalars(history_statement).all()

    except SQLAlchemyError as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="AI history could not be retrieved.",
        ) from error


@app.post(
    "/api/ai/history",
    response_model=AIInteractionResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["AI Mentor"],
)
def create_ai_history(
    interaction_data: AIInteractionCreate,
    db: Session = Depends(get_db),
):
    if db.get(Project, interaction_data.project_id) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(
                f"Project with ID {interaction_data.project_id} "
                "was not found."
            ),
        )

    interaction = AIInteraction(
        project_id=interaction_data.project_id,
        task_type=interaction_data.task_type,
        prompt=interaction_data.prompt,
        ai_response=interaction_data.ai_response,
        model_name=interaction_data.model_name,
    )

    try:
        db.add(interaction)
        db.commit()
        db.refresh(interaction)
        return interaction

    except SQLAlchemyError as error:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="AI interaction could not be saved.",
        ) from error


@app.delete(
    "/api/ai/history/{interaction_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["AI Mentor"],
)
def delete_ai_history(
    interaction_id: int,
    db: Session = Depends(get_db),
):
    interaction = db.get(AIInteraction, interaction_id)

    if interaction is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(
                f"AI interaction with ID {interaction_id} "
                "was not found."
            ),
        )

    try:
        db.delete(interaction)
        db.commit()
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    except SQLAlchemyError as error:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="AI interaction could not be deleted.",
        ) from error

@app.post(
    "/api/ai/plan",
    response_model=AIInteractionResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["AI Mentor"],
)
def generate_project_plan(
    request_data: AIPlanRequest,
    db: Session = Depends(get_db),
):
    project = db.get(
        Project,
        request_data.project_id,
    )

    if project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(
                f"Project with ID "
                f"{request_data.project_id} "
                "was not found."
            ),
        )

    task_statement = (
        select(Task)
        .where(
            Task.project_id
            == request_data.project_id
        )
        .order_by(
            Task.task_id
        )
    )

    existing_tasks = db.scalars(
        task_statement
    ).all()

    try:
        ai_result = generate_ai_response(
            project_name=project.project_name,
            project_description=(
                project.description
            ),
            technology_stack=(
                project.technology_stack
            ),
            existing_tasks=existing_tasks,
            task_type=request_data.task_type,
            user_prompt=request_data.prompt,
        )

    except OllamaServiceError as error:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(error),
        ) from error

    interaction = AIInteraction(
        project_id=project.project_id,
        task_type=request_data.task_type,
        prompt=request_data.prompt,
        ai_response=ai_result["answer"],
        model_name=ai_result["model"],
    )

    try:
        db.add(interaction)
        db.commit()
        db.refresh(interaction)

        return interaction

    except SQLAlchemyError as error:
        db.rollback()

        raise HTTPException(
            status_code=(
                status.HTTP_500_INTERNAL_SERVER_ERROR
            ),
            detail=(
                "The AI response was generated, "
                "but it could not be saved."
            ),
        ) from error


@app.get(
    "/api/ai/history/{project_id}",
    response_model=list[AIInteractionResponse],
    tags=["AI Mentor"],
)
def get_ai_history(
    project_id: int,
    db: Session = Depends(get_db),
):
    project = db.get(
        Project,
        project_id,
    )

    if project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(
                f"Project with ID {project_id} "
                "was not found."
            ),
        )

    try:
        history_statement = (
            select(AIInteraction)
            .where(
                AIInteraction.project_id
                == project_id
            )
            .order_by(
                AIInteraction.created_at.desc()
            )
        )

        interactions = db.scalars(
            history_statement
        ).all()

        return interactions

    except SQLAlchemyError as error:
        raise HTTPException(
            status_code=(
                status.HTTP_500_INTERNAL_SERVER_ERROR
            ),
            detail=(
                "AI history could not be retrieved."
            ),
        ) from error