from django.urls import path
from . import tasks

urlpatterns = [
    path(
        "task-status/<str:task_id>/", tasks.check_task_status, name="check_task_status"
    ),
]
