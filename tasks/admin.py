# tasks/admin.py
from django.contrib import admin
from .models import Task


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ("title", "status", "priority", "due_date", "created_by", "created_at")
    list_filter = ("status", "created_by")
    search_fields = ("title", "description")

    