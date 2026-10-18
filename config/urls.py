
from django.contrib import admin
from django.urls import path
from tasks.views import task_list, task_detail   # add this line

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/tasks/", task_list),   # add this
    path("api/tasks/<int:pk>/", task_detail, name="task-detail"),
]

