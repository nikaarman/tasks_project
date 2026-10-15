import json

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Workspace, Board, Column, Task
from django.contrib.auth.models import User


@csrf_exempt
def workspace_list_create(request):
    if request.method == "GET":
        workspaces = Workspace.objects.all()

        data = [
            {
                "id": workspace.id,
                "name": workspace.name,
                "description": workspace.description,
                "owner_id": workspace.owner_id,
                "created_at": workspace.created_at.isoformat(),
                "updated_at": workspace.updated_at.isoformat(),
            }
            for workspace in workspaces
        ]

        return JsonResponse(data, safe=False, status=200)

    elif request.method == "POST":
        try:
            body = json.loads(request.body)
        except (json.JSONDecodeError, UnicodeDecodeError):
            return JsonResponse(
                {"error": "Invalid JSON"},
                status=400
            )

        name = body.get("name")
        description = body.get("description", "")
        owner_id = body.get("owner_id")

        if not isinstance(name, str) or not name.strip():
            return JsonResponse(
                {"error": "Name is required"},
                status=400
            )

        if not isinstance(description, str):
            return JsonResponse(
                {"error": "Description must be a string"},
                status=400
            )

        if isinstance(owner_id, bool) or not isinstance(owner_id, int):
            return JsonResponse(
                {"error": "Valid owner_id is required"},
                status=400
            )

        try:
            owner = User.objects.get(id=owner_id)
        except User.DoesNotExist:
            return JsonResponse(
                {"error": "Owner not found"},
                status=404
            )

        workspace = Workspace.objects.create(
            name=name.strip(),
            description=description,
            owner=owner,
        )

        return JsonResponse(
            {
                "id": workspace.id,
                "name": workspace.name,
                "description": workspace.description,
                "owner_id": workspace.owner_id,
                "created_at": workspace.created_at.isoformat(),
                "updated_at": workspace.updated_at.isoformat(),
            },
            status=201
        )

    return JsonResponse(
        {"error": "Method not allowed"},
        status=405
    )


@csrf_exempt
def board_list_create(request):
    if request.method == "GET":
        boards = Board.objects.select_related("workspace").all()

        data = [
            {
                "id": board.id,
                "name": board.name,
                "description": board.description,
                "workspace_id": board.workspace_id,
                "created_at": board.created_at.isoformat(),
                "updated_at": board.updated_at.isoformat(),
            }
            for board in boards
        ]

        return JsonResponse(data, safe=False, status=200)

    if request.method == "POST":
        try:
            body = json.loads(request.body)
        except (json.JSONDecodeError, UnicodeDecodeError):
            return JsonResponse({"error": "Invalid JSON"}, status=400)

        name = body.get("name")
        description = body.get("description", "")
        workspace_id = body.get("workspace_id")

        if not isinstance(name, str) or not name.strip():
            return JsonResponse({"error": "Name is required"}, status=400)

        if not isinstance(description, str):
            return JsonResponse(
                {"error": "Description must be a string"}, status=400
            )

        if isinstance(workspace_id, bool) or not isinstance(workspace_id, int):
            return JsonResponse(
                {"error": "Valid workspace_id is required"}, status=400
            )

        try:
            workspace = Workspace.objects.get(id=workspace_id)
        except Workspace.DoesNotExist:
            return JsonResponse({"error": "Workspace not found"}, status=404)

        board = Board.objects.create(
            name=name.strip(),
            description=description,
            workspace=workspace,
        )

        return JsonResponse(
            {
                "id": board.id,
                "name": board.name,
                "description": board.description,
                "workspace_id": board.workspace_id,
                "created_at": board.created_at.isoformat(),
                "updated_at": board.updated_at.isoformat(),
            },
            status=201,
        )

    return JsonResponse({"error": "Method not allowed"}, status=405)

@csrf_exempt
def workspace_boards(request, workspace_id):
    if request.method != "GET":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    try:
        workspace = Workspace.objects.get(id=workspace_id)
    except Workspace.DoesNotExist:
        return JsonResponse({"error": "Workspace not found"}, status=404)

    boards = workspace.boards.all()

    data = [
        {
            "id": board.id,
            "name": board.name,
            "description": board.description,
            "workspace_id": board.workspace_id,
            "created_at": board.created_at.isoformat(),
            "updated_at": board.updated_at.isoformat(),
        }
        for board in boards
    ]

    return JsonResponse(data, safe=False, status=200)
