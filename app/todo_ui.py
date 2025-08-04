import logging
from nicegui import ui
from app.todo_service import TodoService
from app.models import TodoCreate

logger = logging.getLogger(__name__)


def create():
    """Create the todo application UI."""

    @ui.page("/")
    def todo_page():
        # Apply modern theme colors
        ui.colors(
            primary="#2563eb",
            secondary="#64748b",
            accent="#10b981",
            positive="#10b981",
            negative="#ef4444",
            warning="#f59e0b",
        )

        # Page title and header
        ui.label("Todo App").classes("text-3xl font-bold text-gray-800 mb-8 text-center")

        # Container for the entire app
        with ui.column().classes("max-w-2xl mx-auto p-6 gap-6"):
            # Add new todo form
            create_add_todo_form()

            # Stats section
            stats_container = ui.column().classes("gap-2")

            # Todo list container
            todo_list_container = ui.column().classes("gap-3")

            # Initial load
            load_stats(stats_container)
            load_todo_list(todo_list_container)


def create_add_todo_form():
    """Create the form for adding new todos."""
    with ui.card().classes("p-6 shadow-lg rounded-xl bg-white"):
        ui.label("Add New Todo").classes("text-xl font-semibold text-gray-700 mb-4")

        with ui.row().classes("gap-4 w-full items-start"):
            title_input = ui.input(placeholder="What needs to be done?").classes("flex-1").props("outlined")

            description_input = (
                ui.textarea(placeholder="Description (optional)").classes("flex-1").props("outlined rows=2")
            )

        with ui.row().classes("gap-2 justify-end mt-4"):
            ui.button("Add Todo", on_click=lambda: add_new_todo(title_input, description_input)).classes(
                "bg-primary text-white px-6 py-2 rounded-lg hover:bg-blue-600"
            )


def add_new_todo(title_input: ui.input, description_input: ui.textarea):
    """Add a new todo and refresh the display."""
    title = title_input.value.strip() if title_input.value else ""
    description = description_input.value.strip() if description_input.value else ""

    if not title:
        ui.notify("Please enter a title for your todo", type="warning")
        return

    try:
        todo_data = TodoCreate(title=title, description=description)
        TodoService.create_todo(todo_data)

        # Clear form
        title_input.set_value("")
        description_input.set_value("")

        # Refresh the page to show changes
        ui.navigate.reload()

        ui.notify("Todo added successfully!", type="positive")

    except Exception as e:
        logger.error(f"Error adding todo: {str(e)}")
        ui.notify(f"Error adding todo: {str(e)}", type="negative")


def load_stats(container: ui.column):
    """Load and display statistics."""
    try:
        stats = TodoService.get_stats()

        with container:
            with ui.row().classes("gap-4 w-full justify-center"):
                create_stat_card("Total", str(stats["total"]), "text-blue-600")
                create_stat_card("Completed", str(stats["completed"]), "text-green-600")
                create_stat_card("Pending", str(stats["pending"]), "text-orange-600")

    except Exception as e:
        logger.error(f"Error loading stats: {str(e)}")
        with container:
            ui.label(f"Error loading stats: {str(e)}").classes("text-red-500")


def create_stat_card(label: str, value: str, color_class: str):
    """Create a small statistics card."""
    with ui.card().classes("p-4 text-center bg-gray-50 rounded-lg min-w-24"):
        ui.label(value).classes(f"text-2xl font-bold {color_class}")
        ui.label(label).classes("text-sm text-gray-600 mt-1")


def load_todo_list(container: ui.column):
    """Load and display todo list."""
    try:
        todos = TodoService.get_all_todos()

        with container:
            if not todos:
                with ui.card().classes("p-8 text-center bg-gray-50 rounded-xl"):
                    ui.icon("task_alt", size="3rem").classes("text-gray-400 mb-2")
                    ui.label("No todos yet").classes("text-xl text-gray-500 mb-1")
                    ui.label("Add your first todo above to get started!").classes("text-gray-400")
            else:
                for todo in todos:
                    create_todo_item(todo)

    except Exception as e:
        logger.error(f"Error loading todos: {str(e)}")
        with container:
            ui.label(f"Error loading todos: {str(e)}").classes("text-red-500")


def create_todo_item(todo):
    """Create a single todo item card."""
    # Different styling for completed vs pending todos
    card_classes = "p-4 rounded-xl shadow-md hover:shadow-lg transition-shadow"
    if todo.completed:
        card_classes += " bg-green-50 border-l-4 border-green-400"
    else:
        card_classes += " bg-white border-l-4 border-blue-400"

    with ui.card().classes(card_classes):
        with ui.row().classes("w-full items-start justify-between gap-4"):
            # Todo content
            with ui.column().classes("flex-1 gap-2"):
                # Title with completion styling
                title_classes = "text-lg font-semibold"
                if todo.completed:
                    title_classes += " text-green-700 line-through"
                else:
                    title_classes += " text-gray-800"

                ui.label(todo.title).classes(title_classes)

                # Description if present
                if todo.description:
                    desc_classes = "text-sm"
                    if todo.completed:
                        desc_classes += " text-green-600 line-through"
                    else:
                        desc_classes += " text-gray-600"
                    ui.label(todo.description).classes(desc_classes)

                # Metadata
                ui.label(f"Created: {todo.created_at[:19].replace('T', ' ')}").classes("text-xs text-gray-400")

            # Action buttons
            with ui.column().classes("gap-2"):
                # Toggle completion button
                toggle_icon = "undo" if todo.completed else "check_circle"
                toggle_text = "Undo" if todo.completed else "Complete"
                toggle_color = "orange" if todo.completed else "positive"

                ui.button(icon=toggle_icon, on_click=lambda e, t_id=todo.id: toggle_todo_completion(t_id)).props(
                    f"color={toggle_color} round size=sm"
                ).tooltip(toggle_text)

                # Delete button
                ui.button(icon="delete", on_click=lambda e, t_id=todo.id: delete_todo(t_id)).props(
                    "color=negative round size=sm"
                ).tooltip("Delete")


def toggle_todo_completion(todo_id: int):
    """Toggle todo completion and refresh display."""
    try:
        result = TodoService.toggle_todo_completion(todo_id)
        if result:
            status = "completed" if result.completed else "reopened"
            ui.notify(f"Todo {status}!", type="positive")
            # Refresh page to show changes
            ui.navigate.reload()
        else:
            ui.notify("Todo not found", type="warning")

    except Exception as e:
        logger.error(f"Error updating todo: {str(e)}")
        ui.notify(f"Error updating todo: {str(e)}", type="negative")


def delete_todo(todo_id: int):
    """Delete todo and refresh display."""
    try:
        success = TodoService.delete_todo(todo_id)
        if success:
            ui.notify("Todo deleted!", type="warning")
            # Refresh page to show changes
            ui.navigate.reload()
        else:
            ui.notify("Todo not found", type="warning")

    except Exception as e:
        logger.error(f"Error deleting todo: {str(e)}")
        ui.notify(f"Error deleting todo: {str(e)}", type="negative")
