from django.urls import path
from . import views

urlpatterns = [
    path(
        "workspaces/",
        views.workspace_list_create,
        name="workspace_list_create",
    ),

    path("boards/", views.board_list_create, name="board_list_create"),
    path(
        "workspaces/<int:workspace_id>/boards/",
        views.workspace_boards,
        name="workspace_boards",
    ),
    path("columns/", views.column_list_create, name="column_list_create"),

    path(
        "boards/<int:board_id>/columns/",
        views.board_columns,
        name="board_columns",
    ),
    path("tasks/", views.task_list_create, name="task_list_create"),

    path(
        "columns/<int:column_id>/tasks/",
        views.column_tasks,
        name="column_tasks",
    ),
]