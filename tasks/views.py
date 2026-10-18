
# api_view lets a function-based view accept only the HTTP methods we specify.
from rest_framework.decorators import api_view, permission_classes

# IsAuthenticated ensures that only logged-in/authenticated users can access these views.
from rest_framework.permissions import IsAuthenticated

# Response creates an HTTP response and can render Python data as JSON.
from rest_framework.response import Response

# These constants represent standard HTTP response status codes.
from rest_framework.status import (
    HTTP_200_OK,          # Request succeeded.
    HTTP_201_CREATED,     # A new resource was successfully created.
    HTTP_204_NO_CONTENT,  # Request succeeded, but there is no response body.
    HTTP_400_BAD_REQUEST, # The client submitted invalid data.
    HTTP_404_NOT_FOUND,   # The requested resource was not found.
)

# PageNumberPagination divides a large collection of results into pages.
from .pagination import TaskPagination

# Task is our Django model, which represents tasks stored in the database.
from .models import Task

# TaskSerializer handles task data.
# TaskFilterSerializer validates URL query parameters such as status and priority.
from .serializers import TaskSerializer, TaskFilterSerializer


# This endpoint supports listing tasks with GET and creating tasks with POST.
@api_view(["GET", "POST"])

# The request must be authenticated before the function can execute.
@permission_classes([IsAuthenticated])
def task_list(request):

    # ============================================================
    # GET: LIST, FILTER, SEARCH, AND PAGINATE TASKS
    # ============================================================
    if request.method == "GET":

        # IMPORTANT FOR SECURITY:
        # Retrieve only tasks owned by the currently authenticated user.
        # Even if another user has tasks in the database, they won't appear here.
        #
        # QuerySet means Django's representation of a database query.
        # The query is generally evaluated when its results are needed.
        tasks = Task.objects.filter(created_by=request.user)

        # request.query_params contains values supplied in the URL after '?'.
        #
        # Example:
        # /api/tasks/?status=todo&priority=2&search=django
        #
        # These values initially arrive as strings.
        # We pass them to our serializer to validate and convert them.
        filter_serializer = TaskFilterSerializer(
            data=request.query_params
        )

        # Run all validation rules defined in TaskFilterSerializer.
        #
        # For example:
        # - An unsupported status is rejected.
        # - "high" is rejected as a priority because it isn't an integer.
        # - Priority 4 is rejected because the maximum is 3.
        #
        # raise_exception=True tells DRF to raise a validation exception
        # if the data is invalid. DRF handles it and normally returns
        # HTTP 400 Bad Request with field-specific error details.
        filter_serializer.is_valid(raise_exception=True)

        # Access the cleaned data only after validation succeeds.
        #
        # Example input:
        # {"status": "todo", "priority": "2"}
        #
        # Example validated_data:
        # {"status": "todo", "priority": 2}
        #
        # Notice that the priority string "2" has become integer 2.
        filters = filter_serializer.validated_data

        # Retrieve each validated filter.
        # dict.get() returns None when the key is absent.
        task_status = filters.get("status")
        priority = filters.get("priority")
        search = filters.get("search")

        # If the client supplied a status, return tasks with that status.
        # If no status was supplied, don't apply a status filter.
        if task_status:
            tasks = tasks.filter(status=task_status)

        # Check against None rather than using "if priority".
        # Why? Priority 0 is valid, but Python treats 0 as False.
        # This check ensures that priority=0 filters correctly.
        if priority is not None:
            tasks = tasks.filter(priority=priority)

        # Search task titles without case sensitivity.
        #
        # Example:
        # Searching for "django" can match "Learn Django REST Framework".
        # If search is missing or empty, no search filter is applied.
        if search:
            tasks = tasks.filter(title__icontains=search)

        
        # TaskPagination manages page size and page navigation.
        # The client can use ?page=2 or ?page=1&page_size=10.
        paginator = TaskPagination()

        # Apply pagination to the already-filtered queryset.
        # Only the requested page of tasks is retrieved for serialization.
        page = paginator.paginate_queryset(tasks, request)

        # Convert the current page of Task objects into JSON-compatible data.
        serializer = TaskSerializer(page, many=True)

        # Return the results along with count, next, and previous links.
        return paginator.get_paginated_response(serializer.data)


    # ============================================================
    # POST: CREATE A NEW TASK
    # ============================================================
    elif request.method == "POST":

        # request.data contains the data submitted by the client.
        # The serializer validates fields such as title, status, and priority.
        serializer = TaskSerializer(data=request.data)

        # is_valid() runs the serializer's validation rules.
        # Unlike the filter serializer above, we handle errors explicitly here.
        if serializer.is_valid():

            # Save the new task and assign its owner on the server.
            #
            # created_by isn't included in TaskSerializer's writable fields.
            # Passing it here prevents the client from choosing another owner.
            task = serializer.save(created_by=request.user)

            # Return the newly created task with HTTP 201 Created.
            return Response(
                TaskSerializer(task).data,
                status=HTTP_201_CREATED,
            )

        # If validation fails, return the serializer's field-specific errors.
        # For example, a blank title produces a title validation error.
        return Response(
            serializer.errors,
            status=HTTP_400_BAD_REQUEST,
        )


# This endpoint handles operations on one specific task.
# The <int:pk> URL parameter supplies the task's primary key.
@api_view(["GET", "PUT", "PATCH", "DELETE"])
@permission_classes([IsAuthenticated])
def task_detail(request, pk):

    # Look up the task using BOTH its primary key and its owner.
    #
    # Checking only pk=pk would not enforce ownership by itself.
    # Adding created_by=request.user means a user cannot retrieve,
    # update, or delete another user's task through this view.
    try:
        task = Task.objects.get(
            pk=pk,
            created_by=request.user,
        )

    # DoesNotExist is raised when no task matches BOTH conditions.
    # We return 404 rather than revealing whether another user's task exists.
    except Task.DoesNotExist:
        return Response(
            {"detail": "Task not found."},
            status=HTTP_404_NOT_FOUND,
        )

    # ============================================================
    # GET: RETRIEVE ONE TASK
    # ============================================================
    if request.method == "GET":

        # Serialize one task instance.
        # We don't use many=True because this is a single object.
        serializer = TaskSerializer(task)

        return Response(
            serializer.data,
            status=HTTP_200_OK,
        )

    # ============================================================
    # PUT AND PATCH: UPDATE AN EXISTING TASK
    # ============================================================
    if request.method in ["PUT", "PATCH"]:

        # request.data contains the submitted update.
        #
        # PUT generally requires all required writable fields.
        # PATCH allows the client to submit only the fields being changed.
        #
        # partial=True activates partial-update behavior for PATCH.
        serializer = TaskSerializer(
            task,
            data=request.data,
            partial=(request.method == "PATCH"),
        )

        # Validate the update before saving it.
        if serializer.is_valid():

            # Save changes to the existing task.
            # The existing created_by value remains unchanged because
            # created_by isn't a writable field in TaskSerializer.
            serializer.save()

            # Return the updated task and HTTP 200 OK.
            return Response(
                serializer.data,
                status=HTTP_200_OK,
            )

        # Return validation errors if the submitted update is invalid.
        return Response(
            serializer.errors,
            status=HTTP_400_BAD_REQUEST,
        )

    # ============================================================
    # DELETE: REMOVE AN EXISTING TASK
    # ============================================================

    # Ownership was checked before reaching this point.
    # Delete the task from the database.
    task.delete()

    # HTTP 204 means deletion succeeded and there is no response body.
    return Response(status=HTTP_204_NO_CONTENT)

