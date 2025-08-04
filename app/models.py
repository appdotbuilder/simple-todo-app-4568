from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional


# Persistent models (stored in database)
class Todo(SQLModel, table=True):
    __tablename__ = "todos"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(max_length=200)
    description: str = Field(default="", max_length=1000)
    completed: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


# Non-persistent schemas (for validation, forms, API requests/responses)
class TodoCreate(SQLModel, table=False):
    title: str = Field(max_length=200)
    description: str = Field(default="", max_length=1000)


class TodoUpdate(SQLModel, table=False):
    title: Optional[str] = Field(default=None, max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    completed: Optional[bool] = Field(default=None)


class TodoResponse(SQLModel, table=False):
    id: int
    title: str
    description: str
    completed: bool
    created_at: str
    updated_at: str

    @classmethod
    def from_todo(cls, todo: Todo) -> "TodoResponse":
        return cls(
            id=todo.id or 0,
            title=todo.title,
            description=todo.description,
            completed=todo.completed,
            created_at=todo.created_at.isoformat(),
            updated_at=todo.updated_at.isoformat(),
        )
