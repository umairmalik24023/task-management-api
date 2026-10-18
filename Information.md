Four Concepts should be learnt in Tests:
-------------

setUp()
------
Prepares the user and task data before each test.


self.client.get() / post()
---------
Simulates API requests.


self.assertEqual()
----------
Checks whether the actual result matches the expected result.

ne test method
---------
Checks one behavior, such as task creation or ownership protection.


*************
************


For Serializer:
-----


Step 1: Database objects
------
Your task or tasks
-----
task or tasks



Step 2: Serializer
----
TaskSerializer(task)



Step 3: Serialized data
-----
serializer.data
-------
A dictionary for one task, or a list for multiple tasks


Step 4: HTTP response
------
Response(serializer.data)
--------
DRF renders the data as JSON for the client



=======================

HTTP_200_OK
HTTP_201_CREATED
HTTP_204_NO_CONTENT
HTTP_400_BAD_REQUEST
HTTP_404_NOT_FOUND

An HTTP status code tells the client the outcome of its request.

The five status codes in your project:

200
---------

OK

The request succeeded.

Example: GET /api/tasks/19/ returns a task.



201
------

Created

A new resource was created successfully.

Example: a valid POST request creates a task.



204
------

No Content

The request succeeded, but the response has no body.

Example: a task is deleted successfully.


400
-------

Bad Request

The submitted data failed validation.

Example: the client sends a blank title.



404
--------

Not Found

The requested resource couldn't be found.

Example: the task doesn't exist or isn't accessible to the logged-in user.



*********************************************************************************************************************


Look at what you now understand
------

In your Task Management API, you can explain:

1. Models — how Django represents database records.

2. Serializers — how data is validated and converted between Python objects and API representations.

3. Views — how your application processes requests and returns responses.

4. filter() vs. get() — how to retrieve multiple records versus one specific record.

5. request.data and serializer.errors — how to handle incoming data and validation failures.

6. HTTP status codes — how your API communicates success and errors.

7. URL routing — how Django connects URLs to view functions.

8. Authentication and ownership filtering — how to restrict access to users' own tasks.

9. PUT and PATCH — how to update resources.


************************
************************

icontains
----

This performs a case-insensitive partial match on task titles. Searching for django can match titles containing Django, DJANGO, or django.

