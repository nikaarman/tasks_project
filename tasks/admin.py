from django.contrib import admin
from .models import Workspace, Board, Column, Task

admin.site.register(Workspace)
admin.site.register(Board)
admin.site.register(Column)
admin.site.register(Task)