@csrf_exempt
def column_list_create(request):
    if request.method == "GET":
        columns = Column.objects.select_related("board").order_by("position")

        data = [
            {
                "id": column.id,
                "name": column.name,
                "board_id": column.board_id,
                "position": column.position,
                "created_at": column.created_at.isoformat(),
            }
            for column in columns
        ]

        return JsonResponse(data, safe=False, status=200)

    if request.method == "POST":
        try:
            body = json.loads(request.body)
        except (json.JSONDecodeError, UnicodeDecodeError):
            return JsonResponse({"error": "Invalid JSON"}, status=400)

        name = body.get("name")
        board_id = body.get("board_id")
        position = body.get("position")

        if not isinstance(name, str) or not name.strip():
            return JsonResponse({"error": "Name is required"}, status=400)

        if isinstance(board_id, bool) or not isinstance(board_id, int):
            return JsonResponse(
                {"error": "Valid board_id is required"}, status=400
            )

        if (
            isinstance(position, bool)
            or not isinstance(position, int)
            or position < 0
        ):
            return JsonResponse(
                {"error": "Position must be a non-negative integer"},
                status=400,
            )

        try:
            board = Board.objects.get(id=board_id)
        except Board.DoesNotExist:
            return JsonResponse({"error": "Board not found"}, status=404)

        column = Column.objects.create(
            name=name.strip(),
            board=board,
            position=position,
        )

        return JsonResponse(
            {
                "id": column.id,
                "name": column.name,
                "board_id": column.board_id,
                "position": column.position,
                "created_at": column.created_at.isoformat(),
            },
            status=201,
        )

    return JsonResponse({"error": "Method not allowed"}, status=405)


@csrf_exempt
def board_columns(request, board_id):
    if request.method != "GET":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    try:
        board = Board.objects.get(id=board_id)
    except Board.DoesNotExist:
        return JsonResponse({"error": "Board not found"}, status=404)

    columns = board.columns.all().order_by("position")

    data = [
        {
            "id": column.id,
            "name": column.name,
            "board_id": column.board_id,
            "position": column.position,
            "created_at": column.created_at.isoformat(),
        }
        for column in columns
    ]

    return JsonResponse(data, safe=False, status=200)
@csrf_exempt
def task_list_create(request):
    if request.method == "GET":
        tasks = Task.objects.select_related("column").all()

        priority = request.GET.get("priority")
        completed = request.GET.get("completed")

        if priority is not None:
            valid_priorities = Task.Priority.values

            if priority not in valid_priorities:
                return JsonResponse(
                    {"error": "Invalid priority"},
                    status=400,
                )

            tasks = tasks.filter(priority=priority)

        if completed is not None:
            if completed not in ("true", "false"):
                return JsonResponse(
                    {"error": "completed must be true or false"},
                    status=400,
                )

            tasks = tasks.filter(is_completed=(completed == "true"))

        data = [
            {
                "id": task.id,
                "title": task.title,
                "description": task.description,
                "column_id": task.column_id,
                "priority": task.priority,
                "is_completed": task.is_completed,
                "created_at": task.created_at.isoformat(),
                "updated_at": task.updated_at.isoformat(),
            }
            for task in tasks
        ]

        return JsonResponse(data, safe=False, status=200)

    if request.method == "POST":
        try:
            body = json.loads(request.body)
        except (json.JSONDecodeError, UnicodeDecodeError):
            return JsonResponse(
                {"error": "Invalid JSON"},
                status=400,
            )

        title = body.get("title")
        description = body.get("description", "")
        column_id = body.get("column_id")
        priority = body.get("priority", "medium")

        if not isinstance(title, str) or not title.strip():
            return JsonResponse(
                {"error": "Title is required"},
                status=400,
            )

        if not isinstance(description, str):
            return JsonResponse(
                {"error": "Description must be a string"},
                status=400,
            )

        if priority not in Task.Priority.values:
            return JsonResponse(
                {"error": "Invalid priority"},
                status=400,
            )

        if isinstance(column_id, bool) or not isinstance(column_id, int):
            return JsonResponse(
                {"error": "Valid column_id is required"},
                status=400,
            )

        try:
            column = Column.objects.get(id=column_id)
        except Column.DoesNotExist:
            return JsonResponse(
                {"error": "Column not found"},
                status=404,
            )

        task = Task.objects.create(
            title=title.strip(),
            description=description,
            column=column,
            priority=priority,
        )

        return JsonResponse(
            {
                "id": task.id,
                "title": task.title,
                "description": task.description,
                "column_id": task.column_id,
                "priority": task.priority,
                "is_completed": task.is_completed,
                "created_at": task.created_at.isoformat(),
                "updated_at": task.updated_at.isoformat(),
            },
            status=201,
        )

    return JsonResponse(
        {"error": "Method not allowed"},
        status=405,
    )
@csrf_exempt
def column_tasks(request, column_id):
    if request.method != "GET":
        return JsonResponse(
            {"error": "Method not allowed"},
            status=405,
        )

    try:
        column = Column.objects.get(id=column_id)
    except Column.DoesNotExist:
        return JsonResponse(
            {"error": "Column not found"},
            status=404,
        )

    tasks = column.tasks.all()

    data = [
        {
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "column_id": task.column_id,
            "priority": task.priority,
            "is_completed": task.is_completed,
            "created_at": task.created_at.isoformat(),
            "updated_at": task.updated_at.isoformat(),
        }
        for task in tasks
    ]

    return JsonResponse(data, safe=False, status=200)