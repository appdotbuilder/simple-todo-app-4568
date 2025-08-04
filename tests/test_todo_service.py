import pytest
from app.database import reset_db
from app.todo_service import TodoService
from app.models import TodoCreate, TodoUpdate


@pytest.fixture()
def clean_db():
    reset_db()
    yield
    reset_db()


def test_create_todo(clean_db):
    """Test creating a new todo."""
    todo_data = TodoCreate(title="Test Todo", description="Test description")
    result = TodoService.create_todo(todo_data)

    assert result.id > 0
    assert result.title == "Test Todo"
    assert result.description == "Test description"
    assert not result.completed
    assert result.created_at is not None
    assert result.updated_at is not None


def test_create_todo_minimal_data(clean_db):
    """Test creating a todo with minimal data."""
    todo_data = TodoCreate(title="Minimal Todo")
    result = TodoService.create_todo(todo_data)

    assert result.title == "Minimal Todo"
    assert result.description == ""
    assert not result.completed


def test_get_all_todos_empty(clean_db):
    """Test getting all todos when none exist."""
    todos = TodoService.get_all_todos()
    assert todos == []


def test_get_all_todos_with_data(clean_db):
    """Test getting all todos with existing data."""
    # Create test todos
    todo1 = TodoService.create_todo(TodoCreate(title="First Todo"))
    todo2 = TodoService.create_todo(TodoCreate(title="Second Todo"))

    todos = TodoService.get_all_todos()

    assert len(todos) == 2
    # Should be ordered by creation date (newest first)
    assert todos[0].id == todo2.id
    assert todos[1].id == todo1.id


def test_get_todo_by_id_existing(clean_db):
    """Test getting a todo by existing ID."""
    created_todo = TodoService.create_todo(TodoCreate(title="Test Todo"))

    result = TodoService.get_todo_by_id(created_todo.id)

    assert result is not None
    assert result.id == created_todo.id
    assert result.title == "Test Todo"


def test_get_todo_by_id_nonexistent(clean_db):
    """Test getting a todo by non-existent ID."""
    result = TodoService.get_todo_by_id(999)
    assert result is None


def test_update_todo_all_fields(clean_db):
    """Test updating all fields of a todo."""
    created_todo = TodoService.create_todo(TodoCreate(title="Original", description="Original desc"))

    update_data = TodoUpdate(title="Updated Title", description="Updated description", completed=True)
    result = TodoService.update_todo(created_todo.id, update_data)

    assert result is not None
    assert result.title == "Updated Title"
    assert result.description == "Updated description"
    assert result.completed
    assert result.updated_at != result.created_at


def test_update_todo_partial_fields(clean_db):
    """Test updating only some fields of a todo."""
    created_todo = TodoService.create_todo(TodoCreate(title="Original", description="Original desc"))

    update_data = TodoUpdate(completed=True)
    result = TodoService.update_todo(created_todo.id, update_data)

    assert result is not None
    assert result.title == "Original"  # Unchanged
    assert result.description == "Original desc"  # Unchanged
    assert result.completed  # Changed


def test_update_todo_nonexistent(clean_db):
    """Test updating a non-existent todo."""
    update_data = TodoUpdate(title="Updated")
    result = TodoService.update_todo(999, update_data)
    assert result is None


def test_toggle_todo_completion_uncompleted(clean_db):
    """Test toggling an uncompleted todo to completed."""
    created_todo = TodoService.create_todo(TodoCreate(title="Test Todo"))
    assert not created_todo.completed

    result = TodoService.toggle_todo_completion(created_todo.id)

    assert result is not None
    assert result.completed


def test_toggle_todo_completion_completed(clean_db):
    """Test toggling a completed todo to uncompleted."""
    created_todo = TodoService.create_todo(TodoCreate(title="Test Todo"))
    # First toggle to completed
    TodoService.toggle_todo_completion(created_todo.id)

    # Then toggle back to uncompleted
    result = TodoService.toggle_todo_completion(created_todo.id)

    assert result is not None
    assert not result.completed


def test_toggle_todo_completion_nonexistent(clean_db):
    """Test toggling completion of a non-existent todo."""
    result = TodoService.toggle_todo_completion(999)
    assert result is None


def test_delete_todo_existing(clean_db):
    """Test deleting an existing todo."""
    created_todo = TodoService.create_todo(TodoCreate(title="To Delete"))

    result = TodoService.delete_todo(created_todo.id)
    assert result

    # Verify it's actually deleted
    deleted_todo = TodoService.get_todo_by_id(created_todo.id)
    assert deleted_todo is None


def test_delete_todo_nonexistent(clean_db):
    """Test deleting a non-existent todo."""
    result = TodoService.delete_todo(999)
    assert not result


def test_get_stats_empty(clean_db):
    """Test getting stats with no todos."""
    stats = TodoService.get_stats()

    assert stats["total"] == 0
    assert stats["completed"] == 0
    assert stats["pending"] == 0


def test_get_stats_mixed(clean_db):
    """Test getting stats with mixed completion states."""
    # Create some todos
    todo1 = TodoService.create_todo(TodoCreate(title="Todo 1"))
    todo2 = TodoService.create_todo(TodoCreate(title="Todo 2"))
    TodoService.create_todo(TodoCreate(title="Todo 3"))

    # Complete some of them
    TodoService.toggle_todo_completion(todo1.id)
    TodoService.toggle_todo_completion(todo2.id)

    stats = TodoService.get_stats()

    assert stats["total"] == 3
    assert stats["completed"] == 2
    assert stats["pending"] == 1


def test_create_todo_with_long_title(clean_db):
    """Test creating a todo with maximum length title."""
    long_title = "A" * 200  # Max length
    todo_data = TodoCreate(title=long_title)
    result = TodoService.create_todo(todo_data)

    assert result.title == long_title


def test_create_todo_with_long_description(clean_db):
    """Test creating a todo with maximum length description."""
    long_description = "B" * 1000  # Max length
    todo_data = TodoCreate(title="Test", description=long_description)
    result = TodoService.create_todo(todo_data)

    assert result.description == long_description


def test_service_handles_none_values_gracefully(clean_db):
    """Test that service methods handle None values gracefully."""
    # Test with None ID should not crash
    result = TodoService.get_todo_by_id(0)
    assert result is None

    result = TodoService.update_todo(0, TodoUpdate(title="Test"))
    assert result is None

    result = TodoService.toggle_todo_completion(0)
    assert result is None

    result = TodoService.delete_todo(0)
    assert not result
