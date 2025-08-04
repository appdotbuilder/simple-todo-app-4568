from datetime import datetime
from typing import Optional
from sqlmodel import select, desc
from app.database import get_session
from app.models import Todo, TodoCreate, TodoUpdate, TodoResponse


class TodoService:
    """Service layer for todo operations."""

    @staticmethod
    def get_all_todos() -> list[TodoResponse]:
        """Get all todos ordered by creation date (newest first)."""
        with get_session() as session:
            statement = select(Todo).order_by(desc(Todo.created_at))
            todos = session.exec(statement).all()
            return [TodoResponse.from_todo(todo) for todo in todos]

    @staticmethod
    def get_todo_by_id(todo_id: int) -> Optional[TodoResponse]:
        """Get a specific todo by ID."""
        with get_session() as session:
            todo = session.get(Todo, todo_id)
            if todo is None:
                return None
            return TodoResponse.from_todo(todo)

    @staticmethod
    def create_todo(todo_data: TodoCreate) -> TodoResponse:
        """Create a new todo."""
        with get_session() as session:
            todo = Todo(
                title=todo_data.title,
                description=todo_data.description,
                completed=False,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )
            session.add(todo)
            session.commit()
            session.refresh(todo)
            return TodoResponse.from_todo(todo)

    @staticmethod
    def update_todo(todo_id: int, todo_data: TodoUpdate) -> Optional[TodoResponse]:
        """Update an existing todo."""
        with get_session() as session:
            todo = session.get(Todo, todo_id)
            if todo is None:
                return None

            # Update only provided fields
            if todo_data.title is not None:
                todo.title = todo_data.title
            if todo_data.description is not None:
                todo.description = todo_data.description
            if todo_data.completed is not None:
                todo.completed = todo_data.completed

            todo.updated_at = datetime.utcnow()
            session.add(todo)
            session.commit()
            session.refresh(todo)
            return TodoResponse.from_todo(todo)

    @staticmethod
    def toggle_todo_completion(todo_id: int) -> Optional[TodoResponse]:
        """Toggle the completion status of a todo."""
        with get_session() as session:
            todo = session.get(Todo, todo_id)
            if todo is None:
                return None

            todo.completed = not todo.completed
            todo.updated_at = datetime.utcnow()
            session.add(todo)
            session.commit()
            session.refresh(todo)
            return TodoResponse.from_todo(todo)

    @staticmethod
    def delete_todo(todo_id: int) -> bool:
        """Delete a todo by ID. Returns True if deleted, False if not found."""
        with get_session() as session:
            todo = session.get(Todo, todo_id)
            if todo is None:
                return False

            session.delete(todo)
            session.commit()
            return True

    @staticmethod
    def get_stats() -> dict[str, int]:
        """Get basic statistics about todos."""
        with get_session() as session:
            all_todos = session.exec(select(Todo)).all()
            total = len(all_todos)
            completed = sum(1 for todo in all_todos if todo.completed)
            pending = total - completed

            return {"total": total, "completed": completed, "pending": pending}
