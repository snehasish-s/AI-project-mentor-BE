import os

from dotenv import load_dotenv
from ollama import Client


load_dotenv()


class OllamaServiceError(Exception):
    pass


def generate_ai_response(
    project_name,
    project_description,
    technology_stack,
    existing_tasks,
    task_type,
    user_prompt,
):
    api_key = os.getenv("OLLAMA_API_KEY")
    host = os.getenv("OLLAMA_HOST", "https://ollama.com")
    model = os.getenv("OLLAMA_MODEL", "gpt-oss:20b")
    think_level = os.getenv("OLLAMA_THINK_LEVEL", "low")

    if not api_key:
        raise OllamaServiceError(
            "OLLAMA_API_KEY is missing."
        )

    task_context = "No tasks have been created yet."

    if existing_tasks:
        task_lines = []

        for task in existing_tasks:
            task_lines.append(
                f"- {task.title} | "
                f"Priority: {task.priority} | "
                f"Status: {task.status}"
            )

        task_context = "\n".join(task_lines)

    system_message = """
You are an experienced full-stack developer and project mentor.

Your job is to guide beginner software-development students.

Provide practical, technically correct and concise recommendations.

Do not expose hidden reasoning or internal chain-of-thought.

Return only the final recommendation using these headings:

1. Requirement Understanding
2. Frontend Tasks
3. Backend Tasks
4. Database Tasks
5. Testing Steps
6. Possible Blockers
7. Recommended Next Action

Use clear numbered points under every relevant heading.
"""

    user_message = f"""
Project name:
{project_name}

Project description:
{project_description}

Technology stack:
{technology_stack}

Requested AI task:
{task_type}

Existing project tasks:
{task_context}

Student requirement or question:
{user_prompt}

Generate a recommendation that matches the project,
existing tasks and requested AI task.
"""

    try:
        client = Client(
            host=host,
            headers={
                "Authorization": f"Bearer {api_key}"
            },
        )

        response = client.chat(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": system_message,
                },
                {
                    "role": "user",
                    "content": user_message,
                },
            ],
            think=think_level,
            stream=False,
        )

        answer = response.message.content

        if not answer or not answer.strip():
            raise OllamaServiceError(
                "Ollama returned an empty response."
            )

        return {
            "answer": answer.strip(),
            "model": model,
        }

    except OllamaServiceError:
        raise

    except Exception as error:
        raise OllamaServiceError(
            f"Ollama request failed: {error}"
        ) from error