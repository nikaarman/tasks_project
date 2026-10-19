import json
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Workspace, Board, Column, Task


def _error(message, status=400):
    """Return a consistent JSON error response."""
    return JsonResponse({"error": message}, status=status)


def _method_not_allowed():
    return _error("Method not allowed", status=405)


def _parse_json_object(request):
    """Parse the request body and require a JSON object (not [], a string, etc.)."""
    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, UnicodeDecodeError, TypeError):
        return None, _error("Invalid JSON", status=400)

    if not isinstance(data, dict):
        return None, _error("Request body must be a JSON object", status=400)

    return data, None


def _get_or_404(model, object_id, label):
    """Return (object, None) if found, otherwise (None, JSON 404 response)."""
    try:
        return model.objects.get(id=object_id), None
    except model.DoesNotExist:
        return None, _error(f"{label} not found", status=404)


def _is_int(value):
    """bool is a subclass of int in Python, but isn't a valid ID/position here."""
    return isinstance(value, int) and not isinstance(value, bool)


def _workspace_data(workspace):
    return {
        "id": workspace.id,
        "name": workspace.name,
        "description": workspace.description,
        "owner_id": workspace.owner_id,
        "created_at": workspace.created_at.isoformat(),
        "updated_at": workspace.updated_at.isoformat(),
    }


def _board_data(board):
    return {
        "id": board.id,
        "name": board.name,
        "description": board.description,
        "workspace_id": board.workspace_id,
        "created_at": board.created_at.isoformat(),
        "updated_at": board.updated_at.isoformat(),
    }


def _column_data(column):
    return {
        "id": column.id,
        "name": column.name,
        "board_id": column.board_id,
        "position": column.position,
        "created_at": column.created_at.isoformat(),
    }


def _task_data(task):
    return {
        "id": task.id,
        "title": task.title,
        "description": task.description,
        "column_id": task.column_id,
        "priority": task.priority,
        "is_completed": task.is_completed,
        "created_at": task.created_at.isoformat(),
        "updated_at": task.updated_at.isoformat(),
    }


@csrf_exempt
def workspace_list_create(request):
    if request.method == "GET":
        workspaces = Workspace.objects.all()
        return JsonResponse(
            [_workspace_data(workspace) for workspace in workspaces],
            safe=False,
            status=200,
        )

    if request.method != "POST":
        return _method_not_allowed()

    body, error_response = _parse_json_object(request)
    if error_response:
        return error_response

    name = body.get("name")
    description = body.get("description", "")
    owner_id = body.get("owner_id")

    if not isinstance(name, str) or not name.strip():
        return _error("Name is required")

    if not isinstance(description, str):
        return _error("Description must be a string")

    if not _is_int(owner_id):
        return _error("Valid owner_id is required")

    owner, error_response = _get_or_404(User, owner_id, "Owner")
    if error_response:
        return error_response

    workspace = Workspace.objects.create(
        name=name.strip(),
        description=description,
        owner=owner,
    )
    return JsonResponse(_workspace_data(workspace), status=201)


@csrf_exempt
def workspace_boards(request, workspace_id):
    if request.method != "GET":
        return _method_not_allowed()

    workspace, error_response = _get_or_404(Workspace, workspace_id, "Workspace")
    if error_response:
        return error_response

    boards = workspace.boards.all()
    return JsonResponse(
        [_board_data(board) for board in boards],
        safe=False,
        status=200,
    )



@csrf_exempt
def board_list_create(request):
    if request.method == "GET":
        boards = Board.objects.select_related("workspace").all()
        return JsonResponse(
            [_board_data(board) for board in boards],
            safe=False,
            status=200,
        )

    if request.method != "POST":
        return _method_not_allowed()

    body, error_response = _parse_json_object(request)
    if error_response:
        return error_response

    name = body.get("name")
    description = body.get("description", "")
    workspace_id = body.get("workspace_id")

    if not isinstance(name, str) or not name.strip():
        return _error("Name is required")

    if not isinstance(description, str):
        return _error("Description must be a string")

    if not _is_int(workspace_id):
        return _error("Valid workspace_id is required")

    workspace, error_response = _get_or_404(
        Workspace, workspace_id, "Workspace"
    )
    if error_response:
        return error_response

    board = Board.objects.create(
        name=name.strip(),
        description=description,
        workspace=workspace,
    )
    return JsonResponse(_board_data(board), status=201)



@csrf_exempt
def column_list_create(request):
    if request.method == "GET":
        columns = Column.objects.select_related("board").order_by("position")
        return JsonResponse(
            [_column_data(column) for column in columns],
            safe=False,
            status=200,
        )

    if request.method != "POST":
        return _method_not_allowed()

    body, error_response = _parse_json_object(request)
    if error_response:
        return error_response

    name = body.get("name")
    board_id = body.get("board_id")
    position = body.get("position")

    if not isinstance(name, str) or not name.strip():
        return _error("Name is required")

    if not _is_int(board_id):
        return _error("Valid board_id is required")

    if not _is_int(position) or position < 0:
        return _error("Position must be a non-negative integer")

    board, error_response = _get_or_404(Board, board_id, "Board")
    if error_response:
        return error_response

    column = Column.objects.create(
        name=name.strip(),
        board=board,
        position=position,
    )
    return JsonResponse(_column_data(column), status=201)


@csrf_exempt
def board_columns(request, board_id):
    if request.method != "GET":
        return _method_not_allowed()

    board, error_response = _get_or_404(Board, board_id, "Board")
    if error_response:
        return error_response

    columns = board.columns.all().order_by("position")
    return JsonResponse(
        [_column_data(column) for column in columns],
        safe=False,
        status=200,
    )



@csrf_exempt
def task_list_create(request):
    if request.method == "GET":
        tasks = Task.objects.select_related("column").all()
        priority = request.GET.get("priority")
        completed = request.GET.get("completed")

        if priority is not None:
            if priority not in Task.Priority.values:
                return _error("Invalid priority")
            tasks = tasks.filter(priority=priority)

        if completed is not None:
            if completed not in ("true", "false"):
                return _error("completed must be true or false")
            tasks = tasks.filter(is_completed=(completed == "true"))

        return JsonResponse(
            [_task_data(task) for task in tasks],
            safe=False,
            status=200,
        )

    if request.method != "POST":
        return _method_not_allowed()

    body, error_response = _parse_json_object(request)
    if error_response:
        return error_response

    title = body.get("title")
    description = body.get("description", "")
    column_id = body.get("column_id")
    priority = body.get("priority", "medium")

    if not isinstance(title, str) or not title.strip():
        return _error("Title is required")

    if not isinstance(description, str):
        return _error("Description must be a string")

    if not isinstance(priority, str) or priority not in Task.Priority.values:
        return _error("Invalid priority")

    if not _is_int(column_id):
        return _error("Valid column_id is required")

    column, error_response = _get_or_404(Column, column_id, "Column")
    if error_response:
        return error_response

    task = Task.objects.create(
        title=title.strip(),
        description=description,
        column=column,
        priority=priority,
    )
    return JsonResponse(_task_data(task), status=201)


@csrf_exempt
def column_tasks(request, column_id):
    if request.method != "GET":
        return _method_not_allowed()

    column, error_response = _get_or_404(Column, column_id, "Column")
    if error_response:
        return error_response

    tasks = column.tasks.all()
    return JsonResponse(
        [_task_data(task) for task in tasks],
        safe=False,
        status=200,
    )